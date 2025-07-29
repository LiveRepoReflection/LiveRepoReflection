import heapq
import math

# Global graph variable: a dictionary representing the road network.
# Each key is a node and its value is a list of tuples (neighbor, base_time)
graph = {}

# Global congestion function.
# This function should be treated as a black box. For dependency injection,
# users can override this with their own implementation.
def congestion(u, v, t):
    # Default congestion always returns 1.
    return 1

def plan_route(start, end, departure_time, horizon):
    """
    Computes the fastest route for a single AV from start to end given the departure_time and horizon.
    The travel time on edge (u, v) is computed as:
       base_time * congestion(u, v, current_time)
    Returns a tuple: (path, arrival_time). If no path exists within the planning horizon, returns (None, None).
    """
    # Priority queue entries: (current_time, current_node, path_so_far)
    pq = []
    heapq.heappush(pq, (departure_time, start, [start]))
    best_arrival = {}  # For pruning: best_arrival[node] stores the minimum arrival time found.

    while pq:
        current_time, node, path = heapq.heappop(pq)

        # Check if reached destination.
        if node == end:
            return (path, current_time)

        # If current_time exceeds planning horizon, skip this path.
        if current_time > departure_time + horizon:
            continue

        # Prune if we already have a better arrival time for node.
        if node in best_arrival and best_arrival[node] <= current_time:
            continue
        best_arrival[node] = current_time

        # Explore neighbors.
        for neighbor, base_time in graph.get(node, []):
            travel = base_time * congestion(node, neighbor, current_time)
            new_time = current_time + travel
            if new_time <= departure_time + horizon:
                heapq.heappush(pq, (new_time, neighbor, path + [neighbor]))

    return (None, None)

def static_shortest(source, target):
    """
    Computes the shortest travel time from source to target using constant congestion.
    This function assumes that congestion(u, v, t) returns a constant value when t is fixed (e.g., t=0).
    Returns the travel time if target is reachable; otherwise returns math.inf.
    """
    pq = []
    heapq.heappush(pq, (0, source))
    best_time = {}

    while pq:
        current_time, node = heapq.heappop(pq)
        if node == target:
            return current_time
        if node in best_time and best_time[node] <= current_time:
            continue
        best_time[node] = current_time
        for neighbor, base_time in graph.get(node, []):
            travel = base_time * congestion(node, neighbor, 0)
            new_time = current_time + travel
            heapq.heappush(pq, (new_time, neighbor))
    return math.inf

def hungarian(matrix):
    """
    An implementation of the Hungarian Algorithm (Munkres algorithm) for solving the assignment problem.
    The input 'matrix' is a list of lists representing the cost matrix.
    Returns a tuple: (min_cost, assignment) where assignment is a list such that assignment[i] = j 
    means row i is assigned to column j.
    """
    # Ensure the matrix is square by padding with zeros if necessary.
    n = len(matrix)
    m = len(matrix[0]) if matrix else 0
    size = max(n, m)
    cost = [row[:] + [0]*(size - m) for row in matrix] + [[0]*size for _ in range(size - n)]

    # Initialize labels
    u = [0] * (size + 1)
    v = [0] * (size + 1)
    p = [0] * (size + 1)
    way = [0] * (size + 1)

    for i in range(1, size + 1):
        p[0] = i
        minv = [math.inf] * (size + 1)
        used = [False] * (size + 1)
        j0 = 0
        while True:
            used[j0] = True
            i0 = p[j0]
            delta = math.inf
            j1 = 0
            for j in range(1, size + 1):
                if not used[j]:
                    cur = cost[i0 - 1][j - 1] - u[i0] - v[j]
                    if cur < minv[j]:
                        minv[j] = cur
                        way[j] = j0
                    if minv[j] < delta:
                        delta = minv[j]
                        j1 = j
            for j in range(size + 1):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    minv[j] -= delta
            j0 = j1
            if p[j0] == 0:
                break
        # Augmenting path
        while True:
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1
            if j0 == 0:
                break

    # Construct assignment
    assignment = [-1] * n
    for j in range(1, size + 1):
        if p[j] <= n and j <= m:
            assignment[p[j] - 1] = j - 1
    min_cost = -v[0]
    return (min_cost, assignment)

def fleet_rebalance(avs):
    """
    Computes the optimal rebalancing assignment for a fleet of AVs.
    Input: avs - a list of tuples [(current_location, desired_destination), ...]
    For each AV, any destination from the input list can be chosen.
    The cost from AV i to destination j is the shortest travel time from avs[i][0] to avs[j][1].
    Returns a tuple: (total_travel_time, assignment) where assignment is a dictionary mapping AV index
    to the index of the chosen destination from the input list.
    """
    k = len(avs)
    if k == 0:
        return (0, {})
    
    # Build the cost matrix.
    cost_matrix = []
    for i in range(k):
        src, _ = avs[i]
        row = []
        for j in range(k):
            _, dest = avs[j]
            cost = static_shortest(src, dest)
            row.append(cost)
        cost_matrix.append(row)

    min_cost, assignment_list = hungarian(cost_matrix)
    assignment = {}
    for i, j in enumerate(assignment_list):
        # Only add valid assignments, they are 0-indexed.
        assignment[i] = j
    return (min_cost, assignment)