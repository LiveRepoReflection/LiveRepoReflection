def min_total_cost(N, M, C, Dependencies, K):
    # Build graph as adjacency list
    graph = [[] for _ in range(N)]
    # Also record edges with counts per node pair in case there are multiple edges.
    for u, v in Dependencies:
        graph[u].append(v)

    # First, attempt Kahn's algorithm for topological sort to check for acyclicity.
    indegree = [0] * N
    for u in range(N):
        for v in graph[u]:
            indegree[v] += 1

    queue = []
    for i in range(N):
        if indegree[i] == 0:
            queue.append(i)

    count = 0
    while queue:
        node = queue.pop(0)
        count += 1
        for neigh in graph[node]:
            indegree[neigh] -= 1
            if indegree[neigh] == 0:
                queue.append(neigh)

    # If all nodes were processed, the graph is acyclic.
    if count == N:
        return sum(C)

    # Otherwise, compute the minimum number of dependency removals required.
    # We do this by finding strongly connected components (SCCs) using Tarjan's algorithm.
    index = 0
    indices = [-1] * N
    lowlink = [0] * N
    on_stack = [False] * N
    stack = []
    sccs = []

    def tarjan(v):
        nonlocal index
        indices[v] = index
        lowlink[v] = index
        index += 1
        stack.append(v)
        on_stack[v] = True

        for w in graph[v]:
            if indices[w] == -1:
                tarjan(w)
                lowlink[v] = min(lowlink[v], lowlink[w])
            elif on_stack[w]:
                lowlink[v] = min(lowlink[v], indices[w])
        if lowlink[v] == indices[v]:
            # Start a new strongly connected component
            scc = []
            while True:
                w = stack.pop()
                on_stack[w] = False
                scc.append(w)
                if w == v:
                    break
            sccs.append(scc)

    for v in range(N):
        if indices[v] == -1:
            tarjan(v)

    # Map each node to its respective SCC id
    node_to_scc = {}
    for idx, component in enumerate(sccs):
        for node in component:
            node_to_scc[node] = idx

    # Count internal edges for each SCC
    scc_edge_count = [0] * len(sccs)
    scc_node_count = [0] * len(sccs)
    for idx, comp in enumerate(sccs):
        scc_node_count[idx] = len(comp)

    for u in range(N):
        for v in graph[u]:
            if node_to_scc[u] == node_to_scc[v]:
                scc_edge_count[node_to_scc[u]] += 1

    # For each SCC with more than 1 node, calculate minimum removals needed.
    removals_needed = 0
    for idx in range(len(sccs)):
        s = scc_node_count[idx]
        if s > 1:
            # In any acyclic subgraph spanning these nodes, at most s-1 edges can remain.
            removals_needed += scc_edge_count[idx] - (s - 1)

    if removals_needed <= K:
        return sum(C)
    else:
        return -1

if __name__ == '__main__':
    # For debugging or standalone testing, simple manual test can be run
    # Example: Cycle with removal possible.
    N = 3
    M = 2
    C = [10, 20, 30]
    Dependencies = [(0, 1), (1, 2), (2, 0)]
    K = 1
    print(min_total_cost(N, M, C, Dependencies, K))