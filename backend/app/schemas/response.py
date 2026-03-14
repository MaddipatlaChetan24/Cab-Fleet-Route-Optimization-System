from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class EmployeeStop(BaseModel):
    employee_id: int
    x: float
    y: float
    shift_time: str = "09:00"


class AssignmentResponse(BaseModel):
    cab_id: int
    type: str # 'A' or 'B'
    route: List[EmployeeStop]
    distance: float
    shift_time: str = "09:00"
    fuel_percentage: float = 0.0
    extra_fuel: float = 0.0
    co2_saved: float = 0.0


class OptimizeResponse(BaseModel):
    assignments: List[AssignmentResponse]
    total_distance: float
    average_distance: float


# ─────────────────────────────────────────────
#  PHASE 3 — VRP RESPONSE SCHEMAS
# ─────────────────────────────────────────────

class VRPStop(BaseModel):
    """A single stop on a cab's route."""
    label: str                   # "Emp#3" or "Office"
    lat: float
    lng: float
    employee_id: Optional[int] = None
    is_office: bool = False


class ClusterInfo(BaseModel):
    """Information about the AI-driven geographic cluster for a cab."""
    centroid_lat: float
    centroid_lng: float
    radius_km: float


class VRPAssignment(BaseModel):
    """Optimized route for one cab."""
    cab_id: int
    type: str                    # 'A' or 'B'
    route_labels: List[str]      # ["Emp#3", "Emp#1", "Office"]
    stops: List[VRPStop]         # Full stop details
    distance_km: float
    eta_minutes: float
    solver_used: str             # "ortools", "fallback_nn", "trivial", "skipped"
    cluster: Optional[ClusterInfo] = None


class VRPResponse(BaseModel):
    """Full VRP optimization result."""
    assignments: List[VRPAssignment]
    total_distance_km: float
    solver_status: str           # "ROUTING_SUCCESS", "FALLBACK", "ROUTING_FAIL"
    unassigned_employee_ids: List[int] = []
    message: str = ""