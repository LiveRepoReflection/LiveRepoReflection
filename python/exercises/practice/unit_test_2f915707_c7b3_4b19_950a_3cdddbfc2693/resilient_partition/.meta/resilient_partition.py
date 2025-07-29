def min_cost_partition(n, edges, k, node_weights):
    # For k > 1, we can always partition the graph into valid resilient clusters
    # by splitting non-resilient connected components into singletons or pairs.
    if k != 1:
        return sum(node_weights)
    
    # For k == 1 we require that the entire network (as a union of its connected components)
    # is resilient. For each connected component with 3 or more nodes, we check it is biconnected.
    graph = {i: [] for i in range(n)}
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)
        
    visited = [False] * n
    # Function to get one connected component via DFS.
    def get_component(start):
        stack = [start]
        comp = []
        visited[start] = True
        while stack:
            u = stack.pop()
            comp.append(u)
            for v in graph[u]:
                if not visited[v]:
                    visited[v] = True
                    stack.append(v)
        return comp

    # Tarjan's algorithm to find articulation points in a connected component.
    def find_articulation_points(comp):
        comp_set = set(comp)
        # Only consider nodes in comp_set.
        # Initialize necessary arrays.
        disc = {u: -1 for u in comp_set}  # discovery time
        low = {u: -1 for u in comp_set}   # low-link values
        time = [0]
        articulation = set()
        
        def dfs(u, parent):
            children = 0
            disc[u] = time[0]
            low[u] = time[0]
            time[0] += 1
            for v in graph[u]:
                if v not in comp_set:
                    continue
                if disc[v] == -1:  # not visited
                    children += 1
                    dfs(v, u)
                    low[u] = min(low[u], low[v])
                    if parent is not None and low[v] >= disc[u]:
                        articulation.add(u)
                elif v != parent:
                    low[u] = min(low[u], disc[v])
            if parent is None and children > 1:
                articulation.add(u)
        
        for u in comp_set:
            if disc[u] == -1:
                dfs(u, None)
        return articulation

    # Check every connected component.
    for i in range(n):
        if not visited[i]:
            comp = get_component(i)
            if len(comp) >= 3:
                # Check if this connected component is biconnected.
                arts = find_articulation_points(comp)
                if arts:
                    return -1
    return sum(node_weights)


if __name__ == '__main__':
    # For local testing only.
    n = 6
    edges = [(0, 1), (1, 2), (2, 0), (2, 3), (3, 4), (4, 5), (5, 3)]
    k = 2
    node_weights = [10, 12, 15, 8, 5, 7]
    print(min_cost_partition(n, edges, k, node_weights))