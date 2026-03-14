from typing import Dict, List
import random

class RiskDetectionService:
    """
    Analyzes telemetry data for risky driving behavior.
    """
    
    def analyze_risk(self, telemetry_data: Dict[str, float]) -> Dict[str, any]:
        # sudden_braking, speed_spikes, route_deviation
        braking_force = telemetry_data.get("braking_force", 0.0)
        speed_spike = telemetry_data.get("speed_spike", 0.0)
        route_deviation = telemetry_data.get("route_deviation", 0.0)
        
        # Weighted risk calculation
        risk_score = (braking_force * 0.4) + (speed_spike * 0.3) + (route_deviation * 0.3)
        risk_score = min(100.0, max(0.0, risk_score))
        
        status = "Safe"
        if risk_score > 70:
            status = "Critical Risk"
        elif risk_score > 40:
            status = "Warning"
            
        # Simulated accident probability zones
        accident_zones = []
        if risk_score > 50:
            accident_zones.append({
                "zone_id": "ZONE-404",
                "probability": "High",
                "reason": "Sudden deceleration patterns detected"
            })
            
        return {
            "risk_score": f"{round(risk_score, 1)}%",
            "status": status,
            "accident_probability_zones": accident_zones,
            "driver_recommendation": self._get_recommendation(status)
        }
        
    def _get_recommendation(self, status: str) -> str:
        if status == "Critical Risk":
            return "Immediate Intervention Required. Driver flagged for safety review."
        elif status == "Warning":
            return "Advisory status. Monitor next 15 minutes."
        return "Stable performance. No action needed."
