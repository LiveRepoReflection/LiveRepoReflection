import math

def euclidean_distance(p, q):
    return math.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)

def solve(N, customer_locations, M, obstacle_locations, R, D, C, B):
    if N == 0:
        return []
    obstacles = set(obstacle_locations)
    uncovered = set(customer_locations)
    aps = []
    while uncovered:
        best_candidate = None
        best_coverage = set()
        for cust in list(uncovered):
            candidate = cust
            if candidate in obstacles:
                continue
            valid = True
            for ap in aps:
                if euclidean_distance(candidate, ap) < D - 1e-6:
                    valid = False
                    break
            if not valid:
                continue
            coverage = set()
            for other in uncovered:
                if euclidean_distance(candidate, other) <= R + 1e-6:
                    coverage.add(other)
            if len(coverage) > len(best_coverage):
                best_candidate = candidate
                best_coverage = coverage
        if best_candidate is None:
            return []
        aps.append(best_candidate)
        uncovered -= best_coverage
        if len(aps) * C > B:
            return []
    return aps