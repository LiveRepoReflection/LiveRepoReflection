import heapq
from collections import defaultdict

class SmartRideOptimizer:
    def __init__(self, graph):
        self.graph = graph
        self.traffic_cache = {}

    def get_traffic_cost(self, u, v, timestamp):
        cache_key = (min(u, v), max(u, v), timestamp)
        if cache_key not in self.traffic_cache:
            base_cost = abs(u - v)
            time_penalty = (timestamp % 24)
            self.traffic_cache[cache_key] = base_cost + time_penalty
        return self.traffic_cache[cache_key]

    def find_best_routes(self, request):
        start = request['start_intersection']
        end = request['end_intersection']
        timestamp = request['departure_time']
        k = request['k']

        if start not in self.graph:
            raise ValueError(f"Start intersection {start} not found in graph")
        if end not in self.graph:
            raise ValueError(f"End intersection {end} not found in graph")
        if start == end:
            return [{'route': [start], 'cost': 0}]

        heap = []
        heapq.heappush(heap, (0, [start]))
        visited = defaultdict(int)
        results = []

        while heap and len(results) < k:
            current_cost, current_path = heapq.heappop(heap)
            last_node = current_path[-1]

            if last_node == end:
                results.append({'route': current_path, 'cost': current_cost})
                continue

            if visited[last_node] >= k:
                continue
            visited[last_node] += 1

            for neighbor, _ in self.graph[last_node]:
                if neighbor in current_path:
                    continue

                new_path = current_path.copy()
                new_path.append(neighbor)
                edge_cost = self.get_traffic_cost(last_node, neighbor, timestamp)
                new_cost = current_cost + edge_cost
                heapq.heappush(heap, (new_cost, new_path))

        return results