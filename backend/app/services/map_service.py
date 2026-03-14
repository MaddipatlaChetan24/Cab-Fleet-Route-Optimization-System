import requests


class MapService:

    OSRM_URL = "http://router.project-osrm.org/route/v1/driving"

    def road_distance(self, x1, y1, x2, y2):
        try:
            url = f"{self.OSRM_URL}/{x1},{y1};{x2},{y2}?overview=false"
            r = requests.get(url, timeout=5).json()
            return r["routes"][0]["distance"] / 1000
        except Exception:
            # fallback to euclidean if API fails
            return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5