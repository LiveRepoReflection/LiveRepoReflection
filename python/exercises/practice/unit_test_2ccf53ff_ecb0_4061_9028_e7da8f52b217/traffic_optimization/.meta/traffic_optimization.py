def optimize_traffic_lights(n, roads, budget, delay):
    INF = float('inf')
    # Initialize the distance matrix with INF, and 0 for diagonal elements
    dist = [[INF] * n for _ in range(n)]
    for i in range(n):
        dist[i][i] = 0

    # Set the road distances
    for u, v, w in roads:
        if w < dist[u][v]:
            dist[u][v] = w
            dist[v][u] = w

    # Compute all pairs shortest path using Floyd-Warshall algorithm
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]

    # Since installing a traffic light only adds extra delay for any vertex it touches,
    # and we are allowed to install at most 'budget' lights (or even none),
    # the optimal solution with delay > 0 is to not install any lights at all.
    # Therefore, the minimized average travel time is simply the average of the shortest paths.
    total = 0
    count = 0
    for i in range(n):
        for j in range(n):
            if i != j:
                total += dist[i][j]
                count += 1

    avg = total / count if count else 0.0
    return round(avg, 6)

if __name__ == "__main__":
    # Sample run for testing manually
    n = 3
    roads = [(0, 1, 10), (1, 2, 10), (0, 2, 15)]
    budget = 1
    delay = 5
    print(optimize_traffic_lights(n, roads, budget, delay))