import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_demand_prediction():
    print("\n--- Testing AI Demand Prediction ---")
    try:
        response = requests.get(f"{BASE_URL}/predict/demand?hours_ahead=12")
        if response.status_code == 200:
            data = response.json()
            print(f"Success! Prediction: {data['predicted_demand']} emps, Optimal Fleet: {data['optimal_fleet']}")
            assert "predicted_demand" in data
            assert "optimal_fleet" in data
        else:
            print(f"Failed: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

def test_driver_risk():
    print("\n--- Testing Driver Risk Detection ---")
    telemetry = {
        "braking_force": 8.5,
        "speed_spike": 12.0,
        "route_deviation": 5.0
    }
    try:
        response = requests.post(f"{BASE_URL}/risk/analyze", json=telemetry)
        if response.status_code == 200:
            data = response.json()
            print(f"Success! Risk Score: {data['risk_score']}, Status: {data['status']}")
            assert "risk_score" in data
            assert "status" in data
        else:
            print(f"Failed: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Wait a bit for server to reload if reload is active
    time.sleep(2)
    test_demand_prediction()
    test_driver_risk()
