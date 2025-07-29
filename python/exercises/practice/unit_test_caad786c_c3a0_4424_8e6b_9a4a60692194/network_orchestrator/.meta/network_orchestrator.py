import heapq
from collections import defaultdict

class NetworkOrchestrator:
    def __init__(self, n):
        self.n = n
        self.adjacency = defaultdict(set)
        
    def connect(self, node1, node2):
        if node1 == node2:
            return
        self.adjacency[node1].add(node2)
        self.adjacency[node2].add(node1)
        
    def disconnect(self, node1, node2):
        if node1 == node2:
            return
        self.adjacency[node1].discard(node2)
        self.adjacency[node2].discard(node1)
        
    def sendMessage(self, source, destination, message):
        if source == destination:
            return True
            
        visited = set()
        heap = []
        heapq.heappush(heap, (0, source, [source]))
        
        while heap:
            current_cost, current_node, path = heapq.heappop(heap)
            
            if current_node == destination:
                return True
                
            if current_node in visited:
                continue
                
            visited.add(current_node)
            
            for neighbor in self.adjacency[current_node]:
                if neighbor not in visited:
                    new_path = path + [neighbor]
                    heapq.heappush(heap, (current_cost + 1, neighbor, new_path))
                    
        return False