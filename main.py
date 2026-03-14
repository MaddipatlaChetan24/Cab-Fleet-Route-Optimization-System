from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import os

from backend.app.core.config import settings
from backend.app.core.exceptions import (
    FleetBaseException,
    InsufficientCapacityError
)
from backend.app.router.optimize import router as optimize_router
from backend.app.router.fleet import router as fleet
from backend.app.router.vrp_router import router as vrp_router
from backend.app.services.demand_predictor import DemandPredictor
from backend.app.services.risk_service import RiskDetectionService
import datetime


# -------------------------------------------------
# LOGGING CONFIG
# -------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# -------------------------------------------------
# FASTAPI APP INIT
# -------------------------------------------------
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise API for Cab Fleet Route Optimization",
    docs_url="/docs",
    redoc_url="/redoc"
)


# -------------------------------------------------
# CORS CONFIG (Restrict in Production)
# -------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------
# ROUTERS
# -------------------------------------------------
app.include_router(fleet)

app.include_router(
    optimize_router,
    prefix="/api/v1",
    tags=["Optimization"]
)

app.include_router(
    vrp_router,
    prefix="/api/v1",
    tags=["VRP"]
)


# -------------------------------------------------
# AI ENGINE ENDPOINTS
# -------------------------------------------------
demand_predictor = DemandPredictor()
risk_service = RiskDetectionService()

@app.get("/api/v1/predict/demand")
def predict_demand(hours_ahead: int = 24):
    target_time = datetime.datetime.now() + datetime.timedelta(hours=hours_ahead)
    return demand_predictor.predict_demand(target_time)

@app.post("/api/v1/risk/analyze")
async def analyze_driver_risk(telemetry: dict):
    return risk_service.analyze_risk(telemetry)


# -------------------------------------------------
# ROOT ENDPOINT
# -------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def root():
    # Serve Telemetry page as root
    html_path = os.path.join(os.path.dirname(__file__), "frontend", "index.html")
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>UI not found</h1><p>Ensure index.html is in the frontend folder.</p>"

@app.get("/dashboard", response_class=HTMLResponse)
def get_dashboard():
    html_path = os.path.join(os.path.dirname(__file__), "frontend", "dashboard.html")
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Dashboard UI not found</h1>"

@app.get("/fleetmgt", response_class=HTMLResponse)
def get_fleetmgt():
    html_path = os.path.join(os.path.dirname(__file__), "frontend", "fleetmgt.html")
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Fleet Management UI not found</h1>"


# -------------------------------------------------
# EXCEPTION HANDLERS
# -------------------------------------------------

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error_code": "VALIDATION_FAILED",
            "message": "Input validation failed",
            "details": exc.errors()
        }
    )


@app.exception_handler(InsufficientCapacityError)
async def capacity_exception_handler(request: Request, exc: InsufficientCapacityError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error_code": "INSUFFICIENT_CAPACITY",
            "message": exc.message,
            "details": exc.details or {}
        }
    )


@app.exception_handler(FleetBaseException)
async def fleet_exception_handler(request: Request, exc: FleetBaseException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error_code": "BAD_REQUEST",
            "message": exc.message,
            "details": exc.details or {}
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception occurred")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred processing the request.",
            "details": {}
        }
    )