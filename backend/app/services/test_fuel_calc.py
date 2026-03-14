import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from backend.app.services.routing_service import RoutingService
from backend.app.models.domain import Cab, Employee

def test_fuel_calculation():
    service = RoutingService(depot=(0, 0))
    
    # Test Cab Type A (4 seater, efficiency 15, tank 50)
    cab_a = Cab(id=1, cab_type="A", capacity=4, fuel_efficiency=15, tank_capacity=50)
    emp1 = Employee(id=101, x=10, y=0) # Distance 10 (0,0 to 10,0)
    cab_a.assigned_employees = [emp1]
    
    route_a = service.optimize_route_for_cab(cab_a)
    
    # Distance = 10
    # Fuel Consumed = 10 / 15 = 0.666...
    # Fuel % = (0.666 / 50) * 100 = 1.333...
    # Extra Fuel = 0.666 * 0.15 = 0.1
    
    print(f"Cab A - Distance: {route_a.distance}")
    print(f"Cab A - Fuel %: {route_a.fuel_percentage}")
    print(f"Cab A - Extra Fuel: {route_a.extra_fuel}")
    
    assert route_a.distance == 10.0
    assert route_a.fuel_percentage == 1.33 # Round(1.333)
    assert route_a.extra_fuel == 0.1 # Round(0.1)

    # Test Cab Type B (8 seater, efficiency 10, tank 80)
    cab_b = Cab(id=2, cab_type="B", capacity=8, fuel_efficiency=10, tank_capacity=80)
    emp2 = Employee(id=102, x=20, y=20) # Distance 40 (0,0 to 20,20)
    cab_b.assigned_employees = [emp2]
    
    route_b = service.optimize_route_for_cab(cab_b)
    
    # Distance = 40
    # Fuel Consumed = 40 / 10 = 4.0
    # Fuel % = (4.0 / 80) * 100 = 5.0
    # Extra Fuel = 4.0 * 0.15 = 0.6
    
    print(f"Cab B - Distance: {route_b.distance}")
    print(f"Cab B - Fuel %: {route_b.fuel_percentage}")
    print(f"Cab B - Extra Fuel: {route_b.extra_fuel}")
    
    assert route_b.distance == 40.0
    assert route_b.fuel_percentage == 5.0
    assert route_b.extra_fuel == 0.6

    print("All fuel calculation tests passed!")

if __name__ == "__main__":
    test_fuel_calculation()
