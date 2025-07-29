def allocate_resources(cpu_demand, memory_demand, network_demand, priority, num_replicas, 
                         cost_per_hour, cpu_capacity, memory_capacity, network_capacity):
    # Create a list of replica items.
    # Each item: (microservice_index, cpu, mem, net)
    replicas = []
    for i in range(len(cpu_demand)):
        for _ in range(num_replicas[i]):
            replicas.append((i, cpu_demand[i], memory_demand[i], network_demand[i]))
    
    # Sort replicas by total resource demand (sum of cpu, memory, network) in descending order.
    replicas.sort(key=lambda x: x[1] + x[2] + x[3], reverse=True)
    
    # Number of available VM types
    m = len(cost_per_hour)
    
    # Prepare allocation dictionary for each VM type.
    allocation = {j: [] for j in range(m)}
    
    # Residual capacities for each VM type.
    residual_cpu = cpu_capacity[:]
    residual_memory = memory_capacity[:]
    residual_network = network_capacity[:]
    
    # Prepare a list of VM type indices sorted by cost per hour (lowest first).
    vm_order = sorted(range(m), key=lambda j: cost_per_hour[j])
    
    # Greedily assign each replica to the cheapest VM type that can accommodate it.
    for ms_index, req_cpu, req_mem, req_net in replicas:
        assigned = False
        for j in vm_order:
            if (residual_cpu[j] >= req_cpu and
                residual_memory[j] >= req_mem and
                residual_network[j] >= req_net):
                allocation[j].append(ms_index)
                residual_cpu[j] -= req_cpu
                residual_memory[j] -= req_mem
                residual_network[j] -= req_net
                assigned = True
                break
        # If no bin could accommodate this replica, try a second pass over VM types sorted by capacity slack.
        # (This is to handle edge cases in ordering.)
        if not assigned:
            # Sort VM types by available CPU capacity descending (could also consider other resources)
            vm_order_alt = sorted(range(m), key=lambda j: (residual_cpu[j], residual_memory[j], residual_network[j]), reverse=True)
            for j in vm_order_alt:
                if (residual_cpu[j] >= req_cpu and
                    residual_memory[j] >= req_mem and
                    residual_network[j] >= req_net):
                    allocation[j].append(ms_index)
                    residual_cpu[j] -= req_cpu
                    residual_memory[j] -= req_mem
                    residual_network[j] -= req_net
                    assigned = True
                    break
        # If still not assigned, raise an error (should not happen with valid input)
        if not assigned:
            raise ValueError("Unable to assign all replicas with the given VM capacities.")
    
    return allocation