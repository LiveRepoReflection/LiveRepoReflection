import heapq
import math

def dijkstra(city_map, source, destination):
    # Each element in heap: (total_cost, hops, current_node, path)
    heap = [(0, 0, source, [source])]
    # dist[node] = (cost, hops) best found so far.
    dist = {source: (0, 0)}
    
    while heap:
        cost, hops, node, path = heapq.heappop(heap)
        if node == destination:
            return cost, path
        if cost > dist.get(node, (math.inf, math.inf))[0]:
            continue
        for neighbor, weight in city_map.get(node, []):
            new_cost = cost + weight
            new_hops = hops + 1
            # lexicographical order: first by cost then by hops
            if (new_cost, new_hops) < dist.get(neighbor, (math.inf, math.inf)):
                dist[neighbor] = (new_cost, new_hops)
                heapq.heappush(heap, (new_cost, new_hops, neighbor, path + [neighbor]))
    return None, None

def insert_cycle(route, index, cycle, k):
    # Insert the cycle 'k' times at position index in the route.
    # route: list, cycle: list that starts and ends with same vertex.
    new_route = route[:index+1]
    for _ in range(k):
        new_route.extend(cycle[1:])  # avoid duplicating the starting vertex in subsequent cycles
    new_route.extend(route[index+1:])
    return new_route

def optimize_routes(city_map, packages, time_windows):
    # Priority mapping: lower number means higher priority.
    priority_rank = {"high": 0, "medium": 1, "low": 2}
    # Prepare packages with original index and sort them.
    packaged = []
    for idx, pkg in enumerate(packages):
        src, dst, priority = pkg
        packaged.append((priority_rank[priority], idx, src, dst, priority))
    # Sort by priority then by original index.
    packaged.sort(key=lambda x: (x[0], x[1]))
    
    # To enforce ordering constraint among priority groups,
    # For packages in a lower priority group, the chosen route cost must be
    # at least the maximum cost among delivered packages in higher priority groups.
    global_lower_bound = 0
    # To store result: mapping original index -> route (list of nodes)
    delivered = {}
    # For storing computed cost for delivered packages (original index -> cost)
    delivered_cost = {}
    # Group packages by priority rank.
    current_priority = None
    current_group_max = 0

    for prio, idx, src, dst, priority in packaged:
        # When moving to new priority group, update the global lower bound.
        if current_priority is None:
            current_priority = prio
        elif prio != current_priority:
            global_lower_bound = max(global_lower_bound, current_group_max)
            current_priority = prio
            current_group_max = 0

        # Get time window constraint if exists.
        time_constraint = time_windows.get((src, dst), None)
        tw_low = None
        tw_high = None
        if time_constraint is not None:
            tw_low, tw_high = time_constraint

        # First, compute the unconstrained shortest route.
        if src == dst:
            base_cost = 0
            base_route = [src]
        else:
            base_cost, base_route = dijkstra(city_map, src, dst)
            if base_route is None:
                # No path exists
                continue

        # The desired lower bound for cost: must be at least global_lower_bound.
        desired_lb = global_lower_bound
        # If time window exists, also must be at least TW_low.
        if tw_low is not None:
            desired_lb = max(desired_lb, tw_low)
        final_cost = base_cost
        final_route = base_route[:]
        # If unconstrained cost is lower than the desired lower bound, try to insert cycles.
        if final_cost < desired_lb:
            # Find minimum cycle cost along the base route.
            min_cycle_cost = math.inf
            chosen_cycle = None
            chosen_index = None
            # For each vertex in the base_route, check possibility of a 2-node cycle.
            for i, v in enumerate(base_route):
                neighbors = city_map.get(v, [])
                if neighbors:
                    # In undirected graph, a 2-node cycle is: v -> u -> v, cost = 2 * weight.
                    local_min = min([2 * weight for u, weight in neighbors])
                    if local_min < min_cycle_cost:
                        min_cycle_cost = local_min
                        # Also store the corresponding neighbor for cycle creation.
                        # Get the neighbor corresponding to the minimal edge.
                        for u, weight in neighbors:
                            if 2 * weight == local_min:
                                chosen_cycle = [v, u, v]
                                break
                        chosen_index = i
            if min_cycle_cost == math.inf:
                # No cycle available to increase cost.
                continue
            # Calculate number of cycles needed.
            extra_needed = desired_lb - final_cost
            k = math.ceil(extra_needed / min_cycle_cost)
            tentative_cost = final_cost + k * min_cycle_cost
            # If time window upper bound exists, ensure tentative_cost <= tw_high.
            if tw_high is not None and tentative_cost > tw_high:
                continue
            final_cost = tentative_cost
            # Insert the cycle k times at the chosen index.
            final_route = insert_cycle(final_route, chosen_index, chosen_cycle, k)

        # After cycle insertion, if time window exists, check upper bound.
        if tw_high is not None and final_cost > tw_high:
            continue

        # Save the delivered package.
        delivered[idx] = final_route
        delivered_cost[idx] = final_cost
        current_group_max = max(current_group_max, final_cost)
    return delivered