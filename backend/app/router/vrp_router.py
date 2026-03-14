"""
vrp_router.py — Phase 3 Multi-Stop VRP API Endpoint
=====================================================
POST /api/v1/vrp/optimize

Full pipeline:
    Request → Clustering → OR-Tools VRP → Ordered routes per cab → Response
"""

from fastapi import APIRouter, HTTPException, status
import logging

from backend.app.schemas.request import VRPRequest
from backend.app.schemas.response import VRPResponse, VRPAssignment, VRPStop, ClusterInfo
from backend.app.services.vrp_service import VRPService, VRPEmployee, format_route_output
from backend.app.services.clustering_service import ClusteringService, format_cluster_summary

logger = logging.getLogger(__name__)

router = APIRouter()

# Service singletons
clustering_service = ClusteringService()


@router.post(
    "/vrp/optimize",
    response_model=VRPResponse,
    status_code=200,
    summary="Multi-Stop VRP Route Optimization",
    description="""
**Phase 3 — Vehicle Routing Problem (VRP)**

Full pipeline:

1. **Cluster** employees into geographic groups (K-Means++)
2. **Assign** clusters to cabs (capacity-aware)
3. **Solve** optimal pickup order per cab (Google OR-Tools CVRP)

Output format per cab:
```
Cab 101 → Emp#3 → Emp#1 → Emp#5 → Office
```

Falls back to greedy nearest-neighbor if OR-Tools solver times out.
    """
)
def vrp_optimize(payload: VRPRequest):
    """
    Solve multi-stop routing for all cabs.

    - Accepts real lat/lng coordinates for employees and the office.
    - Returns optimized pickup route per cab ending at the office.
    """
    # ── Validation ──────────────────────────────
    if payload.n_a + payload.n_b == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one cab is required (n_a + n_b > 0)."
        )

    if not payload.employees:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee list cannot be empty."
        )

    total_capacity = payload.n_a * 4 + payload.n_b * 8
    if len(payload.employees) > total_capacity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Insufficient capacity: {len(payload.employees)} employees "
                f"but only {total_capacity} seats "
                f"({payload.n_a} × 4 + {payload.n_b} × 8)."
            )
        )

    # ── Build domain objects ─────────────────────
    employees = [
        VRPEmployee(
            id=emp.id,
            lat=emp.lat,
            lng=emp.lng,
            shift_time=emp.shift_time,
            name=emp.name or f"Emp#{emp.id}"
        )
        for emp in payload.employees
    ]

    # ── Step 1: Cluster ──────────────────────────
    logger.info(
        "VRP: clustering %d employees into %d cabs (A:%d × 4, B:%d × 8)",
        len(employees), payload.n_a + payload.n_b, payload.n_a, payload.n_b
    )
    cabs = clustering_service.assign(
        employees=employees,
        n_a=payload.n_a,
        n_b=payload.n_b,
        office_lat=payload.office_lat,
        office_lng=payload.office_lng
    )
    logger.info(format_cluster_summary(cabs))

    # ── Step 2: VRP Solve ────────────────────────
    vrp_service = VRPService(
        office_lat=payload.office_lat,
        office_lng=payload.office_lng
    )
    solution = vrp_service.solve(cabs)
    logger.info(format_route_output(solution))

    # ── Step 3: Build Response ───────────────────
    assignments = []
    for route in solution.assignments:
        vrp_stops = [
            VRPStop(
                label=s.label,
                lat=s.lat,
                lng=s.lng,
                employee_id=s.employee_id,
                is_office=s.is_office
            )
            for s in route.stops
        ]
        cluster_info = None
        if route.cluster_centroid_lat is not None and route.cluster_centroid_lng is not None:
            cluster_info = ClusterInfo(
                centroid_lat=route.cluster_centroid_lat,
                centroid_lng=route.cluster_centroid_lng,
                radius_km=route.cluster_radius_km or 0.5
            )

        assignments.append(
            VRPAssignment(
                cab_id=route.cab_id,
                type=route.cab_type,
                route_labels=[s.label for s in route.stops],
                stops=vrp_stops,
                distance_km=route.distance_km,
                eta_minutes=route.eta_minutes,
                solver_used=route.solver_used,
                cluster=cluster_info
            )
        )

    status_msg = {
        "ROUTING_SUCCESS": "All routes optimized successfully via OR-Tools.",
        "FALLBACK": "Some routes used nearest-neighbor fallback (OR-Tools timed out).",
        "ROUTING_FAIL": "Routing failed for some cabs."
    }.get(solution.solver_status, solution.solver_status)

    return VRPResponse(
        assignments=assignments,
        total_distance_km=solution.total_distance_km,
        solver_status=solution.solver_status,
        unassigned_employee_ids=solution.unassigned_employee_ids,
        message=status_msg
    )


@router.get(
    "/vrp/health",
    summary="VRP Service Health Check",
    tags=["VRP"]
)
def vrp_health():
    """Check that the VRP service and OR-Tools are available."""
    try:
        from ortools.constraint_solver import pywrapcp
        return {
            "status": "ok",
            "or_tools": "available",
            "endpoint": "POST /api/v1/vrp/optimize"
        }
    except ImportError:
        return {
            "status": "degraded",
            "or_tools": "not installed — install ortools>=9.6",
            "fallback": "nearest-neighbor will be used"
        }
