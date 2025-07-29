def allocate_resources(microservices, servers):
    """
    Allocate resources to microservices using a first-fit decreasing algorithm.
    
    Args:
        microservices: List of tuples (cpu_cores, ram_mb, disk_gb)
        servers: List of tuples (cpu_cores, ram_mb, disk_gb)
    
    Returns:
        The minimum number of servers required to host all microservices, or -1 if not possible.
    """
    if not microservices:
        return 0
    
    if not servers:
        return -1
    
    # Assume all servers have the same capacity for simplicity
    server_capacity = servers[0]
    
    # Sort microservices based on resource usage (using CPU as primary, then RAM, then disk)
    # This is the key to the "decreasing" part of first-fit decreasing
    # Using a multi-dimensional sorting approach to order by all three resources
    # First normalize the values relative to server capacity
    normalized_services = []
    for i, (cpu, ram, disk) in enumerate(microservices):
        # Calculate a weighted resource score (higher means more resource-intensive)
        # We normalize by dividing by server capacity to get values between 0 and 1
        cpu_norm = cpu / server_capacity[0]
        ram_norm = ram / server_capacity[1]
        disk_norm = disk / server_capacity[2]
        
        # Use the maximum normalized value as the primary sort key
        # This ensures we place the most resource-intensive services first
        resource_score = max(cpu_norm, ram_norm, disk_norm)
        
        normalized_services.append((resource_score, i, (cpu, ram, disk)))
    
    # Sort in descending order of resource score
    normalized_services.sort(reverse=True)
    
    # Check if any microservice exceeds server capacity
    for _, _, (cpu, ram, disk) in normalized_services:
        if cpu > server_capacity[0] or ram > server_capacity[1] or disk > server_capacity[2]:
            return -1
    
    # Initialize server list
    active_servers = []
    
    # Place each microservice using first-fit algorithm
    for _, _, (cpu, ram, disk) in normalized_services:
        # Try to find an existing server that can fit this microservice
        placed = False
        
        for server in active_servers:
            server_cpu, server_ram, server_disk = server
            
            # Check if this server has enough remaining capacity
            if (server_cpu >= cpu and server_ram >= ram and server_disk >= disk):
                # Update server's remaining capacity
                server[0] -= cpu
                server[1] -= ram
                server[2] -= disk
                placed = True
                break
        
        # If no existing server could fit this microservice, start a new one
        if not placed:
            new_server = list(server_capacity)
            new_server[0] -= cpu
            new_server[1] -= ram
            new_server[2] -= disk
            active_servers.append(new_server)
    
    return len(active_servers)