import requests
import json
import time
import random

payload = {
    "n_a": 5,
    "n_b": 5,
    "office_lat": 13.0827,
    "office_lng": 80.2707,
    "employees": [
        {"id": i, "lat": 13.0827 + (random.random() - 0.5)*0.1, "lng": 80.2707 + (random.random() - 0.5)*0.1, "shift_time": "10:00 AM"}
        for i in range(1, 16)
    ]
}

start = time.time()
try:
    res = requests.post("http://localhost:8000/api/v1/vrp/optimize", json=payload)
    end = time.time()
    print("Status:", res.status_code)
    print(f"Time Taken: {end - start:.2f} seconds")

