import heapq
from collections import defaultdict, deque
import itertools

def optimize_communication(graph, L, critical_pairs, C, r, B, R, p):
    """
    Optimize communication paths between services by strategic cache and replica placement.
    
    Args:
        graph: Dictionary representing the directed graph (adjacency list)
        L: Dictionary representing the latency matrix
        critical_pairs: Set of tuples representing the critical service pairs
        C: Dictionary representing the cache placement costs
        r: Dictionary representing the replication costs
        B: The cache placement budget (integer)
        R: The replication limit (integer)
        p: The percentage of requests served by cache (float, 0.0 to 1.0)
    
    Returns:
        A tuple (cache_placement, replication_placement) of sets containing service names
    """
    # Helper function to compute the shortest path between two services
    def shortest_path(start, end):
        distances = {service: float('infinity') for service in graph}
        distances[start] = 0
        pq = [(0, start)]
        visited = set()
        
        while pq:
            current_distance, current_service = heapq.heappop(pq)
            
            if current_service == end:
                return current_distance
                
            if current_service in visited:
                continue
                
            visited.add(current_service)
            
            for neighbor in graph[current_service]:
                edge = (current_service, neighbor)
                if edge in L:
                    distance = current_distance + L[edge]
                    if distance < distances[neighbor]:
                        distances[neighbor] = distance
                        heapq.heappush(pq, (distance, neighbor))
        
        return float('infinity')  # No path found
    
    # Helper function to compute all paths between two services
    def get_all_paths(start, end):
        paths = []
        
        def dfs(current, path, visited):
            if current == end:
                paths.append(path[:])
                return
            
            visited.add(current)
            for neighbor in graph[current]:
                if neighbor not in visited:
                    edge = (current, neighbor)
                    if edge in L:
                        path.append((current, neighbor))
                        dfs(neighbor, path, visited.copy())
                        path.pop()
        
        dfs(start, [], set())
        return paths
    
    # Helper function to compute the total latency of a path
    def path_latency(path):
        return sum(L[edge] for edge in path)
    
    # Compute the baseline latency for each critical pair
    baseline_latencies = {}
    paths_by_pair = {}
    
    for start, end in critical_pairs:
        paths = get_all_paths(start, end)
        paths.sort(key=path_latency)
        if paths:
            baseline_latencies[(start, end)] = path_latency(paths[0])
            paths_by_pair[(start, end)] = paths
        else:
            baseline_latencies[(start, end)] = float('infinity')
            paths_by_pair[(start, end)] = []
    
    # Helper function to compute the expected latency with caching and replication
    def expected_latency(cache_set, replica_set):
        total_latency = 0
        
        for (start, end), paths in paths_by_pair.items():
            if not paths:
                continue
                
            # If there's no path, latency remains infinite
            if baseline_latencies[(start, end)] == float('infinity'):
                total_latency += float('infinity')
                continue
            
            # Get the best path for this pair
            best_path = paths[0]
            
            # Apply caching effect: when we hit a cache, we get 0 latency with probability p
            # for the remainder of the path
            min_latency = float('infinity')
            
            # Consider the impact of caching on each path
            for path in paths:
                current_latency = 0
                cache_hit = False
                
                for i, edge in enumerate(path):
                    source, target = edge
                    
                    # Skip if we've already hit a cache
                    if cache_hit:
                        break
                    
                    # Add edge latency
                    current_latency += L[edge]
                    
                    # Check if we hit a cache
                    if target in cache_set:
                        # With probability p, we hit the cache and stop accumulating latency
                        expected_cache_latency = (1-p) * current_latency + p * (current_latency + 0)
                        min_latency = min(min_latency, expected_cache_latency)
                        cache_hit = True
                
                # If we didn't hit any cache, use the full path latency
                if not cache_hit:
                    min_latency = min(min_latency, current_latency)
            
            # Consider the impact of replication
            if replica_set and end in replica_set:
                # Find shortest paths to all replicas (including original)
                replica_latencies = []
                for path in paths:
                    # Original path to end
                    replica_latencies.append(path_latency(path))
                
                # Take the minimum latency to any replica
                min_latency = min(min_latency, min(replica_latencies))
            
            total_latency += min_latency
        
        # Average latency across all critical pairs
        return total_latency / len(critical_pairs) if critical_pairs else 0
    
    # Identify high-value services for caching and replication
    service_importance = defaultdict(float)
    
    for (start, end), paths in paths_by_pair.items():
        for path in paths:
            for _, service in path:
                service_importance[service] += 1 / len(paths_by_pair)  # Weight by inverse of path count
    
    # Sort services by importance-to-cost ratio for caching
    cache_candidates = []
    for service in graph:
        if service in C:
            importance_cost_ratio = service_importance[service] / C[service] if C[service] > 0 else float('infinity')
            cache_candidates.append((service, importance_cost_ratio))
    
    cache_candidates.sort(key=lambda x: x[1], reverse=True)
    
    # Sort services by importance-to-cost ratio for replication
    replica_candidates = []
    for service in graph:
        if service in r:
            importance_cost_ratio = service_importance[service] / r[service] if r[service] > 0 else float('infinity')
            replica_candidates.append((service, importance_cost_ratio))
    
    replica_candidates.sort(key=lambda x: x[1], reverse=True)
    
    # Generate cache placement options within budget
    cache_options = []
    current_cost = 0
    current_set = set()
    
    for service, _ in cache_candidates:
        if service in C and current_cost + C[service] <= B:
            current_set.add(service)
            current_cost += C[service]
    
    cache_options.append(current_set)
    
    # Try different combinations of top cache candidates
    top_candidates = [service for service, _ in cache_candidates[:min(10, len(cache_candidates))]]
    for k in range(1, min(6, len(top_candidates) + 1)):
        for combo in itertools.combinations(top_candidates, k):
            combo_cost = sum(C[service] for service in combo if service in C)
            if combo_cost <= B:
                cache_options.append(set(combo))
    
    # Generate replica placement options within limit
    replica_options = []
    
    # No replicas
    replica_options.append(set())
    
    # Single service replicated
    for i in range(min(R, len(replica_candidates))):
        service, _ = replica_candidates[i]
        replica_options.append({service})
    
    # Multiple services replicated (up to R)
    if R > 1:
        for k in range(2, min(R + 1, len(replica_candidates) + 1)):
            for combo in itertools.combinations([s for s, _ in replica_candidates[:10]], k):
                replica_options.append(set(combo))
    
    # Evaluate all combinations to find the best
    best_latency = float('infinity')
    best_cache_placement = set()
    best_replica_placement = set()
    
    for cache_set in cache_options:
        for replica_set in replica_options:
            if len(replica_set) <= R:
                latency = expected_latency(cache_set, replica_set)
                if latency < best_latency:
                    best_latency = latency
                    best_cache_placement = cache_set
                    best_replica_placement = replica_set
    
    return best_cache_placement, best_replica_placement