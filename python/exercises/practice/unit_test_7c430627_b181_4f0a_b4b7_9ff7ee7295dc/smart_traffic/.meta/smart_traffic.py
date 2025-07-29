import heapq
from collections import defaultdict

class SmartTrafficRouter:
    def __init__(self, edges):
        self.edges = edges
        self.graph = self._build_graph(edges)
        self.edge_indices = {(u, v): i for i, (u, v, _, _) in enumerate(edges)}

    def _build_graph(self, edges):
        graph = defaultdict(list)
        for u, v, length, traffic in edges:
            graph[u].append((v, length, traffic))
        return graph

    def update_traffic(self, edge_index, new_traffic_volume):
        if edge_index < 0 or edge_index >= len(self.edges):
            raise IndexError("Edge index out of range")
        u, v, length, _ = self.edges[edge_index]
        self.edges[edge_index] = (u, v, length, new_traffic_volume)
        
        # Update the graph representation
        for i, (neighbor, l, t) in enumerate(self.graph[u]):
            if neighbor == v:
                self.graph[u][i] = (v, l, new_traffic_volume)
                break

    def _dijkstra(self, start, end, cost_function):
        heap = [(0, start, [])]
        visited = set()
        while heap:
            current_cost, node, path = heapq.heappop(heap)
            if node in visited:
                continue
            visited.add(node)
            path = path + [node]
            if node == end:
                return path
            for neighbor, length, traffic in self.graph.get(node, []):
                if neighbor not in visited:
                    new_cost = current_cost + cost_function(length, traffic)
                    heapq.heappush(heap, (new_cost, neighbor, path))
        return []

    def _get_cost_function(self, preference):
        if preference == "shortest":
            return lambda length, traffic: length
        elif preference == "least_congestion":
            return lambda length, traffic: traffic
        elif preference == "balanced":
            return lambda length, traffic: length + 0.1 * traffic
        else:
            raise ValueError("Invalid preference")

    def process_requests(self, requests):
        results = []
        for start, end, preference in requests:
            if start == end:
                results.append([start])
                continue
            cost_function = self._get_cost_function(preference)
            path = self._dijkstra(start, end, cost_function)
            results.append(path)
        return results