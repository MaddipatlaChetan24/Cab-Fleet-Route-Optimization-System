import math
import joblib
import os
from typing import Tuple


class ETAPredictor:
    """
    ML-based ETA predictor.
    Falls back to physics formula if model not trained yet.
    """

    def __init__(self, model_path: str = "backend/app/ml_models/eta_model.pkl"):
        self.model_path = model_path
        self.model = None

        if os.path.exists(model_path):
            self.model = joblib.load(model_path)

    # --------------------------------------------------
    # BASIC DISTANCE
    # --------------------------------------------------
    def _euclidean(self, a: Tuple[float, float], b: Tuple[float, float]) -> float:
        return math.hypot(a[0] - b[0], a[1] - b[1])

    # --------------------------------------------------
    # ETA PREDICTION
    # --------------------------------------------------
    def predict_eta(self, start, end, traffic_factor: float = 1.0) -> float:
        """
        Returns ETA in minutes
        """

        dist = self._euclidean(start, end)

        # -------- ML MODEL AVAILABLE --------
        if self.model:
            return float(
                self.model.predict([[dist, traffic_factor]])[0]
            )

        # -------- FALLBACK FORMULA --------
        avg_speed_kmph = 28 / traffic_factor
        time_hours = dist / avg_speed_kmph
        return round(time_hours * 60, 2)