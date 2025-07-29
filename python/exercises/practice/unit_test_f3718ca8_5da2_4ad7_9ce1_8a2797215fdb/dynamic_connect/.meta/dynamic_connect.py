class DynamicConnectivityOracle:
    def __init__(self, n):
        """
        Initialize the Dynamic Connectivity Oracle with n nodes.
        
        Args:
            n (int): Number of nodes (0 to n-1)
        """
        # We don't store data for all N nodes since N can be as large as 10^9
        # Instead, we'll only track nodes that are actually used in connections
        self.parent = {}
        self.rank = {}
        self.n = n
        
    def find(self, x):
        """
        Find the root of the component containing node x (with path compression).
        
        Args:
            x (int): The node to find the root for
            
        Returns:
            int: The root of the component containing x
        """
        # If this is the first time we've seen this node
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0
            return x
            
        # Path compression: make every node on the path point directly to the root
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    def connect(self, u, v):
        """
        Connect nodes u and v, making them part of the same component.
        
        Args:
            u (int): First node
            v (int): Second node
        """
        # Check input validity
        if u < 0 or u >= self.n or v < 0 or v >= self.n:
            raise ValueError(f"Node values must be between 0 and {self.n-1}")
            
        # Find roots of the components containing u and v
        root_u = self.find(u)
        root_v = self.find(v)
        
        # If u and v are already connected, no need to do anything
        if root_u == root_v:
            return
            
        # Union by rank: attach the smaller tree to the root of the larger tree
        if self.rank[root_u] < self.rank[root_v]:
            self.parent[root_u] = root_v
        elif self.rank[root_u] > self.rank[root_v]:
            self.parent[root_v] = root_u
        else:
            # If ranks are the same, make one the parent and increment its rank
            self.parent[root_v] = root_u
            self.rank[root_u] += 1
    
    def are_connected(self, u, v):
        """
        Check if nodes u and v are connected (in the same component).
        
        Args:
            u (int): First node
            v (int): Second node
            
        Returns:
            bool: True if u and v are connected, False otherwise
        """
        # Check input validity
        if u < 0 or u >= self.n or v < 0 or v >= self.n:
            raise ValueError(f"Node values must be between 0 and {self.n-1}")
            
        # Special case: a node is always connected to itself
        if u == v:
            return True
            
        # If either node has never been connected to anything, they can't be connected
        if u not in self.parent or v not in self.parent:
            return False
            
        # Nodes are connected if they have the same root in the disjoint-set forest
        return self.find(u) == self.find(v)