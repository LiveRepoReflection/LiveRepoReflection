def allocate_vms(vm_instances, requests):
    """
    Allocate VMs to requests in order to maximize the number of satisfied requests and minimize cost.
    
    vm_instances: List of tuples (cpu_cores, ram_gb, disk_gb, cost_per_unit_time).
    requests: List of tuples (request_id, cpu_cores, ram_gb, disk_gb, priority, deadline_timestamp).
    
    Returns:
        A dictionary mapping request IDs to indices of allocated VM instances.
        If a request cannot be satisfied, it is not included in the resulting dictionary.
    """
    # Sort requests by descending priority, then by ascending deadline, then by request_id (for stability)
    sorted_requests = sorted(requests, key=lambda r: (-r[4], r[5], r[0]))
    allocation = {}
    # Maintain a set of available VM indices
    available_vms = set(range(len(vm_instances)))
    
    # Greedily assign VMs to requests based on the sorted order.
    for req in sorted_requests:
        req_id, req_cpu, req_ram, req_disk, priority, deadline = req
        best_vm_index = None
        best_cost = None
        # Iterate over available VM instances to find a candidate that satisfies the request.
        for i in available_vms:
            vm_cpu, vm_ram, vm_disk, base_cost = vm_instances[i]
            if vm_cpu >= req_cpu and vm_ram >= req_ram and vm_disk >= req_disk:
                # Compute the waste penalty
                cpu_waste = vm_cpu - req_cpu
                ram_waste = vm_ram - req_ram
                disk_waste = vm_disk - req_disk
                waste_penalty = cpu_waste + ram_waste + disk_waste
                total_cost = base_cost + waste_penalty
                # Update candidate if cost is lower, or if equal cost, choose lower index.
                if best_cost is None or total_cost < best_cost:
                    best_cost = total_cost
                    best_vm_index = i
                elif total_cost == best_cost and i < best_vm_index:
                    best_vm_index = i
        if best_vm_index is not None:
            allocation[req_id] = best_vm_index
            available_vms.remove(best_vm_index)
    return allocation

if __name__ == '__main__':
    # Example usage
    vm_instances = [
        (2, 4, 50, 10),   # VM Instance 0
        (4, 8, 100, 20),  # VM Instance 1
        (8, 16, 200, 35)  # VM Instance 2
    ]
    requests = [
        (1, 1, 2, 20, 5, 1678886400),
        (2, 3, 6, 70, 8, 1678886400),
        (3, 6, 12, 150, 2, 1678886400)
    ]
    allocation = allocate_vms(vm_instances, requests)
    print("Allocation:", allocation)