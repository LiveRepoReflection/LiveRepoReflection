def analyze_network(devices, edges, entry_point, target_devices):
    # Precompute vulnerability score for each device
    vulnerability = {dev: sum(info["vulnerabilities"]) for dev, info in devices.items()}
    
    # Build a graph as adjacency list
    graph = {}
    for src, dst in edges:
        if src in graph:
            graph[src].append(dst)
        else:
            graph[src] = [dst]
    # Ensure every device appears in the graph even if no outgoing edges
    for dev in devices:
        if dev not in graph:
            graph[dev] = []
            
    # Global answer: best_score and best_path
    best = {"score": 0, "path": None}

    # Use DFS to explore all simple paths
    def dfs(current, current_score, path, visited):
        nonlocal best
        # Add the current device's vulnerability once (already added when calling this function)
        # Check if current is a target device
        if current in target_devices:
            # Compare with global best solution.
            # Update if current score is higher OR score ties and path is shorter.
            if (current_score > best["score"]) or (current_score == best["score"] and (best["path"] is None or len(path) < len(best["path"]))):
                best["score"] = current_score
                best["path"] = path.copy()
        # Explore neighbors
        for neighbor in graph.get(current, []):
            if neighbor not in visited:
                # mark neighbor as visited and add its vulnerability score
                visited.add(neighbor)
                path.append(neighbor)
                dfs(neighbor, current_score + vulnerability.get(neighbor, 0), path, visited)
                # backtrack
                path.pop()
                visited.remove(neighbor)
    
    # Start DFS from entry_point
    if entry_point not in devices:
        return (0, [])
    initial_score = vulnerability.get(entry_point, 0)
    visited = set()
    visited.add(entry_point)
    dfs(entry_point, initial_score, [entry_point], visited)
    
    if best["path"] is None:
        return (0, [])
    return (best["score"], best["path"])

if __name__ == '__main__':
    # Example usage (can be removed or commented out during unit testing)
    devices = {
        "A": {"device_type": "web_server", "os_version": "Linux", "open_ports": [80, 443], "vulnerabilities": [3, 5]},
        "B": {"device_type": "application_server", "os_version": "Windows", "open_ports": [8080], "vulnerabilities": [7, 2]},
        "C": {"device_type": "database_server", "os_version": "Linux", "open_ports": [3306], "vulnerabilities": [9]},
        "D": {"device_type": "workstation", "os_version": "Windows", "open_ports": [139, 445], "vulnerabilities": [1, 4]}
    }
    edges = [("A", "B"), ("B", "C"), ("A", "D")]
    entry_point = "A"
    target_devices = ["C", "D"]
    result = analyze_network(devices, edges, entry_point, target_devices)
    print(result)