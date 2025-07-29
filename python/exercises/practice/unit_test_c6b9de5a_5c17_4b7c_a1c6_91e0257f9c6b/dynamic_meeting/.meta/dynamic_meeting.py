import math

def optimal_meeting_point(n, edges, group, updates):
    # Initialize distance matrix
    dist = [[math.inf] * n for _ in range(n)]
    for i in range(n):
        dist[i][i] = 0

    for u, v, w in edges:
        # If multiple roads exist, choose the smallest weight.
        if w > 0:
            dist[u][v] = min(dist[u][v], w)
            dist[v][u] = min(dist[v][u], w)
        else:
            # If weight is 0, it means road is closed
            dist[u][v] = math.inf
            dist[v][u] = math.inf

    result = []

    # Define function to run Floyd Warshall algorithm
    def floyd_warshall(matrix):
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if matrix[i][k] + matrix[k][j] < matrix[i][j]:
                        matrix[i][j] = matrix[i][k] + matrix[k][j]

    # Process each update sequentially
    for upd in updates:
        u, v, new_w = upd
        # Update the graph: if new_w is 0, road is closed.
        if new_w > 0:
            dist[u][v] = new_w
            dist[v][u] = new_w
        else:
            dist[u][v] = math.inf
            dist[v][u] = math.inf

        # Create a copy of the current distances to run Floyd Warshall.
        # We make a fresh copy because Floyd Warshall updates matrix in-place.
        fw_matrix = [row[:] for row in dist]
        floyd_warshall(fw_matrix)

        best_node = -1
        best_max_time = math.inf

        # For each candidate node in the graph, check if all group members can reach it
        for candidate in range(n):
            max_time = 0
            valid = True
            for g in group:
                if fw_matrix[g][candidate] == math.inf:
                    valid = False
                    break
                # Track the furthest travel time from group member to candidate
                if fw_matrix[g][candidate] > max_time:
                    max_time = fw_matrix[g][candidate]
            if valid:
                if max_time < best_max_time:
                    best_max_time = max_time
                    best_node = candidate
                elif max_time == best_max_time and candidate < best_node:
                    best_node = candidate

        result.append(best_node)
    return result

if __name__ == '__main__':
    # Sample run (optional)
    n = 5
    edges = [(0, 1, 5), (0, 2, 2), (1, 2, 1), (1, 3, 4), (2, 4, 8), (3,4,3)]
    group = [0, 3]
    updates = [(1, 2, 5), (0, 1, 1)]
    output = optimal_meeting_point(n, edges, group, updates)
    print(output)