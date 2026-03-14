from typing import List
from pydantic import BaseModel, Field


class EmployeeInput(BaseModel):
    id: int
    x: int
    y: int
    shift_time: str = "09:00"


class OptimizeRequest(BaseModel):
    # REQUIRED (no defaults)
    n_a: int = Field(..., ge=0)   # 4-seater vehicles
    n_b: int = Field(..., ge=0)   # 8-seater vehicles
    employees: List[EmployeeInput]


# ─────────────────────────────────────────────
#  PHASE 3 — VRP SCHEMAS
# ─────────────────────────────────────────────

class VRPEmployeeInput(BaseModel):
    """Employee with real-world lat/lng coordinates."""
    id: int
    lat: float = Field(..., description="Latitude")
    lng: float = Field(..., description="Longitude")
    shift_time: str = "09:00"
    name: str = ""   # Optional display name; defaults to Emp#<id>


class VRPRequest(BaseModel):
    """Request body for Phase 3 multi-stop VRP optimization."""
    employees: List[VRPEmployeeInput]
    office_lat: float = Field(..., description="Office / destination latitude")
    office_lng: float = Field(..., description="Office / destination longitude")
    n_a: int = Field(..., ge=0, description="Number of 4-seater cabs")
    n_b: int = Field(..., ge=0, description="Number of 8-seater cabs")