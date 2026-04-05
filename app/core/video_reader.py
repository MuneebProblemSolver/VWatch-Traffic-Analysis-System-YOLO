import cv2

class VideoReader:
    def __init__(self, video_path):
        self.cap = cv2.VideoCapture(video_path)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        
    def read_frames(self):
        """Generator to read frames"""
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            yield frame
            
    def get_total_frames(self):
        return self.total_frames if self.total_frames > 0 else 300
        
    def release(self):
        self.cap.release()