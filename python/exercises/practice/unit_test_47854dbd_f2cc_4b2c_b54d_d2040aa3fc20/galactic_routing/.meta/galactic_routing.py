import heapq

def process_events(events):
    graph = {}
    outputs = []
    for event in events:
        parts = event.split()
        if parts[0] == "ADD_LINK":
            u = int(parts[1])
            v = int(parts[2])
            latency = int(parts[3])
            bandwidth = int(parts[4])
            stability = float(parts[5])
            if u not in graph:
                graph[u] = {}
            if v not in graph:
                graph[v] = {}
            graph[u][v] = (latency, bandwidth, stability)
            graph[v][u] = (latency, bandwidth, stability)
        elif parts[0] == "REMOVE_LINK":
            u = int(parts[1])
            v = int(parts[2])
            if u in graph and v in graph[u]:
                del graph[u][v]
            if v in graph and u in graph[v]:
                del graph[v][u]
        elif parts[0] == "QUERY_ROUTE":
            source = int(parts[1])
            destination = int(parts[2])
            data_size = int(parts[3])
            deadline = int(parts[4])
            route = find_best_route(graph, source, destination, deadline)
            if route is None:
                outputs.append("NO_ROUTE")
            else:
                outputs.append(" ".join(str(node) for node in route))
    return outputs

def find_best_route(graph, source, destination, deadline):
    # Multi-objective label: (stability, min_bandwidth, latency, path)
    # Initialize with source: stability=1.0, min_bandwidth is infinite, latency=0, path=[source]
    initial_label = (1.0, float('inf'), 0, [source])
    # Each state will be stored in priority queue with key:
    # (-stability, -min_bandwidth, latency) for lex order: maximize stability, maximize min_bandwidth, minimize latency.
    pq = [((-initial_label[0], -initial_label[1], initial_label[2]), initial_label)]
    # For each node, store non-dominated labels: list of tuples (stability, min_bandwidth, latency)
    best_labels = {source: [(initial_label[0], initial_label[1], initial_label[2])]}
    # Store all valid labels reaching destination
    destination_labels = []
    while pq:
        key, label = heapq.heappop(pq)
        curr_stability, curr_min_bandwidth, curr_latency, curr_path = label
        # If we reached destination and label is feasible, record it.
        if curr_path[-1] == destination:
            destination_labels.append(label)
            # Continue search; there might be better label still in the queue.
            # Do not return immediately.
        # Expand neighbors:
        current_node = curr_path[-1]
        if current_node not in graph:
            continue
        for neighbor, edge in graph[current_node].items():
            if neighbor in curr_path:
                # Avoid cycles
                continue
            edge_latency, edge_bandwidth, edge_stability = edge
            new_latency = curr_latency + edge_latency
            if new_latency > deadline:
                continue
            new_stability = curr_stability * edge_stability
            new_min_bandwidth = edge_bandwidth if curr_min_bandwidth == float('inf') else min(curr_min_bandwidth, edge_bandwidth)
            new_path = curr_path + [neighbor]
            new_label = (new_stability, new_min_bandwidth, new_latency, new_path)
            # Check if new label is dominated by existing ones for this neighbor
            if not is_dominated(neighbor, new_label, best_labels):
                # Record new label for neighbor
                if neighbor not in best_labels:
                    best_labels[neighbor] = []
                best_labels[neighbor].append((new_stability, new_min_bandwidth, new_latency))
                heapq.heappush(pq, ((-new_stability, -new_min_bandwidth, new_latency), new_label))
    if not destination_labels:
        return None
    # Choose the best label among destination labels based on lex criteria:
    # highest stability, highest min_bandwidth, lowest latency.
    destination_labels.sort(key=lambda x: (-x[0], -x[1], x[2]))
    return destination_labels[0][3]

def is_dominated(node, new_label, best_labels):
    new_stability, new_min_bandwidth, new_latency, _ = new_label
    if node in best_labels:
        for stability, min_bandwidth, latency in best_labels[node]:
            # A label dominates new_label if:
            # stability >= new_stability, min_bandwidth >= new_min_bandwidth, latency <= new_latency
            if stability >= new_stability and min_bandwidth >= new_min_bandwidth and latency <= new_latency:
                return True
    return False