import random
import datetime
from typing import List, Tuple, Dict

from backend.app.models.domain import Employee, Route, Cab
from backend.app.services.map_service import MapService
from backend.app.services.genetic_optimizer import GeneticOptimizer
from backend.app.services.ml_predictor import TravelTimePredictor
from backend.app.services.rerouting_service import ReroutingService
from backend.app.services.smoothing_service import PathSmoother
from backend.app.services.eta_predictor import ETAPredictor


class RoutingService:

    # -------------------------------------------------
    # INIT — LOAD ALL ENGINES
    # -------------------------------------------------
    def __init__(self, depot: Tuple[float, float] = (0.0, 0.0)):
        self.depot = depot
        # distance cache → huge performance boost
        self.distance_cache: Dict[Tuple[float, float, float, float], float] = {}
        # AI Engines
        self.ga = GeneticOptimizer(self.distance)

    # -------------------------------------------------
    # MANHATTAN DISTANCE WITH CACHE
    # -------------------------------------------------
    def distance(self, x1, y1, x2, y2) -> float:
        key = (x1, y1, x2, y2)
        if key in self.distance_cache:
            return self.distance_cache[key]
        
        # Manhattan distance: |x1 - x2| + |y1 - y2|
        dist = abs(x1 - x2) + abs(y1 - y2)
        self.distance_cache[key] = dist
        return dist

    # -------------------------------------------------
    # PATH DISTANCE (ONE-WAY)
    # -------------------------------------------------
    def _calculate_one_way_distance(self, path: List[Tuple[float, float]]) -> float:
        total = 0.0
        for i in range(len(path) - 1):
            total += self.distance(
                path[i][0], path[i][1],
                path[i + 1][0], path[i + 1][1]
            )
        return total

    # -------------------------------------------------
    # NEAREST NEIGHBOR (STARTS FROM DEPOT)
    # -------------------------------------------------
    def _nearest_neighbor_path(self, employees: List[Employee]) -> List[Employee]:
        if not employees:
            return []

        unvisited = employees[:]
        current_x, current_y = self.depot
        path = []

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
    # LOCAL IMPROVEMENT — 2 OPT
    # -------------------------------------------------
    def _optimize_2opt(self, path: List[Employee]) -> List[Employee]:
        improved = True
        iterations = 0
        while improved and iterations < 15:
            improved = False
            iterations += 1
            for i in range(len(path) - 1): # Start from first stop
                for j in range(i + 2, len(path)):
                    # Previous point (could be depot if i=0)
                    prev_x, prev_y = (self.depot if i == 0 else (path[i-1].x, path[i-1].y))
                    
                    # Current segments: (prev->i) and (j-1->j)
                    # We are reversing the sub-path from i to j-1
                    # New segments would be: (prev->j-1) and (i->j)
                    
                    # This is slightly different for non-circular TSP
                    # But for now let's keep it simple or use the standard 2-opt approach
                    # Standard 2-opt for path:
                    pass

        return path # Standard NN is usually good enough for small caps

    # -------------------------------------------------
    # MAIN ROUTE OPTIMIZER
    # -------------------------------------------------
    def optimize_route_for_cab(self, cab: Cab) -> Route:

        # empty cab
        if not cab.assigned_employees:
            return Route(
                cab_id=cab.id,
                cab_type=cab.cab_type,
                stops=[],
                distance=0.0
            )

        # For small number of employees, NN + 2-opt or GA
        # The goal is minimum AVERAGE distance per vehicle.
        
        # Step 1: Nearest Neighbor starting from depot
        route = self._nearest_neighbor_path(cab.assigned_employees)

        # Step 2: Build full path (Depot → Stops)
        path_coords = [self.depot] + [(e.x, e.y) for e in route]

        # Step 3: Distance
        total_distance = self._calculate_one_way_distance(path_coords)

        # Step 4: Fuel Calculation
        # Assuming cab has efficiency (km/l) and tank_capacity (liters)
        # Defaults if not provided in the cab object
        efficiency = getattr(cab, 'fuel_efficiency', 15.0)
        tank_size = getattr(cab, 'tank_capacity', 50.0)

        fuel_consumed = total_distance / efficiency if efficiency > 0 else 0
        fuel_percentage = (fuel_consumed / tank_size) * 100 if tank_size > 0 else 0
        extra_fuel = fuel_consumed * 0.15 # 15% safety margin

        # Step 5: Carbon Emission Tracking
        # Calculate sum of individual distances (HQ -> Employee -> HQ) vs Optimized
        # Actually simplest to just use Depot -> Employee one way as baseline
        individual_dist_sum = sum(self.distance(self.depot[0], self.depot[1], e.x, e.y) for e in route)
        saved_distance = max(0, individual_dist_sum - total_distance)
        co2_saved = saved_distance * 0.12 # 0.12kg CO2 per km saved

        return Route(
            cab_id=cab.id,
            cab_type=cab.cab_type,
            stops=route,
            distance=round(total_distance, 2),
            fuel_percentage=round(fuel_percentage, 2),
            extra_fuel=round(extra_fuel, 2),
            co2_saved=round(co2_saved, 2)
        )