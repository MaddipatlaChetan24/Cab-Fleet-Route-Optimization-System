import requests
import json
import time

payload = {
    "n_a": 3,
    "n_b": 2,
    "office_lat": 13.0827,
    "office_lng": 80.2707,
    "employees": [
        {"id": 1, "lat": 13.0927, "lng": 80.2807, "shift_time": "10:00 AM"},
        {"id": 2, "lat": 13.1027, "lng": 80.2907, "shift_time": "10:00 AM"},
        {"id": 3, "lat": 13.0727, "lng": 80.2607, "shift_time": "10:00 AM"},
        {"id": 4, "lat": 13.0627, "lng": 80.2507, "shift_time": "10:00 AM"},
        {"id": 5, "lat": 13.1127, "lng": 80.2407, "shift_time": "10:00 AM"},
    ]
}

start = time.time()
print("1. Calling VRP API...")
res = requests.post("http://localhost:8000/api/v1/vrp/optimize", json=payload)
data = res.json()
print(f"   VRP returned in {time.time() - start:.2f}s")

for idx, assign in enumerate(data.get("assignments", [])):
    if not assign["stops"]: continue
    
    waypoints = [[80.2707, 13.0827]]
    for stop in assign["stops"]:
        waypoints.append([stop["lng"], stop["lat"]])
    
    coords = ";".join([f"{p[0]},{p[1]}" for p in waypoints])
    osrm_url = f"https://router.project-osrm.org/route/v1/driving/{coords}?overview=full&geometries=geojson&steps=false"
    
    osrm_start = time.time()
    try:
        osrm_res = requests.get(osrm_url, timeout=5)
        print(f"   OSRM Cab {assign['cab_id']} returned {osrm_res.status_code} in {time.time() - osrm_start:.2f}s")
    except Exception as e:
        print(f"   OSRM error on Cab {assign['cab_id']}: {e}")

print(f"Total time: {time.time() - start:.2f}s")
