"""
vrp_service.py — Phase 3 Multi-Stop VRP Routing
================================================
Uses Google OR-Tools (CVRP) to find optimal pickup orders.

Flow:
    Cab depot → Employee_A → Employee_B → Employee_C → Office

Key Design:
- Distance matrix built using Haversine (real-world km)
- Node 0  = Cab depot (start/end for OR-Tools, but we end at office in practice)
- Node 1  = Office (destination)
- Node 2+ = Employees
- Capacity constraint per vehicle
- GLS metaheuristic, 10 s time limit
- Fallback: nearest-neighbor if OR-Tools fails
"""

import math
import logging
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
#  DATA STRUCTURES
# ─────────────────────────────────────────────

@dataclass
class VRPEmployee:
    id: int
    lat: float
    lng: float
    shift_time: str = "09:00"
    name: str = ""

    def __post_init__(self):
        if not self.name:
            self.name = f"Emp#{self.id}"


@dataclass
class VRPCab:
    id: int
    cab_type: str          # 'A' (4-seat) or 'B' (8-seat)
    capacity: int
    assigned_employees: List[VRPEmployee] = field(default_factory=list)
    cluster_centroid_lat: Optional[float] = None
    cluster_centroid_lng: Optional[float] = None
    cluster_radius_km: Optional[float] = None


@dataclass
class VRPStop:
    label: str             # "Emp#3" or "Office"
    lat: float
    lng: float
    employee_id: Optional[int] = None   # None for office
    is_office: bool = False


@dataclass
class VRPCabRoute:
    cab_id: int
    cab_type: str
    stops: List[VRPStop]           # Ordered: pickups → Office
    distance_km: float
    eta_minutes: float
    solver_used: str               # "ortools" | "fallback_nn"
    cluster_centroid_lat: Optional[float] = None
    cluster_centroid_lng: Optional[float] = None
    cluster_radius_km: Optional[float] = None


@dataclass
class VRPSolution:
    assignments: List[VRPCabRoute]
    total_distance_km: float
    solver_status: str             # "ROUTING_SUCCESS" | "ROUTING_FAIL" | "FALLBACK"
    unassigned_employee_ids: List[int] = field(default_factory=list)


# ─────────────────────────────────────────────
#  MANHATTAN DISTANCE
# ─────────────────────────────────────────────

