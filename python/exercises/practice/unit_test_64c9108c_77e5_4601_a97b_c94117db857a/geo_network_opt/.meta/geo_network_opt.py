import heapq

def build_adjacency_list(graph):
    adj = {node: [] for node in graph['nodes']}
    for edge in graph['edges']:
        # Assuming undirected graph
        node1, node2, distance, travel_time = edge
        adj[node1].append((node2, travel_time))
        adj[node2].append((node1, travel_time))
    return adj

def dijkstra(adj, start, service_radius):
    # Returns a set of nodes reachable from 'start' within service_radius (using travel_time)
    dist = {node: float('inf') for node in adj}
    dist[start] = 0
    heap = [(0, start)]
    while heap:
        current_time, node = heapq.heappop(heap)
        if current_time > service_radius:
            continue
        if current_time > dist[node]:
            continue
        for neighbor, travel_time in adj[node]:
            time = current_time + travel_time
            if time < dist[neighbor] and time <= service_radius:
                dist[neighbor] = time
                heapq.heappush(heap, (time, neighbor))
    return {node for node, time in dist.items() if time <= service_radius}

def optimize_network(graph, budget, service_radius, station_capacity_per_population, min_stations):
    """
    Optimize placement of EV charging stations given a graph, budget, service radius,
    a capacity scaling factor, and a required minimum number of stations.
    
    Returns a list of node IDs representing optimized locations. If it's impossible
    to place at least min_stations within budget, returns an empty list.
    """
    nodes_info = graph['nodes']
    # Check if there are at least min_stations available
    if len(nodes_info) < min_stations:
        return []
    
    # Precompute coverage for each node using Dijkstra's algorithm.
    adj = build_adjacency_list(graph)
    coverage_map = {}
    for node in nodes_info:
        reachable = dijkstra(adj, node, service_radius)
        coverage_map[node] = reachable

    # Precompute population for each node for quick lookup.
    populations = {node: info['population'] for node, info in nodes_info.items()}
    
    # Helper to compute total population of a set of nodes.
    def total_population(nodes_set):
        return sum(populations[node] for node in nodes_set)

    # Greedy algorithm for the budgeted maximum coverage problem.
    chosen = set()
    current_covered = set()
    remaining_budget = budget

    # Create a set of candidate nodes
    candidates = set(nodes_info.keys())

    while candidates:
        best_candidate = None
        best_gain_ratio = -1
        best_increment_gain = 0
        best_cost = None

        # Evaluate each candidate that can be installed within the remaining budget.
        for node in candidates:
            cost = nodes_info[node]['installation_cost']
            if cost > remaining_budget:
                continue
            # Compute the union if we add this candidate.
            new_coverage = current_covered | coverage_map[node]
            incremental_nodes = new_coverage - current_covered
            incremental_gain = total_population(incremental_nodes)
            # Use gain per cost unit as score.
            if cost > 0:
                ratio = incremental_gain / cost
            else:
                ratio = float('inf')
            if ratio > best_gain_ratio:
                best_gain_ratio = ratio
                best_candidate = node
                best_increment_gain = incremental_gain
                best_cost = cost

        # If no candidate can be afforded or none gives any gain, break out.
        if best_candidate is None:
            break

        # Add the candidate if it has some positive incremental gain.
        if best_increment_gain <= 0:
            # Even if there is no additional population gain, we might need to meet min_stations.
            break

        chosen.add(best_candidate)
        remaining_budget -= best_cost
        current_covered |= coverage_map[best_candidate]
        candidates.remove(best_candidate)

    # If we have not yet met the minimum station requirement, try to add cheapest stations from the remaining ones.
    if len(chosen) < min_stations:
        additional_candidates = sorted(
            [node for node in nodes_info if node not in chosen and nodes_info[node]['installation_cost'] <= remaining_budget],
            key=lambda x: nodes_info[x]['installation_cost']
        )
        for node in additional_candidates:
            if remaining_budget >= nodes_info[node]['installation_cost']:
                chosen.add(node)
                remaining_budget -= nodes_info[node]['installation_cost']
                current_covered |= coverage_map[node]
                if len(chosen) >= min_stations:
                    break

    # Final check: if we still do not meet the required number of stations, return empty list.
    if len(chosen) < min_stations:
        return []

    # (Optional capacity check can be inserted here if a station's capacity constraint is to be enforced.)
    # For each chosen station, one might compute required capacity = (sum of populations in its coverage) * station_capacity_per_population
    # and verify if it is within acceptable limits. In this implementation, we assume the installation_cost reflects capacity upgrades.
    
    return list(chosen)