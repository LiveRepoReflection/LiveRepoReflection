import time
import collections

def optimize_traffic_flow(graph, demands, max_green_time, time_limit):
    """
    Optimize traffic flow assignments for each time interval.
    
    Parameters:
        graph (dict): A dictionary representing the road network.
                      Keys are source intersections, and values are dictionaries
                      where keys are destination intersections and values are road capacities.
        demands (list): A list of traffic demand patterns. Each pattern is a matrix (list of lists)
                        where demands[t][i][j] is the traffic demand from intersection i to j.
        max_green_time (int): Maximum green light time allowed at each intersection per interval.
        time_limit (int): Maximum time in seconds allowed for execution.
    
    Returns:
        list: A list of dictionaries representing traffic flow assignments for each time interval.
              Each dictionary's keys are tuples (source, destination) and values are the assigned flow.
    """
    overall_start = time.time()
    num_intervals = len(demands)
    assignments_overall = []

    # Process each time interval.
    for interval in range(num_intervals):
        # Check for time limit.
        if time.time() - overall_start > time_limit:
            break

        demand_matrix = demands[interval]
        # Initialize residual capacities as a copy of graph capacities for this interval.
        residual = {u: dict(graph[u]) for u in graph}
        # Initialize assignment for this interval: set flow=0 for each road.
        assignment = {}
        for u in graph:
            for v in graph[u]:
                assignment[(u, v)] = 0
        # Initialize green time limits per intersection.
        green_limit = {node: max_green_time for node in graph}
        n = len(demand_matrix)

        # Process each Origin-Destination pair (i -> j) with a positive demand.
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                demand_value = demand_matrix[i][j]
                if demand_value <= 0:
                    continue
                # Limit available flow from the source by its remaining green time.
                available_from_source = green_limit.get(i, 0)
                if available_from_source <= 0:
                    continue
                allowable_demand = min(demand_value, available_from_source)
                # Find a viable path from i to j based on available residual capacity.
                path = bfs_find_path(residual, i, j)
                if not path:
                    continue
                # Determine the bottleneck capacity along the found path.
                bottleneck = min(residual[u][v] for u, v in zip(path, path[1:]))
                flow_to_assign = min(allowable_demand, bottleneck)
                if flow_to_assign <= 0:
                    continue
                # Assign the flow along each edge in the path.
                for u, v in zip(path, path[1:]):
                    assignment[(u, v)] += flow_to_assign
                    residual[u][v] -= flow_to_assign
                # Update the source intersection's remaining green time.
                green_limit[i] -= flow_to_assign
        assignments_overall.append(assignment)

    # If time limit was reached and not all intervals processed, fill remaining intervals with empty assignments.
    while len(assignments_overall) < num_intervals:
        assignments_overall.append({})
    return assignments_overall

def bfs_find_path(residual, source, target):
    """
    Finds a path from source to target in the residual graph using BFS.
    
    Parameters:
        residual (dict): Residual capacities represented as a dictionary.
        source (int): The starting intersection.
        target (int): The destination intersection.
    
    Returns:
        list or None: A list of nodes representing the path if found, otherwise None.
    """
    queue = collections.deque()
    queue.append(source)
    parents = {source: None}
    
    while queue:
        current = queue.popleft()
        if current == target:
            # Reconstruct path from source to target.
            path = []
            while current is not None:
                path.append(current)
                current = parents[current]
            return path[::-1]
        for neighbor in residual.get(current, {}):
            if residual[current][neighbor] > 0 and neighbor not in parents:
                parents[neighbor] = current
                queue.append(neighbor)
    return None