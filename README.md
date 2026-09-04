# Cab Fleet Route Optimization System


An enterprise-grade AI-powered SaaS solution for optimizing cab fleet operations. This system leverages advanced algorithms and machine learning to solve Vehicle Routing Problems (VRP), predict demand, and enhance driver safety.

## Key Features

- **Advanced Route Optimization**: Utilizing Google OR-Tools to solve complex VRP with capacity constraints and time windows.
- **AI Demand Prediction**: ML-based prediction of future cab demand based on historical data and temporal patterns.
- **Risk Detection Service**: Real-time analysis of driver telemetry to identify high-risk behaviors and improve safety.
- **Clustering & Service Management**: Intelligent vehicle-to-region assignment using clustering algorithms.
- **Interactive Dashboards**: Real-time visualization of fleet status, telemetry, and optimization results.
- **Scalable Backend**: Built with FastAPI for high-performance asynchronous API handling.

##  Tech Stack

- **Backend**: Python 3.11+, FastAPI, Pydantic v2
- **Optimization Engine**: Google OR-Tools
- **Machine Learning**: Scikit-learn, NumPy, Pandas, SciPy
- **Frontend**: HTML5, Vanilla CSS, JavaScript (Dashboard & Fleet Management)
- **Deployment**: Docker, Railway

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
