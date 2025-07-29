def network_scan(n, connections, critical_nodes, entry_points):
    # Build the adjacency list
    graph = {i: [] for i in range(n)}
    for u, v, w in connections:
        graph[u].append((v, w))
        
    # DFS function to find all simple paths from start to target.
    # It returns a list of minimum bandwidths for each distinct simple path.
    def dfs(current, target, visited, current_min):
        results = []
        # If we reached target and the path is non-trivial, record the current minimum bandwidth.
        if current == target and len(visited) > 1:
            results.append(current_min)
            # Do not continue further once target is reached in a simple path.
            return results
        for neighbor, weight in graph[current]:
            if neighbor not in visited:
                # Compute the updated minimum bandwidth along this path.
                next_min = weight if current_min is None else min(current_min, weight)
                visited.add(neighbor)
                results.extend(dfs(neighbor, target, visited, next_min))
                visited.remove(neighbor)
        return results

    vulnerable = set()
    
    # For each critical node, check the vulnerability condition for each entry point
    for crit in critical_nodes:
        # For each entry point, if it is not the same as critical (trivial path not considered)
        for entry in entry_points:
            if entry == crit:
                continue
            visited = set()
            visited.add(entry)
            # Find all simple paths from the entry point to the critical node.
            path_bandwidths = dfs(entry, crit, visited, None)
            if path_bandwidths:
                count_paths = len(path_bandwidths)
                min_bandwidth = min(path_bandwidths)
                # Conditions: vulnerability exists if min_bandwidth < count of distinct simple paths.
                if min_bandwidth < count_paths:
                    vulnerable.add(crit)
                    break  # Found vulnerability from one entry point; no need to check others.
    return vulnerable

if __name__ == '__main__':
    # Simple ad-hoc test, can be augmented or tested through unit tests.
    n = 5
    connections = [(0, 1, 5), (0, 2, 3), (1, 3, 2), (2, 3, 4), (3, 4, 1), (0, 4, 8)]
    critical_nodes = {3, 4}
    entry_points = {0}
    print(network_scan(n, connections, critical_nodes, entry_points))