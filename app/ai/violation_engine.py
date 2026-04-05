class ViolationEngine:
    def __init__(self):
        self.violations = {}
        
    def check_violation(self, signal, vehicle, line_y):
        """Check if vehicle committed violation"""
        if signal == "RED" and vehicle['bbox'][3] > line_y:
            return True
        return False