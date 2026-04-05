import cv2
import os
import numpy as np
from datetime import datetime
from app.ai.detector import VehicleDetector
from app.ai.anpr import ANPR
from app.ai.violation_engine import ViolationEngine
from app.ai.tracker import VehicleTracker
from app.core.evidence import EvidenceSaver, save_evidence
from app.core.video_reader import VideoReader

class VideoProcessor:
    def __init__(self):
        self.detector = VehicleDetector()
        self.anpr = ANPR()
        self.violation_engine = ViolationEngine()
        self.tracker = VehicleTracker()
        self.evidence_saver = EvidenceSaver()
        
    def process_video(self, video_path):
        """Process video and yield frames with detection data"""
        video = VideoReader(video_path)
        tracked_vehicles = {}
        frame_count = 0
        total_frames = video.get_total_frames()
        
        for frame in video.read_frames():
            frame_count += 1
            
            # Detect traffic light (improved)
            signal = self._detect_traffic_light(frame)
            
            # Detect vehicles
            detections = self.detector.detect(frame)
            
            # Draw line on frame
            h, w = frame.shape[:2]
            LINE_Y = int(h * 0.66)
            cv2.line(frame, (0, LINE_Y), (w, LINE_Y), (0, 0, 255), 2)
            
            # Add signal indicator with color box
            if signal == "RED":
                # Draw red box at top
                cv2.rectangle(frame, (10, 10), (200, 80), (0, 0, 255), -1)
                cv2.putText(frame, "RED SIGNAL", (20, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                cv2.putText(frame, "VIOLATION DETECTION ACTIVE", (50, 120),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            else:
                # Draw green box at top
                cv2.rectangle(frame, (10, 10), (200, 80), (0, 255, 0), -1)
                cv2.putText(frame, "GREEN SIGNAL", (20, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            # Process each detection
            for detection in detections:
                x1, y1, x2, y2 = detection['bbox']
                
                # Draw bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Check if vehicle crossed the line
                crossed_line = y2 > LINE_Y
                
                # Check for violation
                if signal == "RED" and crossed_line:
                    # Draw red bounding box for violators
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
                    cv2.putText(frame, "VIOLATION!", (x1, y1-20),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    
                    # Extract vehicle image
                    vehicle_img = frame[y1:y2, x1:x2].copy()
                    
                    # Read plate
                    plate = self.anpr.read_plate(vehicle_img)
                    
                    if plate != "Unknown":
                        # Track vehicle
                        vehicle_id = self.tracker.track(plate, detection)
                        
                        # Store best view
                        area = (x2-x1)*(y2-y1)
                        if (plate not in tracked_vehicles or 
                            area > tracked_vehicles[plate]["area"]):
                            tracked_vehicles[plate] = {
                                "img": vehicle_img,
                                "area": area,
                                "frame": frame.copy(),
                                "bbox": (x1, y1, x2, y2),
                                "plate": plate
                            }
                        
                        # Add plate text
                        cv2.putText(frame, f"Plate: {plate}", (x1, y1-35),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                elif signal == "RED" and not crossed_line:
                    # Vehicle is waiting before the line
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
                    cv2.putText(frame, "WAITING", (x1, y1-10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                else:
                    # Green signal - normal traffic
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Calculate progress
            progress = frame_count / total_frames if total_frames > 0 else 0
            
            yield frame, signal, progress, tracked_vehicles
        
        video.release()
    
    def _detect_traffic_light(self, frame):
        """Improved traffic light detection with multiple color ranges"""
        h, w = frame.shape[:2]
        
        # Expand ROI to cover more area (traffic lights are usually at the top)
        roi = frame[0:int(h*0.35), int(w*0.35):int(w*0.65)]
        
        if roi.size == 0:
            return "GREEN"
        
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        
        # Red detection - multiple ranges for different shades of red
        red_lower1 = cv2.inRange(hsv, (0, 100, 100), (10, 255, 255))
        red_lower2 = cv2.inRange(hsv, (160, 100, 100), (180, 255, 255))
        red_mask = cv2.bitwise_or(red_lower1, red_lower2)
        
        # Green detection
        green_mask = cv2.inRange(hsv, (40, 100, 100), (80, 255, 255))
        
        # Yellow/Amber detection (optional)
        yellow_mask = cv2.inRange(hsv, (15, 100, 100), (35, 255, 255))
        
        # Apply morphological operations to clean up noise
        kernel = np.ones((3, 3), np.uint8)
        red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)
        red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel)
        green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_OPEN, kernel)
        green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_CLOSE, kernel)
        
        # Count pixels
        red_pixels = cv2.countNonZero(red_mask)
        green_pixels = cv2.countNonZero(green_mask)
        yellow_pixels = cv2.countNonZero(yellow_mask)
        
        # Calculate percentages
        total_pixels = roi.shape[0] * roi.shape[1]
        red_percentage = (red_pixels / total_pixels) * 100
        green_percentage = (green_pixels / total_pixels) * 100
        yellow_percentage = (yellow_pixels / total_pixels) * 100
        
        # Print debug info (remove in production)
        # print(f"Red: {red_percentage:.2f}%, Green: {green_percentage:.2f}%")
        
        # More sensitive thresholds for red light detection
        # Even a small amount of red indicates a red light
        if red_percentage > 0.3:  # Lower threshold for red detection
            return "RED"
        elif green_percentage > 0.8:
            return "GREEN"
        elif yellow_percentage > 1.0:
            # If yellow, default to RED (as it's about to turn red)
            return "RED"
        else:
            # If unsure, check for any red in the frame
            # This helps when the ROI is slightly off
            full_frame_hsv = cv2.cvtColor(frame[:int(h*0.4), :], cv2.COLOR_BGR2HSV)
            full_red_mask = cv2.bitwise_or(
                cv2.inRange(full_frame_hsv, (0, 100, 100), (10, 255, 255)),
                cv2.inRange(full_frame_hsv, (160, 100, 100), (180, 255, 255))
            )
            full_red_pixels = cv2.countNonZero(full_red_mask)
            full_frame_total = frame[:int(h*0.4), :].shape[0] * frame[:int(h*0.4), :].shape[1]
            full_red_percentage = (full_red_pixels / full_frame_total) * 100
            
            if full_red_percentage > 0.2:
                return "RED"
            
            return "GREEN"


# Wrapper functions for backward compatibility
def process_video(video_path):
    """Wrapper function for process_video"""
    processor = VideoProcessor()
    return processor.process_video(video_path)


def finalize_violations(tracked_vehicles):
    """Finalize violations and save evidence"""
    from app.core.report import generate_report
    
    violations = []
    
    for plate, data in tracked_vehicles.items():
        # Save evidence using standalone function
        evidence_path = save_evidence(
            data["img"], 
            plate, 
            data["bbox"], 
            data["frame"]
        )
        
        violations.append({
            "plate": plate,
            "image": evidence_path,
            "desc": f"Vehicle {plate} crossed RED signal",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    # Generate report
    report_path = generate_report(violations)
    
    return violations, report_path