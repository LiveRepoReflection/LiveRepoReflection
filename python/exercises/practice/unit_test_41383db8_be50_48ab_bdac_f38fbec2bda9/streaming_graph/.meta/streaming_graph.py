def process_operations(operations):
    # Graph represented as an adjacency list.
    graph = {}
    # Using a set to keep track of existing edges.
    # Store edges as tuple with (min(u, v), max(u, v))
    edges = set()
    
    results = []
    
    def add_edge(u, v):
        # Ensure both nodes are in graph
        if u not in graph:
            graph[u] = set()
        if v not in graph:
            graph[v] = set()
        # Check if edge exists
        edge = (min(u, v), max(u, v))
        if edge in edges:
            return
        # Add the edge both ways and record in edges set.
        graph[u].add(v)
        graph[v].add(u)
        edges.add(edge)
    
    def remove_edge(u, v):
        edge = (min(u, v), max(u, v))
        if edge not in edges:
            return
        # Remove edge from both nodes if present.
        if u in graph and v in graph[u]:
            graph[u].remove(v)
        if v in graph and u in graph[v]:
            graph[v].remove(u)
        edges.remove(edge)
    
    def compute_largest_component():
        visited = set()
        largest = 0
        
        def dfs(node):
            stack = [node]
            count = 0
            while stack:
                cur = stack.pop()
                if cur in visited:
                    continue
                visited.add(cur)
                count += 1
                for neighbor in graph.get(cur, []):
                    if neighbor not in visited:
                        stack.append(neighbor)
            return count
        
        # Consider all nodes present in graph.
        for node in graph:
            if node not in visited:
                comp_size = dfs(node)
                if comp_size > largest:
                    largest = comp_size
        return largest

    for op in operations:
        parts = op.split()
        if not parts:
            continue
        if parts[0] == "add":
            # Parse u and v as integers.
            if len(parts) != 3:
                continue
            try:
                u = int(parts[1])
                v = int(parts[2])
            except ValueError:
                continue
            add_edge(u, v)
        elif parts[0] == "remove":
            # Parse u and v as integers.
            if len(parts) != 3:
                continue
            try:
                u = int(parts[1])
                v = int(parts[2])
            except ValueError:
                continue
            remove_edge(u, v)
        elif parts[0] == "query":
            # For query, if no nodes, largest component is 0.
            if not graph:
                results.append(0)
            else:
                results.append(compute_largest_component())
    return results

if __name__ == "__main__":
    # Example usage:
    ops = [
        "add 0 1",
        "add 1 2",
        "query",
        "remove 1 2",
        "query",
        "add 2 3",
        "add 3 4",
        "add 4 5",
        "query"
    ]
    output = process_operations(ops)
    for result in output:
        print(result)