def manhattan_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Manhattan distance formula corrected for city grid.
    D = |x1 - x2| + |y1 - y2| converted to km.
    """
    lat_km = abs(lat1 - lat2) * 111
    lng_km = abs(lng1 - lng2) * 111 * math.cos(math.radians((lat1 + lat2) / 2))
    return lat_km + lng_km


# ─────────────────────────────────────────────
#  VRP SERVICE
# ─────────────────────────────────────────────

class VRPService:
    """
    Capacitated Vehicle Routing Problem solver using Google OR-Tools.

    Node indices in the distance matrix:
        0          → virtual depot (same coords as office for simplicity)
        1          → office (actual destination)
        2 … N+1    → employees
    """

    SPEED_KMH = 30.0          # Average urban cab speed
    TIME_LIMIT_SECONDS = 2    # OR-Tools solver timeout

    def __init__(self, office_lat: float, office_lng: float):
        self.office_lat = office_lat
        self.office_lng = office_lng

    # ──────────────────────────────────────────
    #  PUBLIC: SOLVE
    # ──────────────────────────────────────────

    def solve(self, cabs: List[VRPCab]) -> VRPSolution:
        """
        Solve multi-stop routing for all cabs.
        Each cab has pre-assigned employees (done by ClusteringService).
        Returns ordered stop sequences: pickups → Office.
        """
        assignments: List[VRPCabRoute] = []
        total_dist = 0.0
        any_fallback = False
        unassigned: List[int] = []

        for cab in cabs:
            if not cab.assigned_employees:
                assignments.append(VRPCabRoute(
                    cab_id=cab.id,
                    cab_type=cab.cab_type,
                    stops=[],
                    distance_km=0.0,
                    eta_minutes=0.0,
                    solver_used="skipped",
                    cluster_centroid_lat=cab.cluster_centroid_lat,
                    cluster_centroid_lng=cab.cluster_centroid_lng,
                    cluster_radius_km=cab.cluster_radius_km
                ))
                continue

            route, used_solver = self._solve_single_cab(cab)
            if route is None:
                # Complete failure — mark employees unassigned
                unassigned.extend(e.id for e in cab.assigned_employees)
                any_fallback = True
                continue

            if used_solver == "fallback_nn":
                any_fallback = True

            dist = self._route_distance(route)
            eta  = (dist / self.SPEED_KMH) * 60  # minutes

            assignments.append(VRPCabRoute(
                cab_id=cab.id,
                cab_type=cab.cab_type,
                stops=route,
                distance_km=round(dist, 2),
                eta_minutes=round(eta, 1),
                solver_used=used_solver,
                cluster_centroid_lat=cab.cluster_centroid_lat,
                cluster_centroid_lng=cab.cluster_centroid_lng,
                cluster_radius_km=cab.cluster_radius_km
            ))
            total_dist += dist

        status = ("FALLBACK" if any_fallback
                  else "ROUTING_SUCCESS" if assignments
                  else "ROUTING_FAIL")

        return VRPSolution(
            assignments=assignments,
            total_distance_km=round(total_dist, 2),
            solver_status=status,
            unassigned_employee_ids=unassigned
        )

    # ──────────────────────────────────────────
    #  SINGLE CAB SOLVER
    # ──────────────────────────────────────────

    def _solve_single_cab(
        self, cab: VRPCab
    ) -> Tuple[Optional[List[VRPStop]], str]:
        """
        Returns (ordered stops list, solver_type) or (None, "error").
        Ordered stops = [pickup1, pickup2, …, Office].
        """
        employees = cab.assigned_employees

        # For 1 employee, trivial solution
        if len(employees) == 1:
            emp = employees[0]
            stops = [
                VRPStop(label=emp.name, lat=emp.lat, lng=emp.lng,
                        employee_id=emp.id),
                VRPStop(label="Office", lat=self.office_lat,
                        lng=self.office_lng, is_office=True)
            ]
            return stops, "trivial"

        # Try OR-Tools first
        try:
            return self._ortools_solve(employees), "ortools"
        except Exception as exc:
            logger.warning("OR-Tools failed for cab %d: %s — using fallback NN", cab.id, exc)

        # Fallback: Nearest-Neighbor
        try:
            return self._nn_solve(employees), "fallback_nn"
        except Exception as exc2:
            logger.error("Fallback NN also failed for cab %d: %s", cab.id, exc2)
            return None, "error"

    # ──────────────────────────────────────────
    #  OR-TOOLS SOLVER
    # ──────────────────────────────────────────

    def _ortools_solve(self, employees: List[VRPEmployee]) -> List[VRPStop]:
        """
        Solve TSP (single cab) using OR-Tools.
        Nodes: [depot(0=office), employee_1, employee_2, ..., office_final]
        We treat it as: start at office-depot, visit all employees, end at office.
        """
        from ortools.constraint_solver import routing_enums_pb2
        from ortools.constraint_solver import pywrapcp

        n_employees = len(employees)
        # Nodes: 0 = depot/office, 1..n = employees
        n_nodes = n_employees + 1

        # Build integer distance matrix (OR-Tools needs integers)
        # Scale by 1000 for precision
        dist_matrix = self._build_distance_matrix(employees)

        # Manager: 1 vehicle, depot at node 0
        manager = pywrapcp.RoutingIndexManager(n_nodes, 1, 0)
        routing = pywrapcp.RoutingModel(manager)

        def distance_callback(from_idx, to_idx):
            i = manager.IndexToNode(from_idx)
            j = manager.IndexToNode(to_idx)
            return dist_matrix[i][j]

        transit_cb_idx = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_cb_idx)

        # Search parameters
        search_params = pywrapcp.DefaultRoutingSearchParameters()
        search_params.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        # Removed GUIDED_LOCAL_SEARCH as it forces the solver to run until TIME_LIMIT_SECONDS is exhausted
        # This allows instant millisecond solving for small node counts.
        search_params.time_limit.seconds = self.TIME_LIMIT_SECONDS

        # Solve
        solution = routing.SolveWithParameters(search_params)

        if not solution:
            raise RuntimeError("OR-Tools returned no solution")

        # Extract route
        index = routing.Start(0)
        ordered_employees: List[VRPEmployee] = []
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            if node != 0:  # skip depot
                ordered_employees.append(employees[node - 1])
            index = solution.Value(routing.NextVar(index))

        # Build stop list
        stops = [
            VRPStop(label=emp.name, lat=emp.lat, lng=emp.lng,
                    employee_id=emp.id)
            for emp in ordered_employees
        ]
        stops.append(VRPStop(
            label="Office",
            lat=self.office_lat,
            lng=self.office_lng,
            is_office=True
        ))
        return stops

    # ──────────────────────────────────────────
    #  NEAREST NEIGHBOR FALLBACK
    # ──────────────────────────────────────────

    def _nn_solve(self, employees: List[VRPEmployee]) -> List[VRPStop]:
        """Greedy nearest-neighbor heuristic — cab starts at office."""
        unvisited = employees[:]
        current_lat, current_lng = self.office_lat, self.office_lng
        ordered: List[VRPEmployee] = []

        while unvisited:
            nearest = min(
                unvisited,
                key=lambda e: manhattan_distance(current_lat, current_lng, e.lat, e.lng)
            )
            ordered.append(nearest)
            unvisited.remove(nearest)
            current_lat, current_lng = nearest.lat, nearest.lng

        stops = [
            VRPStop(label=emp.name, lat=emp.lat, lng=emp.lng,
                    employee_id=emp.id)
            for emp in ordered
        ]
        stops.append(VRPStop(
            label="Office",
            lat=self.office_lat,
            lng=self.office_lng,
            is_office=True
        ))
        return stops

    # ──────────────────────────────────────────
    #  DISTANCE MATRIX
    # ──────────────────────────────────────────

    def _build_distance_matrix(
        self, employees: List[VRPEmployee]
    ) -> List[List[int]]:
        """
        Build integer distance matrix (metres * 1000 → integer).
        Node 0 = office/depot, Nodes 1..n = employees.
        """
        coords: List[Tuple[float, float]] = (
            [(self.office_lat, self.office_lng)]     # node 0: office
            + [(e.lat, e.lng) for e in employees]    # nodes 1..n
        )
        n = len(coords)
        matrix = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i != j:
                    km = manhattan_distance(coords[i][0], coords[i][1],
                                          coords[j][0], coords[j][1])
                    matrix[i][j] = int(km * 1000)  # metres as int
        return matrix

    # ──────────────────────────────────────────
    #  ROUTE DISTANCE
    # ──────────────────────────────────────────

    def _route_distance(self, stops: List[VRPStop]) -> float:
        """Calculate total km for a stop list starting from office (depot)."""
        total = 0.0
        # Start from office
        prev_lat, prev_lng = self.office_lat, self.office_lng
        for stop in stops:
            total += manhattan_distance(prev_lat, prev_lng, stop.lat, stop.lng)
            prev_lat, prev_lng = stop.lat, stop.lng
        return total


# ─────────────────────────────────────────────
#  CONVENIENCE: FULL VRP PIPELINE
# ─────────────────────────────────────────────

def format_route_output(solution: VRPSolution) -> str:
    """Pretty-print the VRP solution in the format: Cab 101\npickup1 → ... → Office"""
    lines = [f"Solver Status: {solution.solver_status}",
             f"Total Distance: {solution.total_distance_km} km",
             ""]
    for route in solution.assignments:
        if not route.stops:
            lines.append(f"Cab {route.cab_id} (Type {route.cab_type}): [empty]")
            continue
        stop_labels = " → ".join(s.label for s in route.stops)
        lines.append(f"Cab {route.cab_id} (Type {route.cab_type}):")
        lines.append(f"  {stop_labels}")
        lines.append(f"  Distance: {route.distance_km} km  |  ETA: {route.eta_minutes} min  |  Solver: {route.solver_used}")
        lines.append("")
    if solution.unassigned_employee_ids:
        lines.append(f"⚠ Unassigned Employees: {solution.unassigned_employee_ids}")
    return "\n".join(lines)
