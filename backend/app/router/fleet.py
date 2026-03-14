from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import uuid

router = APIRouter(prefix="/fleet", tags=["Fleet"])

# In-memory storage
fleet_db = {}


class FleetVehicle(BaseModel):
    id: str | None = None
    vehicle_number: str
    capacity: int
    fuel_efficiency: float = 15.0
    tank_capacity: float = 50.0
    status: str  # active | maintenance | idle


@router.get("/", response_model=List[FleetVehicle])
def get_all_vehicles():
    return list(fleet_db.values())


@router.post("/", response_model=FleetVehicle)
def create_vehicle(vehicle: FleetVehicle):
    vehicle.id = str(uuid.uuid4())
    fleet_db[vehicle.id] = vehicle
    return vehicle


@router.put("/{vehicle_id}", response_model=FleetVehicle)
def update_vehicle(vehicle_id: str, vehicle: FleetVehicle):
    if vehicle_id not in fleet_db:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    vehicle.id = vehicle_id
    fleet_db[vehicle_id] = vehicle
    return vehicle


@router.delete("/{vehicle_id}")
def delete_vehicle(vehicle_id: str):
    if vehicle_id not in fleet_db:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    del fleet_db[vehicle_id]
    return {"message": "Vehicle deleted"}