import heapq

def find_shortest_paths(N, edges, sources):
    # Build graph as a dictionary mapping each node to a list of outgoing edges.
    # Each edge is represented as (v, time_costs) where time_costs is a list of (t, c) pairs.
    graph = {i: [] for i in range(N)}
    for u, v, time_costs in edges:
        graph[u].append((v, time_costs))
        
    # best[node] will store a list of (arrival_time, cumulative_cost) pairs for reachable states at node.
    best = {i: [] for i in range(N)}
    
    # Priority queue stores states as (cumulative_cost, arrival_time, node)
    pq = []
    for s in sources:
        # Each source starts at time 0 with cost 0.
        best[s].append((0, 0))
        heapq.heappush(pq, (0, 0, s))
    
    # Function to check if a new state (arrival, cost) is dominated by any state in lst.
    # A state (a, c) in lst dominates (arrival, cost) if c <= cost and a <= arrival.
    def is_dominated(lst, arrival, cost):
        for a, c in lst:
            if c <= cost and a <= arrival:
                return True
        return False

    # Update the state list for a node by removing any states that are dominated by (arrival, cost)
    def add_state(lst, arrival, cost):
        new_list = []
        for a, c in lst:
            if not (cost <= c and arrival <= a):
                new_list.append((a, c))
        new_list.append((arrival, cost))
        return new_list

    while pq:
        cum_cost, arrival, u = heapq.heappop(pq)
        # Skip this state if there is already a strictly better state recorded for u.
        skip = False
        for a, c in best[u]:
            if c < cum_cost and a <= arrival:
                skip = True
                break
        if skip:
            continue
        
        # Explore outgoing edges from node u.
        for v, time_costs in graph[u]:
            T = arrival
            candidates = []
            # Immediate candidate: if arrival time T is greater than or equal to a threshold,
            # you can start at T using the cost corresponding to the largest threshold not exceeding T.
            idx = -1
            for i, (t, c) in enumerate(time_costs):
                if t <= T:
                    idx = i
                else:
                    break
            if idx != -1:
                t_val, c_val = time_costs[idx]
                new_cost = cum_cost + c_val
                new_arrival = T + c_val
                candidates.append((new_arrival, new_cost))
            # For thresholds with t > T, you can choose to wait until t.
            for t, c in time_costs:
                if t > T:
                    new_cost = cum_cost + c
                    new_arrival = t + c
                    candidates.append((new_arrival, new_cost))
                    
            # Process all candidate transitions for edge (u, v).
            for new_arrival, new_cost in candidates:
                if is_dominated(best[v], new_arrival, new_cost):
                    continue
                best[v] = add_state(best[v], new_arrival, new_cost)
                heapq.heappush(pq, (new_cost, new_arrival, v))
    
    # For each node, select the minimum cumulative cost among all states.
    result = []
    for i in range(N):
        if best[i]:
            min_cost = min(c for a, c in best[i])
            result.append(min_cost)
        else:
            result.append(-1)
    return result

if __name__ == "__main__":
    # Example run
    N = 4
    edges = [
        (0, 1, [(0, 10), (5, 20)]),
        (0, 2, [(2, 5), (7, 15)]),
        (1, 3, [(1, 30)])
    ]
    sources = [0]
    print(find_shortest_paths(N, edges, sources))