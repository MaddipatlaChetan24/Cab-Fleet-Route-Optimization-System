import math
import random


class TravelTimePredictor:
    """
    Simulated ML model with Real-time Traffic Prediction
    """

    def __init__(self):
        # Simulated "Traffic Hotspots"
        self.hotspots = [
            {"x": 10, "y": 10, "intensity": 2.5}, # Construction zone
            {"x": -5, "y": 15, "intensity": 1.8}, # Market area
        ]

    def get_traffic_multiplier(self, x, y):
        """Dynamic traffic scoring based on location"""
        multiplier = 1.0
        for spot in self.hotspots:
            dist = abs(x - spot["x"]) + abs(y - spot["y"])
            if dist < 5:
                multiplier += spot["intensity"] * (1 - dist/5)
        return multiplier

    def predict_minutes(self, distance_km, hour, x=0, y=0):
        base_speed = 40.0
        
        # Time of day impact
        if 8 <= hour <= 11 or 17 <= hour <= 20:
            time_penalty = 0.6
        else:
            time_penalty = 1.0

        # Location-based dynamic traffic
        traffic_penalty = self.get_traffic_multiplier(x, y)
        
        noise = random.uniform(0.95, 1.05)
        effective_speed = (base_speed * time_penalty) / traffic_penalty
        
        travel_time = (distance_km / effective_speed) * 60 * noise
        return round(travel_time, 2)