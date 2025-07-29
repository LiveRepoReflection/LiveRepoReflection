import heapq
import math

def dynamic_router(N, initial_links, operations):
    # Build the initial graph representation.
    # Using a dictionary for each node that maps neighbor -> latency.
    graph = {i: {} for i in range(N)}
    for u, v, l in initial_links:
        graph[u][v] = l
        graph[v][u] = l

    results = []

    # Process each operation sequentially.
    for op in operations:
        # Identify query operations by checking if the first element is a set.
        if isinstance(op[0], set):
            # Unpack query operation: (S, D)
            S, D = op

            # Run Dijkstra's algorithm from destination D.
            distances = [math.inf] * N
            distances[D] = 0
            heap = [(0, D)]
            # To optimize early stopping, track the number of sources found.
            found = {}
            while heap:
                current_distance, node = heapq.heappop(heap)
                if current_distance > distances[node]:
                    continue

                # If all source nodes have been updated to their shortest distances, optionally break early.
                # However, since S can be arbitrary and the graph is dynamic, we complete the Dijkstra expansion.
                for neighbor, weight in graph[node].items():
                    new_distance = current_distance + weight
                    if new_distance < distances[neighbor]:
                        distances[neighbor] = new_distance
                        heapq.heappush(heap, (new_distance, neighbor))
            # Determine the minimum latency from any source in S to the destination D.
            best_distance = min((distances[s] for s in S), default=math.inf)
            if best_distance == math.inf:
                results.append(-1)
            else:
                results.append(best_distance)
        else:
            # Interpret the operation as a latency update: (U, V, L).
            U, V, L = op
            # Update the bidirectional edge in the graph.
            graph[U][V] = L
            graph[V][U] = L

    return results