from ultralytics import YOLO
import cv2

class VehicleDetector:
    def __init__(self, model_path="models/yolov8n.pt"):
        self.model = YOLO(model_path)
        self.vehicle_classes = [2, 3, 5, 7]  # car, motorcycle, bus, truck
        
    def detect(self, frame):
        """Detect vehicles in frame"""
        results = self.model(frame)[0]
        detections = []
        
        for box in results.boxes:
            cls = int(box.cls[0])
            if cls not in self.vehicle_classes:
                continue
                
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            confidence = float(box.conf[0])
            
            detections.append({
                'bbox': (x1, y1, x2, y2),
                'confidence': confidence,
                'class': cls
            })
        
        return detections