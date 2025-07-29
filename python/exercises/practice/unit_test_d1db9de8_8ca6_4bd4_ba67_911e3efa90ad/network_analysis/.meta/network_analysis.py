from collections import defaultdict, deque
import heapq

class SocialNetwork:
    def __init__(self, n):
        """
        Initialize a social network with n users numbered from 0 to n-1.
        
        Args:
            n: Number of users in the network
        """
        self.n = n
        self.graph = defaultdict(set)
        self.parent = list(range(n))  # For Union-Find
        self.rank = [0] * n  # For Union-Find by rank
        self.size = [1] * n  # Size of each component
        self._largest_component_cache = 1  # Cache for the largest component size
        self._components_changed = False  # Flag to indicate if components have changed
    
    def _find(self, x):
        """
        Find the parent of user x with path compression.
        
        Args:
            x: User ID
            
        Returns:
            Parent of user x
        """
        if self.parent[x] != x:
            self.parent[x] = self._find(self.parent[x])
        return self.parent[x]
    
    def _union(self, x, y):
        """
        Union two users by rank.
        
        Args:
            x: First user ID
            y: Second user ID
            
        Returns:
            True if users were not already connected, False otherwise
        """
        root_x = self._find(x)
        root_y = self._find(y)
        
        if root_x == root_y:
            return False  # Already connected
        
        # Union by rank
        if self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
            self.size[root_y] += self.size[root_x]
            new_size = self.size[root_y]
        else:
            self.parent[root_y] = root_x
            self.size[root_x] += self.size[root_y]
            new_size = self.size[root_x]
            if self.rank[root_x] == self.rank[root_y]:
                self.rank[root_x] += 1
        
        # Update largest component size cache
        self._largest_component_cache = max(self._largest_component_cache, new_size)
        self._components_changed = True
        return True
    
    def connect(self, user1, user2):
        """
        Establish a friendship between user1 and user2.
        
        Args:
            user1: First user ID
            user2: Second user ID
        """
        # Add edges to the graph
        self.graph[user1].add(user2)
        self.graph[user2].add(user1)
        
        # Union the users in the Union-Find structure
        self._union(user1, user2)
    
    def are_connected(self, user1, user2):
        """
        Check if user1 and user2 are connected.
        
        Args:
            user1: First user ID
            user2: Second user ID
            
        Returns:
            True if users are connected, False otherwise
        """
        # Use Union-Find to check connectivity
        return self._find(user1) == self._find(user2)
    
    def largest_component_size(self):
        """
        Get the size of the largest connected component.
        
        Returns:
            Size of the largest connected component
        """
        if not self._components_changed:
            return self._largest_component_cache
        
        # If components have changed since last calculation, recalculate
        max_size = max(self.size[self._find(i)] for i in range(self.n))
        self._largest_component_cache = max_size
        self._components_changed = False
        return max_size
    
    def min_connections_to_separate(self, user1, user2):
        """
        Determine the minimum number of connections that need to be broken
        to separate user1 and user2.
        
        Args:
            user1: First user ID
            user2: Second user ID
            
        Returns:
            Minimum number of connections to break, or 0 if not connected
        """
        # If users are not connected, return 0
        if not self.are_connected(user1, user2):
            return 0
        
        # Use max-flow algorithm (Ford-Fulkerson with Edmonds-Karp)
        # to find the minimum cut between user1 and user2
        return self._edmonds_karp(user1, user2)
    
    def _edmonds_karp(self, source, sink):
        """
        Edmonds-Karp algorithm to find the max flow / min cut.
        
        Args:
            source: Source node
            sink: Sink node
            
        Returns:
            Maximum flow from source to sink
        """
        # Create a residual graph
        residual_graph = defaultdict(dict)
        for u in self.graph:
            for v in self.graph[u]:
                residual_graph[u][v] = 1  # Each edge has capacity 1
                residual_graph[v].setdefault(u, 0)  # Ensure reverse edge exists
        
        max_flow = 0
        
        while True:
            # Find an augmenting path using BFS
            path, flow = self._bfs_augmenting_path(residual_graph, source, sink)
            
            if path is None:
                break  # No more augmenting paths
            
            # Update residual capacities
            max_flow += flow
            
            # Augment the flow along the path
            current = sink
            while current != source:
                prev = path[current]
                residual_graph[prev][current] -= flow
                residual_graph[current][prev] += flow
                current = prev
        
        return max_flow
    
    def _bfs_augmenting_path(self, residual_graph, source, sink):
        """
        Find an augmenting path using BFS.
        
        Args:
            residual_graph: Residual capacity graph
            source: Source node
            sink: Sink node
            
        Returns:
            (path, flow) tuple where path is a dictionary of parent pointers
            and flow is the bottleneck capacity of the path
        """
        queue = deque([source])
        path = {source: None}
        
        while queue and sink not in path:
            current = queue.popleft()
            
            for neighbor in residual_graph[current]:
                if neighbor not in path and residual_graph[current][neighbor] > 0:
                    path[neighbor] = current
                    queue.append(neighbor)
        
        if sink not in path:
            return None, 0  # No augmenting path found
        
        # Find the bottleneck capacity
        flow = float('inf')
        current = sink
        while current != source:
            prev = path[current]
            flow = min(flow, residual_graph[prev][current])
            current = prev
        
        return path, flow