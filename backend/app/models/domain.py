from dataclasses import dataclass, field
from typing import List


# -------------------------
# EMPLOYEE
# -------------------------
@dataclass
class Employee:
    id: int
    x: float
    y: float
    shift_time: str = "09:00" # Default shift


# -------------------------
# CAB
# -------------------------
@dataclass
class Cab:
    id: int
    cab_type: str
    capacity: int
    license_plate: str = "TBD"
    fuel_efficiency: float = 15.0  # km/l
    tank_capacity: float = 50.0   # liters
    assigned_employees: List[Employee] = field(default_factory=list)


# -------------------------
# ROUTE
# -------------------------
@dataclass
class Route:
    cab_id: int
    cab_type: str
    stops: List[Employee]
    distance: float
    eta_minutes: float = 0.0
    fuel_percentage: float = 0.0
    extra_fuel: float = 0.0
    co2_saved: float = 0.0