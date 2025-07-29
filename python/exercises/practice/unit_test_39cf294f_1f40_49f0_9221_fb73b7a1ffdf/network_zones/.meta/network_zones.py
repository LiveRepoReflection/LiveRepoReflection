from collections import defaultdict, deque
import heapq

def partition_network(graph, resilience, K, latencies):
    # Input validation
    N = len(graph)
    if N == 0:
        raise ValueError("Graph cannot be empty")
    if K > N:
        raise ValueError("Number of zones cannot be greater than number of nodes")
    if any(r < 0 for r in resilience):
        raise ValueError("Resilience scores must be non-negative")
    if any(l < 0 for l in latencies.values()):
        raise ValueError("Latencies must be non-negative")

    def is_connected_subgraph(nodes):
        if not nodes:
            return True
        visited = set()
        queue = deque([next(iter(nodes))])
        
        while queue:
            node = queue.popleft()
            if node not in visited:
                visited.add(node)
                for neighbor in graph[node]:
                    if neighbor in nodes and neighbor not in visited:
                        queue.append(neighbor)
        
        return len(visited) == len(nodes)

    def calculate_inter_zone_latency(partition):
        total_latency = 0
        for u in range(N):
            for v in graph[u]:
                if partition[u] != partition[v]:
                    total_latency += latencies.get((u, v), 0)
        return total_latency // 2  # Divide by 2 as each edge is counted twice

    def calculate_min_resilience(partition):
        zone_resilience = defaultdict(list)
        for node, zone in enumerate(partition):
            zone_resilience[zone].append(resilience[node])
        return min(min(scores) for scores in zone_resilience.values())

    def is_valid_partition(partition):
        zones = defaultdict(set)
        for node, zone in enumerate(partition):
            zones[zone].add(node)
        return all(is_connected_subgraph(nodes) for nodes in zones.values())

    def generate_partitions(curr_partition, pos):
        if pos == N:
            if is_valid_partition(curr_partition):
                return [(calculate_min_resilience(curr_partition),
                        -calculate_inter_zone_latency(curr_partition),
                        curr_partition)]
            return []
        
        results = []
        for zone in range(K):
            curr_partition[pos] = zone
            results.extend(generate_partitions(curr_partition[:], pos + 1))
        return results

    # Generate and evaluate all valid partitions
    initial_partition = [0] * N
    all_partitions = generate_partitions(initial_partition, 0)
    
    if not all_partitions:
        raise ValueError("No valid partition found")

    # Sort by min resilience (descending) and then by negative latency (ascending)
    all_partitions.sort(reverse=True)
    
    # Return the partition with maximum min resilience and minimum latency
    return list(all_partitions[0][2])

def optimize_partition(partition, graph, resilience, K, latencies):
    """Local search optimization to improve the partition"""
    N = len(graph)
    best_score = (calculate_min_resilience(partition), -calculate_inter_zone_latency(partition))
    improved = True
    
    while improved:
        improved = False
        for node in range(N):
            original_zone = partition[node]
            for new_zone in range(K):
                if new_zone != original_zone:
                    partition[node] = new_zone
                    if is_valid_partition(partition):
                        new_score = (calculate_min_resilience(partition),
                                   -calculate_inter_zone_latency(partition))
                        if new_score > best_score:
                            best_score = new_score
                            improved = True
                            break
                    partition[node] = original_zone
            if improved:
                break
    
    return partition

def calculate_min_resilience(partition):
    """Helper function to calculate minimum resilience of a partition"""
    zone_resilience = defaultdict(list)
    for node, zone in enumerate(partition):
        zone_resilience[zone].append(resilience[node])
    return min(min(scores) for scores in zone_resilience.values())

def calculate_inter_zone_latency(partition):
    """Helper function to calculate inter-zone latency"""
    total_latency = 0
    for u in range(len(partition)):
        for v in graph[u]:
            if partition[u] != partition[v]:
                total_latency += latencies.get((u, v), 0)
    return total_latency // 2

def is_valid_partition(partition):
    """Helper function to check if a partition is valid"""
    zones = defaultdict(set)
    for node, zone in enumerate(partition):
        zones[zone].add(node)
    return all(is_connected_subgraph(nodes) for nodes in zones.values())

def is_connected_subgraph(nodes):
    """Helper function to check if a subgraph is connected"""
    if not nodes:
        return True
    visited = set()
    queue = deque([next(iter(nodes))])
    
    while queue:
        node = queue.popleft()
        if node not in visited:
            visited.add(node)
            for neighbor in graph[node]:
                if neighbor in nodes and neighbor not in visited:
                    queue.append(neighbor)
    
    return len(visited) == len(nodes)