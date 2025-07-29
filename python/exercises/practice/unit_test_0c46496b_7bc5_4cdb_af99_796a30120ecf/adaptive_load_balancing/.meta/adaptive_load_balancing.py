import heapq

def distribute_requests(N, M, server_capacities, initial_loads, latency_matrix, requests):
    # Calculate remaining capacity for each server
    remaining_capacity = [server_capacities[i] - initial_loads[i] for i in range(N)]
    total_capacity = sum(remaining_capacity)
    
    # If total capacity is less than requests, adjust requests
    actual_requests = min(requests, total_capacity)
    
    # Initialize result with zeros
    result = [0] * N
    
    # If no requests or no capacity, return zeros
    if actual_requests == 0 or total_capacity == 0:
        return result
    
    # For each load balancer, create a min-heap based on latency and load
    lb_heaps = []
    for lb in range(M):
        heap = []
        for server in range(N):
            if remaining_capacity[server] > 0:
                # Use a composite key: (latency, remaining_capacity)
                # Lower latency and higher capacity get higher priority
                key = (latency_matrix[lb][server], -remaining_capacity[server], server)
                heapq.heappush(heap, key)
        lb_heaps.append(heap)
    
    # Distribute requests
    for _ in range(actual_requests):
        best_server = None
        best_lb = None
        min_score = float('inf')
        
        # Find the best server across all load balancers
        for lb in range(M):
            if lb_heaps[lb]:
                current_latency, neg_capacity, server = lb_heaps[lb][0]
                current_score = current_latency * (1 + initial_loads[server]/server_capacities[server])
                
                if current_score < min_score:
                    min_score = current_score
                    best_server = server
                    best_lb = lb
        
        if best_server is not None:
            # Assign request to this server
            result[best_server] += 1
            initial_loads[best_server] += 1
            remaining_capacity[best_server] -= 1
            
            # Update the heap for this load balancer
            heapq.heappop(lb_heaps[best_lb])
            if remaining_capacity[best_server] > 0:
                new_key = (
                    latency_matrix[best_lb][best_server],
                    -remaining_capacity[best_server],
                    best_server
                )
                heapq.heappush(lb_heaps[best_lb], new_key)
    
    return result