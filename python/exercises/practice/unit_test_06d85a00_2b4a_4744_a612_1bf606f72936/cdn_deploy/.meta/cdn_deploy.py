from collections import deque
import math

def bfs(start, n, adj):
    dist = [math.inf] * n
    dist[start] = 0
    q = deque()
    q.append(start)
    while q:
        cur = q.popleft()
        for neigh in adj[cur]:
            if dist[neigh] == math.inf:
                dist[neigh] = dist[cur] + 1
                q.append(neigh)
    return dist

def compute_all_pairs_shortest(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    all_dist = []
    for i in range(n):
        all_dist.append(bfs(i, n, adj))
    return all_dist

def evaluate_subset(facilities, all_dist, populations, D, L):
    n = len(populations)
    cost = 0
    # cost for facility deployments
    cost += len(facilities) * D
    # cost for latency in non-facility nodes
    for v in range(n):
        if v in facilities:
            continue
        min_d = math.inf
        for u in facilities:
            if all_dist[u][v] < min_d:
                min_d = all_dist[u][v]
        # if unreachable (should not happen in connected graph) then continue
        cost += L * populations[v] * min_d
    return cost

def brute_force_solution(n, edges, populations, D, L, all_dist):
    best = math.inf
    # iterate over all non-empty subsets of nodes (bitmask enumeration)
    # Only feasible if n is small.
    for mask in range(1, 1 << n):
        facilities = set()
        for i in range(n):
            if mask & (1 << i):
                facilities.add(i)
        cost = evaluate_subset(facilities, all_dist, populations, D, L)
        if cost < best:
            best = cost
    return best

def greedy_solution(n, edges, populations, D, L, all_dist):
    # Greedy heuristic for large n.
    # Start with the single best facility (minimizing total cost when only that facility is opened)
    best_cost = math.inf
    best_facility = None
    for i in range(n):
        current_set = {i}
        cost = evaluate_subset(current_set, all_dist, populations, D, L)
        if cost < best_cost:
            best_cost = cost
            best_facility = i
    facilities = {best_facility}
    current_cost = best_cost

    # Precompute current assignment cost for each node (latency cost if not a facility)
    assign = [math.inf] * n
    for v in range(n):
        if v in facilities:
            assign[v] = 0
        else:
            # distance from v to the facility in facilities
            d = min(all_dist[u][v] for u in facilities)
            assign[v] = L * populations[v] * d

    improved = True
    while improved:
        improved = False
        # Try adding a new facility that is not already in facilities
        best_delta = 0
        best_candidate = None
        for i in range(n):
            if i in facilities:
                continue
            # Cost if we add i as facility:
            new_assign = assign[:]
            delta = 0
            # For candidate facility, its own cost becomes 0 instead of current assign (which might be >0)
            delta += - new_assign[i]
            for v in range(n):
                if v in facilities or v == i:
                    continue
                # New latency cost if served by i
                d = all_dist[i][v]
                new_cost = L * populations[v] * d
                if new_cost < new_assign[v]:
                    delta += (new_cost - new_assign[v])
            # Also add deployment cost D for new facility
            delta += D
            if delta < best_delta:
                best_delta = delta
                best_candidate = i
        if best_candidate is not None:
            facilities.add(best_candidate)
            # update assignment costs
            for v in range(n):
                if v in facilities:
                    assign[v] = 0
                else:
                    new_cost = L * populations[v] * all_dist[best_candidate][v]
                    if new_cost < assign[v]:
                        assign[v] = new_cost
            current_cost += best_delta
            improved = True

    return current_cost

def min_cost(n, m, edges, populations, D, L):
    all_dist = compute_all_pairs_shortest(n, edges)
    # Use brute force if n is small enough, otherwise use greedy heuristic.
    if n <= 15:
        return brute_force_solution(n, edges, populations, D, L, all_dist)
    else:
        return greedy_solution(n, edges, populations, D, L, all_dist)