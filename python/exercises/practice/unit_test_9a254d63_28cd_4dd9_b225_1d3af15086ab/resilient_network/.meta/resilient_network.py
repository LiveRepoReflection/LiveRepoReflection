import math
import sys
sys.setrecursionlimit(10000)

def min_links(n, links, max_cost, min_reliability):
    # Pre-calculate logarithms to transform products into sums.
    # We want: product >= min_reliability  <=>  sum(log r_i) >= log(min_reliability)
    # Since reliabilities are in [0,1], log(r) <= 0. Let req = log(min_reliability).
    if min_reliability <= 0:
        req = -math.inf
    else:
        req = math.log(min_reliability)
    
    # Sort links by cost ascending, and then by reliability descending (i.e. log reliability is higher)
    sorted_links = sorted(links, key=lambda x: (x[2], -x[3]))
    
    # Union-find structure without path compression to support copying
    class UnionFind:
        __slots__ = ('parent', 'rank')
        def __init__(self, size):
            self.parent = list(range(size))
            self.rank = [0] * size
        def find(self, x):
            while self.parent[x] != x:
                x = self.parent[x]
            return x
        def union(self, x, y):
            rx = self.find(x)
            ry = self.find(y)
            if rx == ry:
                return False
            if self.rank[rx] < self.rank[ry]:
                self.parent[rx] = ry
            else:
                self.parent[ry] = rx
                if self.rank[rx] == self.rank[ry]:
                    self.rank[rx] += 1
            return True
        def copy(self):
            new_uf = UnionFind(0)
            new_uf.parent = self.parent[:]
            new_uf.rank = self.rank[:]
            return new_uf
        def components_count(self):
            # Count distinct roots.
            roots = set()
            for i in range(len(self.parent)):
                roots.add(self.find(i))
            return len(roots)
    
    # Check if the current graph (given by selected_edges) satisfies the reliability condition
    def check_reliability(selected_edges):
        # Build reliability matrix. For nodes directly connected, take the maximum reliability edge.
        R = [[0.0 for _ in range(n)] for _ in range(n)]
        for i in range(n):
            R[i][i] = 1.0
        for (u, v, cost, rel) in selected_edges:
            if rel > R[u][v]:
                R[u][v] = rel
                R[v][u] = rel
        # Floyd-Warshall max-product version (in logarithmic domain we use addition)
        # Instead of multiplication, add logarithms.
        # Pre-calculate log_r matrix. For 0 reliability, set to -inf.
        logR = [[-math.inf for _ in range(n)] for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if R[i][j] > 0:
                    logR[i][j] = math.log(R[i][j])
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if logR[i][k] + logR[k][j] > logR[i][j]:
                        logR[i][j] = logR[i][k] + logR[k][j]
        for i in range(n):
            for j in range(n):
                if logR[i][j] < req:
                    return False
        return True

    # Global flag and result container.
    result = [-1]
    found = [False]
    
    # Recursive DFS search for selecting exactly target_count edges among sorted_links.
    def dfs(index, selected_count, target_count, current_cost, uf, selected_edges):
        if found[0]:
            return
        # Prune if current cost exceeds budget
        if current_cost > max_cost:
            return
        # If we've selected enough edges, check connectivity and reliability
        if selected_count == target_count:
            if uf.components_count() != 1:
                return
            # Check reliability condition using Floyd Warshall on the selected subgraph.
            if check_reliability(selected_edges):
                found[0] = True
            return
        
        # Lower bound for connectivity: at least (components - 1) edges needed.
        lower_bound = uf.components_count() - 1
        if selected_count + lower_bound > target_count:
            return
        
        # Prune if not enough remaining edges.
        remaining = target_count - selected_count
        if len(sorted_links) - index < remaining:
            return

        # Iterate over possible edges
        for i in range(index, len(sorted_links)):
            u, v, cost, rel = sorted_links[i]
            # Skip if adding the cost exceeds max_cost
            if current_cost + cost > max_cost:
                continue
            # Make a new union-find copy to simulate union operation.
            new_uf = uf.copy()
            new_edges = list(selected_edges)
            # Check if this edge connects two different components.
            new_uf.union(u, v)
            new_edges.append((u, v, cost, rel))
            dfs(i + 1, selected_count + 1, target_count, current_cost + cost, new_uf, new_edges)
            if found[0]:
                return

    # Try increasing number of edges from minimal (n-1) to total number of links.
    for target_count in range(n - 1, len(sorted_links) + 1):
        found[0] = False
        uf_init = UnionFind(n)
        dfs(0, 0, target_count, 0, uf_init, [])
        if found[0]:
            return target_count
    return -1

if __name__ == "__main__":
    # Sample test run (for manual debugging, not used in unit tests)
    n = 4
    links = [
        (0, 1, 10, 0.9),
        (0, 2, 15, 0.8),
        (1, 2, 12, 0.7),
        (1, 3, 8, 0.95),
        (2, 3, 20, 0.6)
    ]
    max_cost = 40
    min_reliability = 0.65
    print(min_links(n, links, max_cost, min_reliability))