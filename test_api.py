import requests
import json

payload = {
    "n_a": 3,
    "n_b": 2,
    "office_lat": 13.0827,
    "office_lng": 80.2707,
    "employees": [
        {"id": 1, "lat": 13.0927, "lng": 80.2807, "shift_time": "10:00 AM"}
    ]
}

try:
    res = requests.post("http://localhost:8000/api/v1/vrp/optimize", json=payload)
    print("Status:", res.status_code)
    try:
        print("Response:", json.dumps(res.json(), indent=2))
    except:
        print("Response text:", res.text)
except Exception as e:
    print("Error:", e)
