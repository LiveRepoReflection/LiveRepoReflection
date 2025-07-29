from collections import defaultdict
import heapq
from typing import List, Tuple, Set, Dict

class AdaptiveRouter:
    def __init__(self, n: int, edges: List[Tuple[int, int, int]]):
        """Initialize the adaptive router with n nodes and initial edges."""
        self.n = n
        self.graph = defaultdict(dict)
        self.failed_nodes: Set[int] = set()
        
        # Initialize the graph with given edges
        for u, v, w in edges:
            self.graph[u][v] = w
            self.graph[v][u] = w  # Bidirectional edges

    def edge_update(self, u: int, v: int, w: int) -> None:
        """Update edge weight between nodes u and v. If w is -1, remove the edge."""
        if w == -1:
            # Remove edge if it exists
            self.graph[u].pop(v, None)
            self.graph[v].pop(u, None)
        else:
            # Add or update edge
            self.graph[u][v] = w
            self.graph[v][u] = w

    def node_failure(self, x: int) -> None:
        """Mark node x as failed and remove all its edges."""
        self.failed_nodes.add(x)
        # Remove all edges connected to the failed node
        if x in self.graph:
            neighbors = list(self.graph[x].keys())
            for neighbor in neighbors:
                self.graph[neighbor].pop(x, None)
            self.graph.pop(x)

    def route(self, s: int, d: int) -> int:
        """Find the shortest path from source s to destination d."""
        # Check if either source or destination has failed
        if s in self.failed_nodes or d in self.failed_nodes:
            return -1

        # Initialize distance dictionary and priority queue
        distances: Dict[int, int] = {s: 0}
        pq = [(0, s)]  # (distance, node)
        visited: Set[int] = set()

        while pq:
            curr_dist, curr_node = heapq.heappop(pq)

            # If we've reached the destination, return the distance
            if curr_node == d:
                return curr_dist

            # Skip if we've already processed this node
            if curr_node in visited:
                continue

            visited.add(curr_node)

            # Process all neighbors
            for neighbor, weight in self.graph[curr_node].items():
                if neighbor in self.failed_nodes or neighbor in visited:
                    continue

                distance = curr_dist + weight

                # Update distance if it's shorter
                if neighbor not in distances or distance < distances[neighbor]:
                    distances[neighbor] = distance
                    heapq.heappush(pq, (distance, neighbor))

        # If we can't reach the destination
        return -1

    def _validate_node(self, node: int) -> bool:
        """Validate if a node is within bounds and not failed."""
        return 0 <= node < self.n and node not in self.failed_nodes

    def _validate_weight(self, weight: int) -> bool:
        """Validate if a weight is within the acceptable range."""
        return -1 <= weight <= 1000
