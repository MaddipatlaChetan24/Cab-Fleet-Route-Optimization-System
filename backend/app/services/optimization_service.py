import random
from typing import List, Tuple, Dict
from backend.app.models.domain import Employee, Route, Cab
from .map_service import MapService


class OptimizationService:

    def __init__(self, depot: Tuple[float, float] = (19.0760, 72.8777)):
        self.map_service = MapService()
        self.depot = depot
        self.distance_cache: Dict[Tuple[float, float, float, float], float] = {}

    # -------------------------------------------------
    # TRAFFIC SIMULATION FACTOR
    # -------------------------------------------------
    def traffic_multiplier(self) -> float:
        return random.uniform(1.0, 1.35)

    # -------------------------------------------------
    # DISTANCE WITH CACHE + TRAFFIC
    # -------------------------------------------------
    def distance(self, x1: float, y1: float, x2: float, y2: float) -> float:
        key = (x1, y1, x2, y2)

        if key in self.distance_cache:
            return self.distance_cache[key]

        base = self.map_service.road_distance(x1, y1, x2, y2)
        traffic_adjusted = base * self.traffic_multiplier()

        self.distance_cache[key] = traffic_adjusted
        return traffic_adjusted

    # -------------------------------------------------
    # PATH DISTANCE
    # -------------------------------------------------
    def _calculate_path_distance(self, path: List[Tuple[float, float]]) -> float:
        total = 0.0
        for i in range(len(path) - 1):
            total += self.distance(
                path[i][0], path[i][1],
                path[i + 1][0], path[i + 1][1]
            )
        return total

    # -------------------------------------------------
    # NEAREST NEIGHBOR
    # -------------------------------------------------
    def _nearest_neighbor_path(self, employees: List[Employee]) -> List[Employee]:
        if not employees:
            return []

        unvisited = employees[:]

        start = min(
            unvisited,
            key=lambda e: self.distance(self.depot[0], self.depot[1], e.x, e.y)
        )

        path = [start]
        unvisited.remove(start)

        current_x, current_y = start.x, start.y

        while unvisited:
            nearest = min(
                unvisited,
                key=lambda e: self.distance(current_x, current_y, e.x, e.y)
            )
            path.append(nearest)
            unvisited.remove(nearest)
            current_x, current_y = nearest.x, nearest.y

        return path

    # -------------------------------------------------
    # 2-OPT IMPROVEMENT
    # -------------------------------------------------
    def _optimize_2opt(self, path: List[Employee]) -> List[Employee]:
        improved = True
        iterations = 0

        while improved and iterations < 15:
            improved = False
            iterations += 1

            for i in range(len(path) - 2):
                for j in range(i + 2, len(path)):

                    a = (path[i].x, path[i].y)
                    b = (path[i + 1].x, path[i + 1].y)
                    c = (path[j - 1].x, path[j - 1].y)
                    d = (path[j].x, path[j].y)

                    old = self.distance(*a, *b) + self.distance(*c, *d)
                    new = self.distance(*a, *c) + self.distance(*b, *d)

                    if new < old:
                        path[i + 1:j] = list(reversed(path[i + 1:j]))
                        improved = True

        return path

    # -------------------------------------------------
    # MAIN ROUTE OPTIMIZER
    # -------------------------------------------------
    def optimize_route_for_cab(self, cab: Cab) -> Route:

        if not cab.assigned_employees:
            return Route(
                cab_id=cab.id,
                cab_type=cab.cab_type,
                stops=[],
                distance=0
            )

        # Step 1: Nearest Neighbor
        nn_path = self._nearest_neighbor_path(cab.assigned_employees)

        # Step 2: 2-Opt Optimization
        optimized = self._optimize_2opt(nn_path)

        # Step 3: Build full path (Depot → Stops → Depot)
        path_coords = (
            [self.depot]
            + [(e.x, e.y) for e in optimized]
            + [self.depot]
        )

        total_distance = self._calculate_path_distance(path_coords)

        return Route(
            cab_id=cab.id,
            cab_type=cab.cab_type,
            stops=optimized,
            distance=round(total_distance, 2)
        )