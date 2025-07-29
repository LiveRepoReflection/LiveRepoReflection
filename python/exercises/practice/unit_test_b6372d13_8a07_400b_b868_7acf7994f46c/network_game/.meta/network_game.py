import heapq
import copy

MAX_ITERATIONS = 1000

def simulate_nash_equilibrium(graph, congestion_functions, start_nodes, end_nodes):
    num_agents = len(start_nodes)
    # Initial assignment: For each agent, compute the shortest path given initial congestion (which is 0 on all edges).
    # Global congestion counts: dictionary mapping edge_id -> count
    global_congestion = {edge_id: 0 for edge_id in congestion_functions}
    # Store paths for each agent (list of edge_ids)
    agent_paths = [None] * num_agents

    # Helper: compute cost of a path given a base congestion (for an agent who is added).
    def compute_path_cost(path, eff_congestion):
        total = 0
        for eid in path:
            a, b = congestion_functions[eid]
            # cost when agent uses this edge: effective congestion + 1
            total += a * (eff_congestion.get(eid, 0) + 1) + b
        return total

    # Dijkstra that returns tuple: (total_cost, path as list of edge_ids)
    def dijkstra(start, end, eff_congestion):
        # Each state: (total_cost, count_edges, path as tuple, current_node)
        heap = []
        heapq.heappush(heap, (0, 0, (), start))
        # visited dictionary holds the best cost found for (node, count_edges, path) but we only need cost comparison keyed on node with tie-breaking.
        best = {}
        while heap:
            cost, count_edges, path, node = heapq.heappop(heap)
            if node == end:
                return cost, list(path)
            # If visited with a better cost (or same cost and better tie-break), skip.
            if node in best:
                prev = best[node]
                # If the current cost is greater than previously found, skip.
                if cost > prev[0]:
                    continue
                # If cost equal but count_edges is more, skip.
                if cost == prev[0] and count_edges >= prev[1]:
                    continue
            best[node] = (cost, count_edges)
            for nbr, eid in graph.get(node, []):
                a, b = congestion_functions[eid]
                # When taking this edge, the effective congestion for the agent will be current count + 1 (agent adding itself).
                edge_cost = a * (eff_congestion.get(eid, 0) + 1) + b
                new_cost = cost + edge_cost
                new_path = path + (eid,)
                new_count = count_edges + 1
                heapq.heappush(heap, (new_cost, new_count, new_path, nbr))
        # If no path found, return None values.
        return None, None

    # Initialize each agent's path
    for i in range(num_agents):
        # For each agent, effective congestion is global_congestion (since agent not added)
        eff_congestion = copy.deepcopy(global_congestion)
        cost, path = dijkstra(start_nodes[i], end_nodes[i], eff_congestion)
        if path is None:
            # If no path found, assign empty list.
            agent_paths[i] = []
        else:
            agent_paths[i] = path
            # Update global congestion counts with this new path.
            for eid in path:
                global_congestion[eid] += 1

    iterations = 0
    while iterations < MAX_ITERATIONS:
        iterations += 1
        changes = 0
        # For each agent, re-evaluate its best path.
        for i in range(num_agents):
            # Remove this agent's contribution temporarily.
            eff_congestion = copy.deepcopy(global_congestion)
            if agent_paths[i]:
                for eid in agent_paths[i]:
                    eff_congestion[eid] -= 1
            # Compute the best path using dijkstra.
            new_cost, new_path = dijkstra(start_nodes[i], end_nodes[i], eff_congestion)
            if new_path is None:
                # If no path is available, skip update.
                new_cost = float('inf')
                new_path = []
            # Compute current path cost.
            current_cost = compute_path_cost(agent_paths[i] if agent_paths[i] is not None else [], eff_congestion)
            # Compare costs. If new path has lower cost, or equal cost but better tie-break conditions, update.
            update = False
            if new_cost < current_cost:
                update = True
            elif new_cost == current_cost:
                # Tie-breaking: first by number of edges, then lexicographical order.
                curr_length = len(agent_paths[i]) if agent_paths[i] is not None else float('inf')
                new_length = len(new_path)
                if new_length < curr_length:
                    update = True
                elif new_length == curr_length:
                    # Compare lexicographically.
                    if tuple(new_path) < tuple(agent_paths[i] if agent_paths[i] is not None else ()):
                        update = True
            if update:
                # Update global congestion: remove old path contribution and add new path.
                if agent_paths[i]:
                    for eid in agent_paths[i]:
                        global_congestion[eid] -= 1
                for eid in new_path:
                    global_congestion[eid] += 1
                agent_paths[i] = new_path
                changes += 1
        if changes == 0:
            break
    # Return final assignment of paths.
    return agent_paths