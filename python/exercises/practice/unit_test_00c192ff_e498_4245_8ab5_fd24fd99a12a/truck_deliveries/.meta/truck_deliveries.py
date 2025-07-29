import math

def plan_deliveries(num_cities, roads, trucks, requests):
    # Build graph and compute all-pairs shortest paths with route reconstruction.
    # Cities are numbered 1..num_cities.
    INF = math.inf
    # Initialize distance and next matrices.
    dist = [[INF] * (num_cities + 1) for _ in range(num_cities + 1)]
    nxt = [[None] * (num_cities + 1) for _ in range(num_cities + 1)]
    
    for i in range(1, num_cities + 1):
        dist[i][i] = 0
        nxt[i][i] = i
        
    for u, v, t in roads:
        if t < dist[u][v]:
            dist[u][v] = t
            nxt[u][v] = v

    # Floyd Warshall
    for k in range(1, num_cities + 1):
        for i in range(1, num_cities + 1):
            for j in range(1, num_cities + 1):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    nxt[i][j] = nxt[i][k]
    
    # Function to reconstruct route from u to v.
    def reconstruct_path(u, v):
        if nxt[u][v] is None:
            return []
        path = [u]
        while u != v:
            u = nxt[u][v]
            path.append(u)
        return path

    # Precompute feasibility and cost for each truck-request pair.
    # trucks: list of (start_city, capacity)
    # requests: list of (destination, (start_time, end_time), weight)
    num_trucks = len(trucks)
    num_requests = len(requests)
    
    # cost_matrix[i][j] is travel time from truck i's start to request j destination if feasible.
    cost_matrix = [[INF] * num_requests for _ in range(num_trucks)]
    for i, (start_city, cap) in enumerate(trucks):
        for j, (dest, time_window, weight) in enumerate(requests):
            if cap >= weight and dist[start_city][dest] != INF:
                # Feasible: waiting allowed means truck can always depart at an appropriate time.
                cost_matrix[i][j] = dist[start_city][dest]
            # Else cost remains INF.

    # Use recursion to assign trucks to requests maximizing fulfilled count and then minimizing total travel time.
    best_solution = {"count": 0, "cost": math.inf, "assignment": [None] * num_trucks}

    def rec(truck_index, used, count, total_cost, assignment):
        if truck_index == num_trucks:
            # Check if this solution is better.
            if count > best_solution["count"] or (count == best_solution["count"] and total_cost < best_solution["cost"]):
                best_solution["count"] = count
                best_solution["cost"] = total_cost
                best_solution["assignment"] = assignment.copy()
            return
        
        # Option 1: Do not assign truck truck_index.
        assignment.append(None)
        rec(truck_index + 1, used, count, total_cost, assignment)
        assignment.pop()
        
        # Option 2: Try all possible requests for this truck.
        for req in range(num_requests):
            if req in used:
                continue
            if cost_matrix[truck_index][req] == INF:
                continue
            # Feasible assignment.
            assignment.append(req)
            used.add(req)
            rec(truck_index + 1, used, count + 1, total_cost + cost_matrix[truck_index][req], assignment)
            used.remove(req)
            assignment.pop()
    
    rec(0, set(), 0, 0, [])
    
    # If no deliveries can be fulfilled, return as specified.
    if best_solution["count"] == 0:
        return (-1, [], [])
    
    total_time = best_solution["cost"]
    assignment = best_solution["assignment"]
    fulfilled = []
    assignments = []
    
    # Build assignments details based on truck indices.
    for truck_idx, req_idx in enumerate(assignment):
        if req_idx is not None:
            fulfilled.append(req_idx)
            # For each assigned truck, start time is the start_time of the request window.
            dest, time_window, weight = requests[req_idx]
            start_time = time_window[0]
            truck_start = trucks[truck_idx][0]
            route = reconstruct_path(truck_start, dest)
            assignments.append({
                "truck": truck_idx,
                "request": req_idx,
                "start_time": start_time,
                "route": route
            })
    
    return (total_time, fulfilled, assignments)

if __name__ == '__main__':
    # For simple manual testing
    num_cities = 2
    roads = [(1, 2, 5)]
    trucks = [(1, 10)]
    requests = [
        (2, (0, 10), 5)
    ]
    result = plan_deliveries(num_cities, roads, trucks, requests)
    print(result)