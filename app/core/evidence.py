import cv2
import os
from datetime import datetime

EVIDENCE_DIR = "evidence"

class EvidenceSaver:
    """Class to handle saving evidence images"""
    
    def __init__(self, evidence_dir="evidence"):
        self.evidence_dir = evidence_dir
        os.makedirs(self.evidence_dir, exist_ok=True)
    
    def save_evidence(self, vehicle_img, plate_text, bbox, full_frame):
        """Save violation evidence image"""
        # Create evidence image
        evidence = full_frame.copy()
        x1, y1, x2, y2 = bbox
        
        # Draw bounding box
        cv2.rectangle(evidence, (x1, y1), (x2, y2), (0, 0, 255), 3)
        
        # Add text overlay
        overlay = evidence.copy()
        cv2.rectangle(overlay, (x1, y1-40), (x1+350, y1), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, evidence, 0.4, 0, evidence)
        
        # Add violation text
        cv2.putText(evidence, "RED LIGHT VIOLATION", (x1+10, y1-15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(evidence, f"Plate: {plate_text}", (x1+10, y1-35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(evidence, timestamp, (10, evidence.shape[0]-20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Save
        filename = f"violation_{plate_text}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        path = os.path.join(self.evidence_dir, filename)
        cv2.imwrite(path, evidence)
        
        return path


# Standalone function for backward compatibility
def save_evidence(vehicle_img, plate_text, bbox, full_frame):
    """Standalone function to save evidence"""
    saver = EvidenceSaver()
    return saver.save_evidence(vehicle_img, plate_text, bbox, full_frame)