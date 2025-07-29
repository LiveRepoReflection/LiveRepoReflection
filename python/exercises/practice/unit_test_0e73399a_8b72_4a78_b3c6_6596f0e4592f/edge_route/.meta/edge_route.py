def find_optimal_route(graph, node_resources, link_latencies, stage_requirements, eligible_nodes, deadline):
    """
    Finds the optimal route for executing a task on a distributed edge computing platform.

    Args:
        graph: A dictionary representing the directed graph. Keys are node IDs, and values are lists of neighboring node IDs.
        node_resources: A dictionary representing the available resources for each node. Keys are node IDs, and values are tuples (CPU, Memory).
        link_latencies: A dictionary representing the communication latency between nodes. Keys are tuples (node1, node2), and values are the latency.
        stage_requirements: A list of tuples representing the resource requirements for each stage. Each tuple is (CPU, Memory).
        eligible_nodes: A list of lists representing the eligible nodes for each stage.
        deadline: The maximum allowed execution time (total latency).

    Returns:
        A list of node IDs representing the optimal route, or an empty list if no feasible route exists.
    """
    best = [float('inf'), None]  # best[0]: minimum latency, best[1]: best route

    def dfs(stage, current_route, current_cost, resource_usage):
        nonlocal best
        if stage == len(stage_requirements):
            if current_cost < best[0]:
                best = [current_cost, current_route.copy()]
            return

        cpu_req, mem_req = stage_requirements[stage]
        for candidate in eligible_nodes[stage]:
            used_cpu, used_mem = resource_usage.get(candidate, (0, 0))
            available_cpu, available_mem = node_resources[candidate]
            if used_cpu + cpu_req > available_cpu or used_mem + mem_req > available_mem:
                continue

            # For stages beyond the first, check that there is a direct edge from the previous node.
            if stage > 0:
                prev = current_route[-1]
                if candidate not in graph.get(prev, []):
                    continue
                if (prev, candidate) not in link_latencies:
                    continue
                transition_cost = link_latencies[(prev, candidate)]
            else:
                transition_cost = 0

            new_cost = current_cost + transition_cost
            if new_cost > deadline or new_cost >= best[0]:
                continue

            # Update resource usage for the candidate node
            new_resource_usage = dict(resource_usage)
            new_resource_usage[candidate] = (used_cpu + cpu_req, used_mem + mem_req)

            current_route.append(candidate)
            dfs(stage + 1, current_route, new_cost, new_resource_usage)
            current_route.pop()

    dfs(0, [], 0, {})
    if best[1] is None or best[0] > deadline:
        return []
    return best[1]