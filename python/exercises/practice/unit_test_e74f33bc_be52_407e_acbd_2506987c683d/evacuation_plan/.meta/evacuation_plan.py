from collections import deque
import math

def evacuation_time(n, roads, residents, safe_zones):
    # Create adjacency list representation of the graph
    adj = [[] for _ in range(n)]
    for u, v, capacity in roads:
        adj[u].append((v, capacity))
        adj[v].append((u, capacity))  # Undirected graph

    # Check if all non-safe locations can reach at least one safe zone
    visited = [False] * n
    queue = deque(safe_zones)
    for zone in safe_zones:
        visited[zone] = True
    
    while queue:
        u = queue.popleft()
        for (v, _) in adj[u]:
            if not visited[v]:
                visited[v] = True
                queue.append(v)
    
    # If any non-safe location with residents can't reach safe zone, return -1
    for i in range(n):
        if residents[i] > 0 and not visited[i]:
            return -1

    # Binary search for minimum evacuation time
    low = 0
    high = sum(residents)  # Upper bound
    answer = -1

    while low <= high:
        mid = (low + high) // 2
        if can_evacuate(n, adj, residents, safe_zones, mid):
            answer = mid
            high = mid - 1
        else:
            low = mid + 1

    return answer

def can_evacuate(n, adj, residents, safe_zones, time):
    if time == 0:
        return all(residents[i] == 0 or i in safe_zones for i in range(n))

    # Create flow network
    # We'll use the original graph with capacities scaled by time
    # and add a super source connected to all nodes with residents
    # and a super sink connected to all safe zones

    # Since we're using standard libraries only, we'll implement Ford-Fulkerson
    # with BFS (Edmonds-Karp algorithm)

    # Create a new graph with super source (n) and super sink (n+1)
    size = n + 2
    source = n
    sink = n + 1
    capacity = [[0] * size for _ in range(size)]

    # Connect source to nodes with residents
    for i in range(n):
        if residents[i] > 0:
            capacity[source][i] = residents[i]

    # Connect safe zones to sink with infinite capacity
    for zone in safe_zones:
        capacity[zone][sink] = math.inf

    # Add original edges with scaled capacities
    for u in range(n):
        for (v, cap) in adj[u]:
            capacity[u][v] += cap * time

    # Edmonds-Karp algorithm
    parent = [-1] * size
    max_flow = 0

    while True:
        # BFS to find augmenting path
        queue = deque()
        queue.append(source)
        parent = [-1] * size
        parent[source] = -2  # Mark source as visited
        found_path = False

        while queue and not found_path:
            u = queue.popleft()
            for v in range(size):
                if parent[v] == -1 and capacity[u][v] > 0:
                    parent[v] = u
                    if v == sink:
                        found_path = True
                        break
                    queue.append(v)

        if not found_path:
            break

        # Find minimum residual capacity along the path
        path_flow = math.inf
        v = sink
        while v != source:
            u = parent[v]
            path_flow = min(path_flow, capacity[u][v])
            v = u

        # Update residual capacities
        v = sink
        while v != source:
            u = parent[v]
            capacity[u][v] -= path_flow
            capacity[v][u] += path_flow
            v = u

        max_flow += path_flow

    # Check if all residents can be evacuated
    total_residents = sum(residents)
    return max_flow >= total_residents