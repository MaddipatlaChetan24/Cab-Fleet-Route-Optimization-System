from fastapi import APIRouter
from backend.app.schemas.request import OptimizeRequest
from backend.app.schemas.response import OptimizeResponse, AssignmentResponse, EmployeeStop

from backend.app.models.domain import Employee
from backend.app.services.assignment_service import AssignmentService
# 1. We import RoutingService (Math) instead of OptimizationService (Internet API)
from backend.app.services.routing_service import RoutingService

router = APIRouter()
assignment_service = AssignmentService()
routing_service = RoutingService() # 2. Initialize it here

@router.post("/optimize", response_model=OptimizeResponse, status_code=200)
def optimize_fleet_routes(payload: OptimizeRequest):
    employees = [
        Employee(id=emp.id, x=emp.x, y=emp.y, shift_time=emp.shift_time) 
        for emp in payload.employees
    ]
    
    cabs = assignment_service.create_cabs(n_a=payload.n_a, n_b=payload.n_b)
    assignment_service.assign_employees_to_cabs(employees=employees, cabs=cabs)

    routes = []
    total_distance = 0.0
    
    for cab in cabs:
        route = routing_service.optimize_route_for_cab(cab)
        routes.append(route)
        total_distance += route.distance

    average_distance = total_distance / len(routes) if routes else 0.0

    assignments = []
    for route in routes:
        # Get shift time from the first stop (or default)
        cab_shift = route.stops[0].shift_time if route.stops else "09:00"
        
        stops = [
            EmployeeStop(employee_id=emp.id, x=emp.x, y=emp.y, shift_time=emp.shift_time)
            for emp in route.stops
        ]
        assignments.append(
            AssignmentResponse(
                cab_id=route.cab_id,
                type=route.cab_type,
                route=stops,
                distance=route.distance,
                fuel_percentage=route.fuel_percentage,
                extra_fuel=route.extra_fuel,
                co2_saved=route.co2_saved,
                shift_time=cab_shift
            )
        )

    return OptimizeResponse(
        assignments=assignments,
        total_distance=round(total_distance, 2),
        average_distance=round(average_distance, 2)
    )

@router.get("/logistics/hotspots")
async def get_traffic_hotspots():
    """Expose simulated traffic congestion zones"""
    from backend.app.services.ml_predictor import TravelTimePredictor
    predictor = TravelTimePredictor()
    return {"hotspots": predictor.hotspots}