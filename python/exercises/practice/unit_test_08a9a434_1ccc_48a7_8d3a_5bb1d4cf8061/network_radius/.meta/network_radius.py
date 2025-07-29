import math
from functools import lru_cache

def find_minimum_radius(buildings, k):
    if not buildings:
        return 0.0
    n = len(buildings)
    if k >= n:
        return 0.0

    def dist(a, b):
        return math.hypot(a[0] - b[0], a[1] - b[1])
    
    # Determine an initial upper bound for R: half the maximum pairwise distance.
    max_d = 0.0
    for i in range(n):
        for j in range(i + 1, n):
            d = dist(buildings[i], buildings[j])
            if d > max_d:
                max_d = d
    high = max_d / 2.0
    low = 0.0

    def can_cover(R):
        candidate_centers = []
        # Add each building as a candidate center.
        for i in range(n):
            candidate_centers.append(buildings[i])
        # For every pair of distinct buildings, if their distance is <= 2R, compute intersection points.
        for i in range(n):
            x0, y0 = buildings[i]
            for j in range(i + 1, n):
                x1, y1 = buildings[j]
                d = dist(buildings[i], buildings[j])
                if d > 2 * R + 1e-8:
                    continue
                if d < 1e-8:
                    continue
                midx = (x0 + x1) / 2.0
                midy = (y0 + y1) / 2.0
                try:
                    h = math.sqrt(R * R - (d / 2.0) * (d / 2.0))
                except Exception:
                    h = 0.0
                dx = (x1 - x0) / d
                dy = (y1 - y0) / d
                # Perpendicular vector components.
                px = -dy
                py = dx
                center1 = (midx + h * px, midy + h * py)
                center2 = (midx - h * px, midy - h * py)
                candidate_centers.append(center1)
                candidate_centers.append(center2)
        
        # For each candidate center, determine which buildings are covered.
        candidate_disks = []
        for center in candidate_centers:
            covered = set()
            cx, cy = center
            for idx, (bx, by) in enumerate(buildings):
                if math.hypot(cx - bx, cy - by) <= R + 1e-8:
                    covered.add(idx)
            candidate_disks.append(covered)
        
        # Build a mapping for each building to candidate disks that cover it.
        mapping = {i: [] for i in range(n)}
        for disk in candidate_disks:
            for idx in disk:
                mapping[idx].append(disk)
        
        universe = frozenset(range(n))
        
        @lru_cache(maxsize=None)
        def search(uncovered, disks_left):
            if not uncovered:
                return True
            if disks_left == 0:
                return False
            uncovered_set = set(uncovered)
            # Choose an arbitrary uncovered building
            i = next(iter(uncovered_set))
            for disk in mapping[i]:
                new_uncovered = uncovered_set - disk
                if search(frozenset(new_uncovered), disks_left - 1):
                    return True
            return False
        
        return search(universe, k)

    for _ in range(50):
        mid = (low + high) / 2.0
        if can_cover(mid):
            high = mid
        else:
            low = mid
    return high