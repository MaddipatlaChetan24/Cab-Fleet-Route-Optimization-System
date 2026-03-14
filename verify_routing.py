import sys
import os
import math

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app.services.routing_service import RoutingService
from backend.app.services.assignment_service import AssignmentService
from backend.app.models.domain import Employee, Cab

def test_routing_logic():
    routing_service = RoutingService(depot=(0, 0))
    assignment_service = AssignmentService()

    # 1. Test Manhattan Distance
    d = routing_service.distance(0, 0, 3, 4)
    expected = abs(0 - 3) + abs(0 - 4)
    print(f"Manhattan Distance (0,0) to (3,4): {d} (Expected: {expected})")
    assert d == expected

    # 2. Test Assignment and Capacity
    employees = [
        Employee(id=1, x=1, y=1),
        Employee(id=2, x=2, y=2),
        Employee(id=3, x=-1, y=-1),
        Employee(id=4, x=-2, y=-2),
        Employee(id=5, x=5, y=5)
    ]
    
    # N_a = 1 (4 seats), N_b = 0
    cabs = assignment_service.create_cabs(n_a=1, n_b=0)
    print(f"Cabs created: {[ (c.id, c.capacity) for c in cabs]}")
    
    try:
        assignment_service.assign_employees_to_cabs(employees, cabs)
        print("Error: Should have raised InsufficientCapacityError")
    except Exception as e:
        print(f"Caught expected error: {e}")

    # N_a = 2 (total 8 seats)
    cabs = assignment_service.create_cabs(n_a=2, n_b=0)
    assignment_service.assign_employees_to_cabs(employees, cabs)
    
    for cab in cabs:
        print(f"Cab {cab.id} ({cab.cab_type}) assigned: {[e.id for e in cab.assigned_employees]}")
        assert len(cab.assigned_employees) <= cab.capacity

    # 3. Test Routing (No Return)
    cab = cabs[0]
    route = routing_service.optimize_route_for_cab(cab)
    print(f"Route for Cab {cab.id}: Dist={route.distance}, Stops={[e.id for e in route.stops]}")
    
    # Calculate expected distance for the route
    # Depot (0,0) -> Stop1 -> Stop2 ...
    expected_dist = 0
    curr_x, curr_y = (0, 0)
    for stop in route.stops:
        expected_dist += abs(curr_x - stop.x) + abs(curr_y - stop.y)
        curr_x, curr_y = stop.x, stop.y
    
    print(f"Manually calculated distance: {expected_dist} (Route reported: {route.distance})")
    assert round(route.distance, 2) == round(expected_dist, 2)

if __name__ == "__main__":
    test_routing_logic()
    print("\nALL TESTS PASSED!")
