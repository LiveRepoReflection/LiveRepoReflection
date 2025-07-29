import heapq
import math

def find_optimal_path(N, edges, start_node, end_node, latency_updates):
    """
    Finds the minimum latency path between start_node and end_node after each latency update.

    Args:
        N: The number of nodes in the network.
        edges: A list of tuples, where each tuple (u, v, w) represents a bidirectional communication channel between node u and node v with a latency of w.
        start_node: The starting node for pathfinding.
        end_node: The destination node for pathfinding.
        latency_updates: A list of tuples, where each tuple (u, v, new_latency) represents an update to the latency of the communication channel between node u and node v.

    Returns:
        A list of integers, where the i-th integer represents the minimum latency path length from start_node to end_node after applying the i-th latency update.
        If there is no path between start_node and end_node at any point after an update, returns -1 for that update.
    """
    # Build graph: list of lists. Each list element is a pair [neighbor, weight].
    graph = [[] for _ in range(N)]
    # Dictionary to quickly update edges.
    # key: (min(u, v), max(u, v)) -> list of references (u, index) in graph[u] for this channel.
    edge_index = {}

    def add_edge(u, v, w):
        # Add edge to graph from u to v and from v to u.
        graph[u].append([v, w])
        graph[v].append([u, w])
        key = (min(u, v), max(u, v))
        # Append the reference indices for both u and v.
        if key not in edge_index:
            edge_index[key] = []
        edge_index[key].append((u, len(graph[u]) - 1))
        edge_index[key].append((v, len(graph[v]) - 1))
    
    for (u, v, w) in edges:
        add_edge(u, v, w)
    
    def dijkstra():
        # Compute the shortest distance from start_node to end_node using Dijkstra's algorithm.
        dist = [math.inf] * N
        dist[start_node] = 0
        heap = [(0, start_node)]
        while heap:
            d, u = heapq.heappop(heap)
            if d != dist[u]:
                continue
            if u == end_node:
                break
            for v, w in graph[u]:
                nd = d + w
                if nd < dist[v]:
                    dist[v] = nd
                    heapq.heappush(heap, (nd, v))
        return dist[end_node] if dist[end_node] != math.inf else -1

    results = []
    # Process each update, update the graph then compute new shortest path.
    for (u, v, new_latency) in latency_updates:
        key = (min(u, v), max(u, v))
        if key in edge_index:
            # Update all edges matching this key.
            for (src, idx) in edge_index[key]:
                graph[src][idx][1] = new_latency
        else:
            # Edge does not exist; add it as a new edge.
            add_edge(u, v, new_latency)
        # After updating the graph, compute the optimal path.
        res = dijkstra()
        results.append(res)
    return results

if __name__ == "__main__":
    # Example usage:
    N = 4
    edges = [(0, 1, 5), (1, 2, 3), (0, 2, 10), (2, 3, 1)]
    start_node = 0
    end_node = 3
    latency_updates = [(1, 2, 2), (0, 1, 1), (0, 3, 15)]
    print(find_optimal_path(N, edges, start_node, end_node, latency_updates))