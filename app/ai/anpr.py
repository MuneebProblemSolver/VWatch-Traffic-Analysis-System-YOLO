import easyocr
import cv2
import numpy as np

class ANPR:
    def __init__(self):
        self.reader = easyocr.Reader(['en'])
        
    def read_plate(self, img):
        """Read license plate from image"""
        if img is None or img.size == 0:
            return "Unknown"
        
        try:
            # Enhance image
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)
            
            # Try reading
            results = self.reader.readtext(gray)
            
            if results and len(results) > 0:
                return results[0][1]
            
            # Try with thresholding
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            results = self.reader.readtext(thresh)
            
            return results[0][1] if results and len(results) > 0 else "Unknown"
        except Exception as e:
            print(f"Error reading plate: {e}")
            return "Unknown"