class VehicleTracker:
    def __init__(self):
        self.tracked_vehicles = {}
        
    def track(self, plate, detection):
        """Track vehicle by plate number"""
        if plate not in self.tracked_vehicles:
            self.tracked_vehicles[plate] = {
                'first_seen': detection,
                'count': 1,
                'best_view': detection
            }
        else:
            self.tracked_vehicles[plate]['count'] += 1
            
        return plate