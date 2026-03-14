import math
from typing import List
from backend.app.models.domain import Employee, Cab
from backend.app.core.exceptions import InsufficientCapacityError
from backend.app.services.ml_predictor import TravelTimePredictor

class AssignmentService:
    def __init__(self):
        self.traffic = TravelTimePredictor()

    def create_cabs(self, n_a: int, n_b: int) -> List[Cab]:
        cabs: List[Cab] = []
        cab_id_counter = 1
        
        for _ in range(n_a):
            cabs.append(Cab(id=cab_id_counter, cab_type="A", capacity=4))
            cab_id_counter += 1
            
        for _ in range(n_b):
            cabs.append(Cab(id=cab_id_counter, cab_type="B", capacity=8))
            cab_id_counter += 1
            
        return cabs

    def assign_employees_to_cabs(self, employees: List[Employee], cabs: List[Cab]) -> None:
        # 1. Capacity Check
        total_capacity = sum(c.capacity for c in cabs)
        if len(employees) > total_capacity:
            raise InsufficientCapacityError(
                message=f"Insufficient capacity! You have {len(employees)} employees but only {total_capacity} total seats."
            )

        # 2. SMART POOLING: Group by Shift Time
        # This is a hard constraint: Employees in different shifts shouldn't be pooled.
        shift_groups = {}
        for emp in employees:
            if emp.shift_time not in shift_groups:
                shift_groups[emp.shift_time] = []
            shift_groups[emp.shift_time].append(emp)

        # 3. Sort Cabs by Capacity (Largest first for efficiency)
        cabs.sort(key=lambda c: c.capacity, reverse=True)
        cab_idx = 0

        # 4. Assign per Shift Group
        for shift, group_employees in shift_groups.items():
            # Get current hour for traffic (default to 8am if not parsable)
            try:
                hour = int(shift.split(':')[0])
            except:
                hour = 8

            # Spatial Sort (Sweep) with Traffic Weighting
            # We want to group people who "experience" similar traffic bottlenecks
            sorted_emps = sorted(
                group_employees,
                key=lambda emp: (
                    math.atan2(emp.y, emp.x), # Direction
                    self.traffic.get_traffic_multiplier(emp.x, emp.y) # Bottleneck grouping
                )
            )
            
            emp_idx = 0
            while emp_idx < len(sorted_emps) and cab_idx < len(cabs):
                cab = cabs[cab_idx]
                space_left = cab.capacity - len(cab.assigned_employees)
                
                # If cab is already partially full from another shift (shouldn't happen with strict shift grouping)
                # or if it has space, fill it.
                to_add = sorted_emps[emp_idx : emp_idx + space_left]
                cab.assigned_employees.extend(to_add)
                emp_idx += len(to_add)
                
                if len(cab.assigned_employees) >= cab.capacity:
                    cab_idx += 1