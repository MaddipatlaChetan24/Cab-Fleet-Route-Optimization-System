from fastapi import APIRouter
from backend.app.schemas.request import OptimizeRequest
from response import OptimizeResponse, AssignmentResponse, EmployeeStop
from optimization_service import OptimizationService

router = APIRouter()
optimization_service = OptimizationService()

@router.post("/optimize", response_model=OptimizeResponse, status_code=200)
def optimize_fleet_routes(payload: OptimizeRequest):
    employee_dicts = [{"x": emp.x, "y": emp.y} for emp in payload.employees]

    routes, total_distance, average_distance = optimization_service.process_optimization(
        n_a=payload.n_a,
        n_b=payload.n_b,
        employee_data=employee_dicts
    )

    assignments = []
    for route in routes:
        stops = [
            EmployeeStop(employee_id=emp.id, x=emp.x, y=emp.y)
            for emp in route.st_topics
        ]
        assignments.append(
            AssignmentResponse(
                cab_id=route.cab_id,
                type=route.cab_type,
                route=stops,
                distance=route.distance
            )
        )

    return OptimizeResponse(
        assignments=assignments,
        total_distance=total_distance,
        average_distance=average_distance
    )
