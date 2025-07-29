import heapq
import math

def compute_risk_paths(n, edges, sources, target, updates):
    # Build the graph and maintain a mapping for edge weights.
    graph = {i: [] for i in range(n)}
    edge_weights = {}
    for u, v, w in edges:
        graph[u].append(v)
        edge_weights[(u, v)] = w

    def dijkstra():
        dist = [math.inf] * n
        pq = []
        # Multi-source initialization.
        for src in sources:
            dist[src] = 0.0
            heapq.heappush(pq, (0.0, src))
        
        while pq:
            d, node = heapq.heappop(pq)
            if d != dist[node]:
                continue
            if node == target:
                # Since we need complete shortest path computation because updates affect entire graph,
                # we do not break immediately when target is reached.
                pass
            for nei in graph[node]:
                new_d = d + edge_weights[(node, nei)]
                if new_d < dist[nei]:
                    dist[nei] = new_d
                    heapq.heappush(pq, (new_d, nei))
        return dist[target]

    results = []
    for update in updates:
        # Unpack the update details.
        time, u, v, risk_increase = update
        # Apply the risk update. Updates are cumulative.
        edge_weights[(u, v)] += risk_increase
        # Recompute the shortest path from any source to the target.
        sp = dijkstra()
        results.append(sp)
    return results