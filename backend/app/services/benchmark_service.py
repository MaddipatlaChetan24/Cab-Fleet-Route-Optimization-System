import itertools
import math

class BenchmarkService:

    def brute_force_route(self, employees):

        if len(employees) > 8:
            return None

        best_dist = float("inf")
        best_path = None

        for perm in itertools.permutations(employees):

            dist = 0
            cx, cy = 0,0

            for e in perm:
                dist += math.hypot(cx-e.x, cy-e.y)
                cx, cy = e.x, e.y

            dist += math.hypot(cx,cy)

            if dist < best_dist:
                best_dist = dist
                best_path = perm

        return best_dist