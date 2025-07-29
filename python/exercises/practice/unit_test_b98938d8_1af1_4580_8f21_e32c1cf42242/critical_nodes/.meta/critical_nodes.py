from itertools import combinations

def critical_nodes(N, links, K):
    # Build the graph as an adjacency list.
    graph = {i: set() for i in range(N)}
    for u, v in links:
        graph[u].add(v)
        graph[v].add(u)
        
    def count_components(removed):
        removed_set = set(removed)
        visited = [False] * N
        components = 0
        for i in range(N):
            if i in removed_set or visited[i]:
                continue
            components += 1
            stack = [i]
            visited[i] = True
            while stack:
                node = stack.pop()
                for neighbor in graph[node]:
                    if neighbor not in removed_set and not visited[neighbor]:
                        visited[neighbor] = True
                        stack.append(neighbor)
        return components

    # If the current graph already has at least K connected components,
    # then no removal is needed.
    if count_components([]) >= K:
        return []
    
    # For small graphs, perform a brute-force search over subsets
    # to find the minimum removal set with at least K components.
    # Since combinations returns in lexicographical order, the first valid set
    # is both minimal and lexicographically smallest.
    for r in range(1, N + 1):
        for combo in combinations(range(N), r):
            if count_components(combo) >= K:
                return list(combo)
    # If no valid removal set is found, return an empty list.
    return []