from collections import deque

def max_resource_transport(num_planets, wormholes, source, destination, timeframe):
    # Create residual graph
    residual_graph = [[0] * num_planets for _ in range(num_planets)]
    for u, v, capacity in wormholes:
        residual_graph[u][v] += capacity

    parent = [-1] * num_planets
    max_flow = 0

    # Edmonds-Karp algorithm implementation
    def bfs():
        visited = [False] * num_planets
        queue = deque()
        queue.append(source)
        visited[source] = True

        while queue:
            u = queue.popleft()
            for v in range(num_planets):
                if not visited[v] and residual_graph[u][v] > 0:
                    queue.append(v)
                    visited[v] = True
                    parent[v] = u
                    if v == destination:
                        return True
        return False

    while bfs():
        path_flow = float('inf')
        v = destination
        while v != source:
            u = parent[v]
            path_flow = min(path_flow, residual_graph[u][v])
            v = u

        v = destination
        while v != source:
            u = parent[v]
            residual_graph[u][v] -= path_flow
            residual_graph[v][u] += path_flow
            v = u

        max_flow += path_flow

    return max_flow * timeframe