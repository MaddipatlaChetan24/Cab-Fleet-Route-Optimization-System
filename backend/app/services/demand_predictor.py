import pickle
import os
import datetime
from typing import Dict

class DemandPredictor:
    def __init__(self):
        self.model_path = os.path.join(os.path.dirname(__file__), '../ml_models/demand_model.pkl')
        self.model = None
        self._load_model()
        
    def _load_model(self):
        if os.path.exists(self.model_path):
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
                
    def predict_demand(self, target_time: datetime.datetime) -> Dict[str, any]:
        if not self.model:
            return {"error": "Model not loaded"}
            
        hour = target_time.hour
        day_of_week = target_time.weekday()
        
        prediction = self.model.predict([[hour, day_of_week]])[0]
        optimal_cabs = int(prediction / 5) + 1 # Assuming 5 seats average
        
        return {
            "predicted_demand": int(prediction),
            "optimal_fleet": optimal_cabs,
            "target_time": target_time.isoformat(),
            "confidence_score": 0.85 # Mocked confidence
        }
