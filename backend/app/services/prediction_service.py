import math
from collections import defaultdict

class PredictionService:

    def predict_zones(self, employees, grid_size=10):
        zones = defaultdict(int)

        for e in employees:
            gx = int(e.x // grid_size)
            gy = int(e.y // grid_size)
            zones[(gx, gy)] += 1

        ranked = sorted(zones.items(), key=lambda z: z[1], reverse=True)

        return [
            {"zone": k, "demand": v}
            for k, v in ranked
        ]