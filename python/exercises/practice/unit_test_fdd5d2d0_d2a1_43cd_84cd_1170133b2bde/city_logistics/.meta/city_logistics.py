import heapq

class LogisticsNetwork:
    def __init__(self):
        # Graph is stored as a dict: key is source city, value is list of edges (dest, time, cost)
        self.graph = {}

    def add_edge(self, src, dest, time, cost):
        if src not in self.graph:
            self.graph[src] = []
        self.graph[src].append((dest, time, cost))
        # Ensure destination node exists in graph structure, even if it has no outgoing edges
        if dest not in self.graph:
            self.graph[dest] = []

    def update_edge(self, src, dest, time, cost):
        # Update the first matching edge from src to dest with new time and cost.
        if src in self.graph:
            for i, edge in enumerate(self.graph[src]):
                if edge[0] == dest:
                    self.graph[src][i] = (dest, time, cost)
                    break

    def process_request(self, src, dest, package_size, deadline):
        # Use a modified Dijkstra to find the path with the minimum total cost while keeping time <= deadline.
        # Each edge weight is given by: edge_cost + package_size * edge_time.
        # State is (total_cost, total_time, current_node, path)
        # We use a priority queue ordered by total_cost.
        heap = []
        heapq.heappush(heap, (0, 0, src, [src]))
        
        # For pruning, maintain best known (time, cost) tuples for each node.
        best = {node: [] for node in self.graph}
        best[src].append((0, 0))
        
        while heap:
            total_cost, total_time, current, path = heapq.heappop(heap)
            # If we reach the destination and the time constraint is satisfied, return the result.
            if current == dest and total_time <= deadline:
                return (path, total_cost)
            
            if current not in self.graph:
                continue
            
            for neighbor, edge_time, edge_cost in self.graph[current]:
                new_time = total_time + edge_time
                if new_time > deadline:
                    continue
                new_cost = total_cost + edge_cost + package_size * edge_time
                new_path = path + [neighbor]
                # Prune states: If we have reached neighbor with less time and lower cost, skip this state.
                dominated = False
                for t, c in best[neighbor]:
                    if t <= new_time and c <= new_cost:
                        dominated = True
                        break
                if dominated:
                    continue
                # Otherwise, record new_state in best list and push state into heap.
                best[neighbor].append((new_time, new_cost))
                heapq.heappush(heap, (new_cost, new_time, neighbor, new_path))
        return None