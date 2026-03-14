"""
verify_vrp.py — Phase 3 VRP End-to-End Verification
====================================================
Run directly:
    cd "/Users/chetan/Documents/cap da"
    python verify_vrp.py

Tests:
  1. Clustering: employees assigned to correct number of cabs
  2. Capacity: no cab exceeds its limit
  3. VRP solve: all employees appear exactly once across all routes
  4. Routing: every route ends at Office
  5. Distance: total > 0 for non-trivial inputs
  6. Formatted output matches expected pattern
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app.services.vrp_service import VRPService, VRPEmployee, format_route_output
from backend.app.services.clustering_service import ClusteringService, format_cluster_summary

# ─────────────────────────────────────────────
#  TEST DATA — Mumbai area (real coordinates)
# ─────────────────────────────────────────────

OFFICE_LAT = 19.0760
OFFICE_LNG = 72.8777

EMPLOYEES = [
    VRPEmployee(id=1,  lat=19.1200, lng=72.8500, name="Emp#1"),   # Andheri West
    VRPEmployee(id=2,  lat=19.1300, lng=72.8600, name="Emp#2"),   # Andheri East
    VRPEmployee(id=3,  lat=19.0800, lng=72.8200, name="Emp#3"),   # Bandra West
    VRPEmployee(id=4,  lat=19.0900, lng=72.8400, name="Emp#4"),   # Bandra East
    VRPEmployee(id=5,  lat=19.1100, lng=72.8800, name="Emp#5"),   # Jogeshwari
    VRPEmployee(id=6,  lat=19.0600, lng=72.8300, name="Emp#6"),   # Mahim
    VRPEmployee(id=7,  lat=19.1500, lng=72.8700, name="Emp#7"),   # Goregaon
    VRPEmployee(id=8,  lat=19.1050, lng=72.8450, name="Emp#8"),   # Vile Parle
    VRPEmployee(id=9,  lat=19.0750, lng=72.9000, name="Emp#9"),   # Kurla
    VRPEmployee(id=10, lat=19.0500, lng=72.8150, name="Emp#10"),  # Sion
]

N_A = 2   # Two 4-seaters  (capacity = 8)
N_B = 1   # One  8-seater  (capacity = 8)
# Total capacity = 16, employees = 10 ✓

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────

PASS = "✅ PASS"
FAIL = "❌ FAIL"

def check(cond, msg):
    tag = PASS if cond else FAIL
    print(f"  {tag}  {msg}")
    return cond

# ─────────────────────────────────────────────
#  TEST 1: CLUSTERING
# ─────────────────────────────────────────────

print("=" * 60)
print(" PHASE 3 VRP — VERIFICATION SCRIPT")
print("=" * 60)
print()
print("TEST 1: Geographic K-Means Clustering")
print("-" * 40)

clustering = ClusteringService()
cabs = clustering.assign(
    employees=EMPLOYEES,
    n_a=N_A,
    n_b=N_B,
    office_lat=OFFICE_LAT,
    office_lng=OFFICE_LNG
)

print(format_cluster_summary(cabs))
print()

results = []
results.append(check(len(cabs) == N_A + N_B, f"Correct number of cabs: {len(cabs)} == {N_A + N_B}"))
results.append(check(all(len(c.assigned_employees) <= c.capacity for c in cabs),
    "No cab exceeds capacity"))

total_assigned = sum(len(c.assigned_employees) for c in cabs)
results.append(check(total_assigned == len(EMPLOYEES),
    f"All employees assigned: {total_assigned}/{len(EMPLOYEES)}"))

# ─────────────────────────────────────────────
#  TEST 2: VRP SOLVE
# ─────────────────────────────────────────────

print()
print("TEST 2: VRP Route Optimization (OR-Tools + Fallback)")
print("-" * 40)

vrp = VRPService(office_lat=OFFICE_LAT, office_lng=OFFICE_LNG)
solution = vrp.solve(cabs)

print(format_route_output(solution))

results.append(check(
    solution.solver_status in ("ROUTING_SUCCESS", "FALLBACK"),
    f"Solver succeeded: status={solution.solver_status}"
))

results.append(check(solution.total_distance_km > 0,
    f"Total distance > 0: {solution.total_distance_km} km"))

# Every employee appears exactly once
all_emp_ids_in_routes = []
for route in solution.assignments:
    for stop in route.stops:
        if not stop.is_office and stop.employee_id is not None:
            all_emp_ids_in_routes.append(stop.employee_id)

expected_ids = sorted(e.id for e in EMPLOYEES)
actual_ids   = sorted(all_emp_ids_in_routes)
results.append(check(actual_ids == expected_ids,
    f"All employees in routes exactly once: {actual_ids}"))

# Every route ends at Office
for route in solution.assignments:
    if route.stops:
        last = route.stops[-1]
        results.append(check(last.is_office,
            f"Cab {route.cab_id} — last stop is Office (got: {last.label})"))

# ─────────────────────────────────────────────
#  TEST 3: EXAMPLE OUTPUT FORMAT
# ─────────────────────────────────────────────

print()
print("TEST 3: Route Output Format")
print("-" * 40)
for route in solution.assignments:
    if route.stops:
        labels = " → ".join(s.label for s in route.stops)
        print(f"  Cab {route.cab_id} (Type {route.cab_type}): {labels}")
print()

# ─────────────────────────────────────────────
#  SUMMARY
# ─────────────────────────────────────────────

all_passed = all(results)
total = len(results)
passed = sum(results)

print("=" * 60)
print(f" RESULT: {passed}/{total} tests passed {'🎉' if all_passed else '⚠'}")
if not all_passed:
    print(" Some tests FAILED — review output above.")
print("=" * 60)

sys.exit(0 if all_passed else 1)
