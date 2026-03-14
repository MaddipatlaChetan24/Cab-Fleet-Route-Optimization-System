"""
clustering_service.py — Phase 3 Geographic K-Means Clustering
==============================================================
Assigns employees to cabs using geographic proximity BEFORE routing.

Algorithm:
  1. K-Means clustering (k = number of cabs) using Haversine distances
  2. Capacity enforcement — if a cluster exceeds cab capacity, overflow
     employees are moved to the nearest under-capacity cab
  3. Returns: list of VRPCab objects with employees pre-assigned
"""

import math
import random
import logging
from typing import List, Tuple
from backend.app.services.vrp_service import VRPEmployee, VRPCab, manhattan_distance

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
#  CLUSTERING SERVICE
# ─────────────────────────────────────────────

class ClusteringService:
    """
    K-Means geographic clustering to pre-assign employees to cabs.

    Steps:
        1. Determine k = total number of cabs (n_a + n_b)
        2. Run K-Means on employee (lat, lng) pairs
        3. Assign each cluster to a cab, respecting capacity
        4. Handle overflow by reassigning to nearest under-capacity cab

    Why cluster before routing?
        OR-Tools solves per-cab independently.
        Good clustering = geographically local employees per cab
        = shorter intra-cab routes = better overall solution.
    """

    MAX_KMEANS_ITERATIONS = 100
    KMEANS_RESTARTS = 5          # Run K-Means multiple times, pick best

    # ──────────────────────────────────────────
    #  PUBLIC: ASSIGN EMPLOYEES TO CABS
    # ──────────────────────────────────────────

    def assign(
        self,
        employees: List[VRPEmployee],
        n_a: int,   # 4-seater cabs
        n_b: int,   # 8-seater cabs
        office_lat: float,
        office_lng: float
    ) -> List[VRPCab]:
        """
        Cluster employees and assign to cabs.
        Returns list of VRPCab with assigned_employees populated.
        """
        # Create cab objects (sorted largest first for better packing)
        cabs = self._create_cabs(n_a, n_b)
        n_cabs = len(cabs)

        if not employees or n_cabs == 0:
            return cabs

        # Capacity check
        total_capacity = sum(c.capacity for c in cabs)
        if len(employees) > total_capacity:
            logger.warning(
                "Not enough capacity: %d employees, %d seats",
                len(employees), total_capacity
            )
            # Truncate to capacity (prefer employees closer to office)
            employees = sorted(
                employees,
                key=lambda e: manhattan_distance(e.lat, e.lng, office_lat, office_lng)
            )[:total_capacity]

        # Edge case: all cabs the same capacity → standard K-Means
        # Otherwise: weighted clustering (more employees near larger cabs)
        clusters = self._kmeans_cluster(employees, n_cabs)

        # Assign clusters to cabs (largest cluster → largest cab)
        self._assign_clusters_to_cabs(clusters, cabs)

        # Fix capacity overflows
        self._fix_overflow(cabs)

        # Calculate and store centroid and radius for each cab
        self._calculate_cluster_metadata(cabs)

        return cabs

    # ──────────────────────────────────────────
    #  CAB CREATION
    # ──────────────────────────────────────────

    def _create_cabs(self, n_a: int, n_b: int) -> List[VRPCab]:
        cabs: List[VRPCab] = []
        cab_id = 101  # Starting ID for VRP cabs (distinct from optimize endpoint)

        # Type B (8-seater) first — largest capacity
        for _ in range(n_b):
            cabs.append(VRPCab(id=cab_id, cab_type="B", capacity=8))
            cab_id += 1

        # Type A (4-seater)
        for _ in range(n_a):
            cabs.append(VRPCab(id=cab_id, cab_type="A", capacity=4))
            cab_id += 1

        return cabs

    # ──────────────────────────────────────────
    #  K-MEANS CLUSTERING
    # ──────────────────────────────────────────

    def _kmeans_cluster(
        self, employees: List[VRPEmployee], k: int
    ) -> List[List[VRPEmployee]]:
        """
        K-Means with Haversine distance. Restarts KMEANS_RESTARTS times.
        Returns k clusters (some may be empty).
        """
        if k >= len(employees):
            # Each employee gets their own cluster
            return [[emp] for emp in employees] + [[] for _ in range(k - len(employees))]

        best_clusters = None
        best_inertia = float("inf")

        for _ in range(self.KMEANS_RESTARTS):
            clusters, inertia = self._run_kmeans(employees, k)
            if inertia < best_inertia:
                best_inertia = inertia
                best_clusters = clusters

        return best_clusters

    def _run_kmeans(
        self, employees: List[VRPEmployee], k: int
    ) -> Tuple[List[List[VRPEmployee]], float]:
        """Single K-Means run. Returns (clusters, inertia)."""

        # Random initialisation (k-means++ lite)
        centroids = self._init_centroids(employees, k)

        clusters: List[List[VRPEmployee]] = [[] for _ in range(k)]

        for iteration in range(self.MAX_KMEANS_ITERATIONS):
            # Assignment step
            new_clusters: List[List[VRPEmployee]] = [[] for _ in range(k)]
            for emp in employees:
                distances = [
                    manhattan_distance(emp.lat, emp.lng, lat, lng)
                    for lat, lng in centroids
                ]
                nearest_cluster = distances.index(min(distances))
                new_clusters[nearest_cluster].append(emp)

            # Update centroids
            new_centroids = []
            for ci, cluster in enumerate(new_clusters):
                if cluster:
                    mean_lat = sum(e.lat for e in cluster) / len(cluster)
                    mean_lng = sum(e.lng for e in cluster) / len(cluster)
                    new_centroids.append((mean_lat, mean_lng))
                else:
                    # Empty cluster — keep old centroid or reassign to random
                    new_centroids.append(centroids[ci])

            # Convergence check
            shift = sum(
                manhattan_distance(centroids[i][0], centroids[i][1],
                                   new_centroids[i][0], new_centroids[i][1])
                for i in range(k)
            )
            centroids = new_centroids
            clusters = new_clusters

            if shift < 0.001:  # km — converged
                break

        # Compute inertia (sum of squared distances to centroid)
        inertia = 0.0
        for ci, cluster in enumerate(clusters):
            for emp in cluster:
                inertia += manhattan_distance(
                    emp.lat, emp.lng, centroids[ci][0], centroids[ci][1]
                ) ** 2

        return clusters, inertia

    def _init_centroids(
        self, employees: List[VRPEmployee], k: int
    ) -> List[Tuple[float, float]]:
        """K-Means++ style initialisation."""
        chosen = [random.choice(employees)]

        while len(chosen) < k:
            # Weighted probability by distance to nearest chosen centroid
            dists = []
            for emp in employees:
                min_d = min(
                    manhattan_distance(emp.lat, emp.lng, c.lat, c.lng)
                    for c in chosen
                )
                dists.append(min_d ** 2)

            total = sum(dists)
            if total == 0:
                chosen.append(random.choice(employees))
                continue

            probs = [d / total for d in dists]
            r = random.random()
            cumulative = 0.0
            for emp, prob in zip(employees, probs):
                cumulative += prob
                if r <= cumulative:
                    chosen.append(emp)
                    break
            else:
                chosen.append(employees[-1])

        return [(c.lat, c.lng) for c in chosen]

    # ──────────────────────────────────────────
    #  CLUSTER → CAB ASSIGNMENT
    # ──────────────────────────────────────────

    def _assign_clusters_to_cabs(
        self, clusters: List[List[VRPEmployee]], cabs: List[VRPCab]
    ) -> None:
        """
        Assign clusters to cabs: largest cluster → largest cab.
        Employees are already sorted inside each cluster by K-Means.
        """
        # Sort clusters by size descending
        sorted_clusters = sorted(clusters, key=len, reverse=True)
        # Sort cabs by capacity descending
        sorted_cabs = sorted(cabs, key=lambda c: c.capacity, reverse=True)

        # Pool all employees (largest cluster first)
        all_employees: List[VRPEmployee] = []
        for cluster in sorted_clusters:
            all_employees.extend(cluster)

        # Fill cabs in order
        emp_idx = 0
        for cab in sorted_cabs:
            to_take = min(cab.capacity, len(all_employees) - emp_idx)
            cab.assigned_employees = all_employees[emp_idx: emp_idx + to_take]
            emp_idx += to_take

    # ──────────────────────────────────────────
    #  OVERFLOW FIXING
    # ──────────────────────────────────────────

    def _fix_overflow(self, cabs: List[VRPCab]) -> None:
        """
        If any cab is over capacity, move excess employees to
        the nearest under-capacity cab (by centroid distance).
        This should not happen after _assign_clusters_to_cabs, but
        is a safety net in case of edge cases.
        """
        overflow_pool: List[VRPEmployee] = []

        for cab in cabs:
            if len(cab.assigned_employees) > cab.capacity:
                excess = cab.assigned_employees[cab.capacity:]
                cab.assigned_employees = cab.assigned_employees[:cab.capacity]
                overflow_pool.extend(excess)

        for emp in overflow_pool:
            # Find cab with most available space
            target = max(
                cabs,
                key=lambda c: c.capacity - len(c.assigned_employees)
            )
            space = target.capacity - len(target.assigned_employees)
            if space > 0:
                target.assigned_employees.append(emp)
            else:
                logger.warning("Employee %d cannot be assigned — all cabs full", emp.id)

    # ──────────────────────────────────────────
    #  CLUSTER METADATA CALCULATION
    # ──────────────────────────────────────────

    def _calculate_cluster_metadata(self, cabs: List[VRPCab]) -> None:
        """
        Calculates the geographic centroid and max radius (in km)
        for the employees assigned to each cab.
        """
        for cab in cabs:
            employees = cab.assigned_employees
            if not employees:
                cab.cluster_centroid_lat = None
                cab.cluster_centroid_lng = None
                cab.cluster_radius_km = None
                continue

            # Calculate centroid
            mean_lat = sum(e.lat for e in employees) / len(employees)
            mean_lng = sum(e.lng for e in employees) / len(employees)
            cab.cluster_centroid_lat = mean_lat
            cab.cluster_centroid_lng = mean_lng

            # Calculate radius (max distance from centroid to any employee)
            max_radius = 0.0
            for e in employees:
                dist = manhattan_distance(mean_lat, mean_lng, e.lat, e.lng)
                if dist > max_radius:
                    max_radius = dist
            
            # Ensure a minimum visual radius even for a single employee or tight cluster
            cab.cluster_radius_km = max(max_radius, 0.5)


# ─────────────────────────────────────────────
#  CONVENIENCE: CLUSTER SUMMARY
# ─────────────────────────────────────────────

def format_cluster_summary(cabs: List[VRPCab]) -> str:
    lines = ["Cluster Assignment:"]
    for cab in cabs:
        emp_ids = [str(e.id) for e in cab.assigned_employees]
        fill = f"{len(cab.assigned_employees)}/{cab.capacity}"
        lines.append(
            f"  Cab {cab.id} (Type {cab.cab_type}, {fill}): "
            f"employees [{', '.join(emp_ids)}]"
        )
    return "\n".join(lines)
