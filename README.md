# Cab Fleet Route Optimization System





### Using Docker

```bash
docker build -t fleet-optimization .
docker run -p 8000:8000 fleet-optimization
```

##  API Endpoints (Highlights)

- `GET /api/v1/predict/demand`: Predict future demand levels.
- `POST /api/v1/optimize`: Run route optimization for a set of vehicles and orders.
- `POST /api/v1/risk/analyze`: Analyze driver telemetry for safety risk scores.
- `GET /dashboard`: Main monitoring dashboard.

---
Developed as part of the Cab Fleet Route Optimization System project.
