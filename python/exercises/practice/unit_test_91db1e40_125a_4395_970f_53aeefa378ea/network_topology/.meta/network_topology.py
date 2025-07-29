def optimal_network_topology(n, m, k):
    # Check feasibility: each spanning tree requires 2*(n-1) total degrees.
    if sum(k) < 2 * (n - 1):
        return []
    
    # Helper: to add an edge and update degrees, and record in edge_set for quick lookup.
    edges = []
    edge_set = set()
    degrees = [0] * n
    used_edges = 0

    # Function to add an edge if it doesn't exist and update degree counts.
    def add_edge(u, v):
        nonlocal used_edges
        # Ensure u < v for consistent ordering.
        if u > v:
            u, v = v, u
        if (u, v) in edge_set:
            return False
        # Check capacity constraints
        if degrees[u] >= k[u] or degrees[v] >= k[v]:
            return False
        edges.append((u, v))
        edge_set.add((u, v))
        degrees[u] += 1
        degrees[v] += 1
        used_edges += 1
        return True

    # First try to build a spanning tree using a star configuration if possible.
    star_center = None
    for i in range(n):
        if k[i] >= n - 1:
            star_center = i
            break

    if star_center is not None:
        # Use the star center to connect all other nodes
        for j in range(n):
            if j == star_center:
                continue
            if not add_edge(star_center, j):
                # Should not happen because star_center has sufficient capacity
                return []
    else:
        # No suitable star center exists. Build a spanning tree using a greedy approach.
        in_tree = set()
        in_tree.add(0)
        for j in range(1, n):
            connected = False
            # Attempt to connect node j to any node in the current tree
            for i in sorted(in_tree):
                if degrees[i] < k[i] and k[j] > 0:
                    if add_edge(i, j):
                        connected = True
                        break
            if not connected:
                # Unable to connect node j under capacity constraints.
                return []
            in_tree.add(j)

    # After spanning tree, we have used (n-1) edges.
    # Now, if we can add extra edges (used_edges < m), iterate over all possible pairs in lex order.
    for i in range(n):
        for j in range(i+1, n):
            if used_edges >= m:
                break
            if (i, j) in edge_set:
                continue
            if degrees[i] < k[i] and degrees[j] < k[j]:
                add_edge(i, j)
        if used_edges >= m:
            break

    # Final check: ensure the graph is connected.
    if not is_connected(n, edges):
        return []
    
    # Ensure the edges are sorted lexicographically.
    edges.sort()
    return edges

def is_connected(n, edges):
    from collections import deque, defaultdict
    graph = defaultdict(list)
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)
    visited = [False] * n
    queue = deque([0])
    visited[0] = True
    count = 1
    while queue:
        node = queue.popleft()
        for neighbor in graph[node]:
            if not visited[neighbor]:
                visited[neighbor] = True
                count += 1
                queue.append(neighbor)
    return count == n

if __name__ == '__main__':
    # Example usage:
    n = 5
    m = 7
    k = [4, 4, 4, 4, 4]
    result = optimal_network_topology(n, m, k)
    print(result)