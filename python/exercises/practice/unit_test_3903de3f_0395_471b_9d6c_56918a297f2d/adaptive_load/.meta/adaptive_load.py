def adaptive_load(N, server_capacities, server_weights, requests):
    """
    Distribute client requests across server nodes based on load and capacity.

    Args:
        N: Number of server nodes
        server_capacities: List of tuples (cpu, memory, network) capacity for each server
        server_weights: List of performance weights for each server
        requests: List of tuples (cpu, memory, network) usage for each request

    Returns:
        List of integers indicating which server each request is assigned to (-1 if unassignable)
    """
    # Initialize current resource usage on each server
    current_loads = [(0, 0, 0) for _ in range(N)]
    
    # Result list to track assignments
    assignments = []
    
    # Process each request
    for request in requests:
        cpu_req, mem_req, net_req = request
        
        # Find best server for this request
        best_server = -1
        lowest_cost = float('inf')
        
        for server in range(N):
            # Check if server has enough capacity
            cpu_cap, mem_cap, net_cap = server_capacities[server]
            cpu_used, mem_used, net_used = current_loads[server]
            
            if (cpu_used + cpu_req <= cpu_cap and 
                mem_used + mem_req <= mem_cap and 
                net_used + net_req <= net_cap):
                
                # Calculate cost based on utilization and performance weight
                # Higher utilization = higher cost
                # Higher server weight = lower cost (faster server)
                
                # Calculate utilization percentages after adding this request
                new_cpu_util = (cpu_used + cpu_req) / cpu_cap if cpu_cap > 0 else 1.0
                new_mem_util = (mem_used + mem_req) / mem_cap if mem_cap > 0 else 1.0
                new_net_util = (net_used + net_req) / net_cap if net_cap > 0 else 1.0
                
                # Calculate cost - weighted average utilization
                # Use inverse of server weight so higher weights = lower cost
                server_weight_factor = 1.0 / server_weights[server] if server_weights[server] > 0 else float('inf')
                cost = server_weight_factor * (new_cpu_util + new_mem_util + new_net_util) / 3
                
                # Add a small penalty for more loaded servers to prevent imbalance
                # This helps distribute load more evenly when utilization is similar
                utilization_penalty = 0.01 * (new_cpu_util + new_mem_util + new_net_util)
                cost += utilization_penalty
                
                # Check if this server has lower cost
                if cost < lowest_cost:
                    best_server = server
                    lowest_cost = cost
        
        # Assign request to best server (if any available)
        assignments.append(best_server)
        
        # Update server loads if assigned
        if best_server != -1:
            cpu_used, mem_used, net_used = current_loads[best_server]
            current_loads[best_server] = (
                cpu_used + cpu_req,
                mem_used + mem_req,
                net_used + net_req
            )
    
    return assignments