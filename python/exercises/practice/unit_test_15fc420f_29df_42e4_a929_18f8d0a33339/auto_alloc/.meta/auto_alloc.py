def allocate_resource(request, vm_types, infrastructure):
    # Unpack request parameters
    req_id = request["request_id"]
    req_cpu = request["required_cpu"]
    req_memory = request["required_memory"]
    req_perf = request["expected_performance_score"]
    duration = request["duration"]
    max_latency = request["max_latency"]

    best_allocation = None
    best_cost = float("inf")

    # Iterate over each PM (node)
    for pm in infrastructure["nodes"]:
        # For each VM type that meets the requirements
        for vm in vm_types:
            # Check if the VM type satisfies resource and performance requirements
            if vm["cpu"] < req_cpu or vm["memory"] < req_memory or vm["performance_score"] < req_perf:
                continue

            # Check if the PM has sufficient available resources for the VM type
            if pm["available_cpu"] < vm["cpu"] or pm["available_memory"] < vm["memory"] or pm["available_storage"] < vm["storage"]:
                continue

            # Check latency constraint: if allocation is on a single PM, latency constraint is trivially satisfied.
            # However, if there were already allocated VMs for this request on other PMs,
            # then one would need to check the latency between PMs.
            # For this single-allocation solution, we assume allocation is isolated to one PM.
            # In a multi-VM scenario, additional logic would be needed here.

            # Calculate total cost = (VM cost + PM cost) * duration
            total_cost = (vm["cost_per_hour"] + pm["cost_per_hour"]) * duration

            # Select the allocation with minimum cost
            if total_cost < best_cost:
                best_cost = total_cost
                best_allocation = {
                    "request_id": req_id,
                    "vm_id": vm["id"],
                    "pm_id": pm["id"],
                    "total_cost": best_cost
                }

    if best_allocation is None:
        raise Exception("No suitable allocation found for request: " + req_id)
    
    return best_allocation


if __name__ == "__main__":
    # Sample execution for manual testing
    vm_types = [
        {
            "id": "vm_small",
            "cpu": 2,
            "memory": 4,
            "storage": 50,
            "cost_per_hour": 0.1,
            "performance_score": 100
        },
        {
            "id": "vm_medium",
            "cpu": 4,
            "memory": 8,
            "storage": 100,
            "cost_per_hour": 0.2,
            "performance_score": 200
        },
        {
            "id": "vm_large",
            "cpu": 8,
            "memory": 16,
            "storage": 200,
            "cost_per_hour": 0.4,
            "performance_score": 300
        }
    ]
    
    infrastructure_nodes = [
        {
            "id": "pm1",
            "available_cpu": 8,
            "available_memory": 16,
            "available_storage": 200,
            "cost_per_hour": 0.05
        },
        {
            "id": "pm2",
            "available_cpu": 4,
            "available_memory": 8,
            "available_storage": 100,
            "cost_per_hour": 0.03
        }
    ]
    
    infrastructure_edges = [
        {
            "source": "pm1",
            "destination": "pm2",
            "latency": 10,
            "bandwidth": 100
        },
        {
            "source": "pm2",
            "destination": "pm1",
            "latency": 12,
            "bandwidth": 100
        }
    ]
    
    infrastructure = {
        "nodes": infrastructure_nodes,
        "edges": infrastructure_edges
    }
    
    request = {
        "request_id": "req_main",
        "required_cpu": 2,
        "required_memory": 4,
        "expected_performance_score": 80,
        "max_latency": 15,
        "duration": 5
    }
    
    allocation = allocate_resource(request, vm_types, infrastructure)
    print("Allocation:", allocation)