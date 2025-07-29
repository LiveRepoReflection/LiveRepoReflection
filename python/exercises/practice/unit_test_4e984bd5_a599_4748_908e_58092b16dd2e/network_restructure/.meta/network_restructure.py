import sys
from itertools import combinations
from collections import defaultdict

class UnionFind:
    def __init__(self, size):
        self.parent = list(range(size+1))  # 1-based indexing
        self.rank = [0]*(size+1)
        
    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    def union(self, x, y):
        x_root = self.find(x)
        y_root = self.find(y)
        if x_root == y_root:
            return False
        if self.rank[x_root] < self.rank[y_root]:
            self.parent[x_root] = y_root
        else:
            self.parent[y_root] = x_root
            if self.rank[x_root] == self.rank[y_root]:
                self.rank[x_root] += 1
        return True

def optimal_network_restructure(N, M, edges, B, K):
    if N == 1:
        return 0
        
    # Pre-process edges and create a set for quick lookup
    edge_set = set((u, v) for u, v, _ in edges)
    edges_with_cost = [(u, v, cost) for u, v, cost in edges]
    
    min_max_degree = sys.maxsize
    
    # Try all possible combinations of K edges from original network
    for original_edges in combinations(edges_with_cost, K):
        total_cost = sum(cost for _, _, cost in original_edges)
        if total_cost > B:
            continue
            
        uf = UnionFind(N)
        selected_edges = list(original_edges)
        degree = defaultdict(int)
        
        # Add original edges first
        for u, v, _ in original_edges:
            uf.union(u, v)
            degree[u] += 1
            degree[v] += 1
            
        # Sort remaining edges by cost (ascending)
        remaining_edges = [e for e in edges_with_cost if e not in original_edges]
        remaining_edges.sort(key=lambda x: x[2])
        
        # Krusky's algorithm to build MST with remaining budget
        for u, v, cost in remaining_edges:
            if total_cost + cost > B:
                continue
            if uf.union(u, v):
                selected_edges.append((u, v, cost))
                total_cost += cost
                degree[u] += 1
                degree[v] += 1
                
        # Check if all nodes are connected
        root = uf.find(1)
        all_connected = all(uf.find(i) == root for i in range(2, N+1))
        
        if all_connected:
            current_max_degree = max(degree.values()) if degree else 0
            if current_max_degree < min_max_degree:
                min_max_degree = current_max_degree
                
    return min_max_degree if min_max_degree != sys.maxsize else -1