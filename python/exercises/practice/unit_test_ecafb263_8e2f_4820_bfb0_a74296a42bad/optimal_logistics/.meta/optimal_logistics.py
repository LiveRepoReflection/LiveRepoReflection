import heapq
import math
from collections import defaultdict

def dijkstra(adj, start, n):
    dist = [math.inf] * n
    dist[start] = 0
    heap = [(0, start)]
    while heap:
        d, u = heapq.heappop(heap)
        if d != dist[u]:
            continue
        for v, w in adj[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(heap, (nd, v))
    return dist

def build_distance_matrix(n, graph_adj):
    # n: total nodes count (0..n-1)
    dist_matrix = []
    for i in range(n):
        d = dijkstra(graph_adj, i, n)
        dist_matrix.append(d)
    return dist_matrix

def route_feasible(mask, dist, deadlines, T):
    # mask: bitmask over customers indices 0..(N-1)
    # dist: matrix with indices: 0 is warehouse, customers are 1..N. So customer i corresponds to index i+1.
    # deadlines: list of deadlines for customers, index 0 corresponds to customer 0 (node 1).
    # T: maximum travel time for the route.
    # Using DP: dp[state][j] = minimal arrival time finishing at customer j.
    N = len(deadlines)
    dp = {}
    # initialize for each customer in the mask (single element subset)
    for j in range(N):
        if mask & (1 << j):
            time_to_j = dist[0][j+1]
            if time_to_j <= deadlines[j]:
                dp[(1 << j, j)] = time_to_j
    full_mask = mask
    # iterate over states
    for state in range(1, 1 << N):
        # only consider states that are subset of mask
        if state & ~mask:
            continue
        for j in range(N):
            if not (state & (1 << j)):
                continue
            if (state, j) not in dp:
                continue
            current_time = dp[(state, j)]
            # try to add a new customer k not in state but in mask
            remain = mask ^ state
            k = 0
            while remain:
                if remain & 1:
                    new_time = current_time + dist[j+1][k+1]
                    if new_time <= deadlines[k]:
                        new_state = state | (1 << k)
                        key = (new_state, k)
                        if new_state == mask and new_time <= T:
                            return True
                        if key not in dp or new_time < dp[key]:
                            dp[key] = new_time
                remain >>= 1
                k += 1
    # Also check for single element states if they already satisfy T (should be caught in initialization)
    for key, t in dp.items():
        state, _ = key
        if state == mask and t <= T:
            return True
    return False

def min_vehicles(N, K, graph, D, V, T, C, vehicle_types):
    # N: number of customer zones, customers are nodes 1..N, warehouse is node 0.
    # Build available vehicles count by type.
    avail = defaultdict(int)
    for vt in vehicle_types:
        avail[vt] += 1

    # Distinct vehicle types that we have available.
    vehicle_types_set = set(avail.keys())

    total_nodes = N + 1  # nodes: 0 is warehouse, 1..N are customers
    # Build road networks for each distinct vehicle type.
    dist_matrices = {}
    for vt in vehicle_types_set:
        # Build restricted graph: nodes 0..N
        adj = [[] for _ in range(total_nodes)]
        for u, v, w, types in graph:
            if vt in types:
                # Add edge from u to v if within range.
                if u < total_nodes and v < total_nodes:
                    adj[u].append((v, w))
        # Compute distance matrix for this vehicle type.
        dist_matrix = build_distance_matrix(total_nodes, adj)
        dist_matrices[vt] = dist_matrix

    # Precompute volume sum for every mask of customers (0-indexed, corresponds to node i+1)
    vol_sum = {}
    for mask in range(1, 1 << N):
        s = 0
        for i in range(N):
            if mask & (1 << i):
                s += V[i]
        vol_sum[mask] = s

    # For each vehicle type, precompute the feasible groups (mask over customers) that can be delivered by one vehicle of that type.
    feasible_groups = defaultdict(list)
    for vt in vehicle_types_set:
        dist_matrix = dist_matrices[vt]
        for mask in range(1, 1 << N):
            if vol_sum[mask] > C:
                continue
            # Check if route exists with deadlines D and total travel time T.
            if route_feasible(mask, dist_matrix, D, T):
                feasible_groups[vt].append(mask)
        # Sort groups by number of customers descending to try larger groups first.
        feasible_groups[vt].sort(key=lambda m: -bin(m).count("1"))

    # For recursion, use memoization keyed by (mask, avail_state) where avail_state is tuple of remaining vehicles for each type sorted by type.
    from functools import lru_cache

    types_sorted = sorted(avail.keys())
    def avail_to_tuple(avail_dict):
        return tuple(avail_dict[vt] for vt in types_sorted)

    @lru_cache(maxsize=None)
    def search(mask, avail_tuple):
        # mask: bitmask of customers remaining to be delivered.
        if mask == 0:
            return 0
        best = math.inf
        avail_list = list(avail_tuple)
        # Try each vehicle type if available.
        for idx, vt in enumerate(types_sorted):
            if avail_list[idx] == 0:
                continue
            # For each feasible group for this vehicle type that is a subset of mask:
            for group in feasible_groups[vt]:
                if group & mask == group:
                    new_mask = mask ^ group
                    avail_list[idx] -= 1
                    new_avail = tuple(avail_list)
                    res = search(new_mask, new_avail)
                    if res != math.inf:
                        best = min(best, 1 + res)
                    avail_list[idx] += 1
        return best

    full_mask = (1 << N) - 1
    result = search(full_mask, avail_to_tuple(avail))
    if result == math.inf or result > K:
        return -1
    return result