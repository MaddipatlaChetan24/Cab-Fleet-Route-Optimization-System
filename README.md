# Cab Fleet Route Optimization System




##  Project Structure

```text
.
├── backend/app/
│   ├── core/           # Configuration and global exceptions
│   ├── models/         # Database models
│   ├── schemas/        # Pydantic validation schemas
│   ├── router/         # API Route handlers (Fleet, Optimization, VRP)
│   └── services/       # Core business logic (ML Predictors, VRP Solvers)
├── frontend/           # UI components (Index, Dashboard, Fleet Management)
├── main.py             # FastAPI entry point
├── Dockerfile          # Containerization config
├── requirements.txt    # Python dependencies
└── vercel.json         # Vercel deployment config
```

##  Installation & Setup

### Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/MaddipatlaChetan24/Cab-Fleet-Route-Optimization-System.git
   cd Cab-Fleet-Route-Optimization-System
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the server**:
   ```bash
   uvicorn main:app --reload
   ```
   Access the API docs at `http://localhost:8000/docs`.

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
