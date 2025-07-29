import heapq
from collections import defaultdict
import math

def optimize_multi_commodity_flow(nodes, edges, commodities):
    """
    Optimize the flow of multiple commodities through a network using a specialized
    Frank-Wolfe algorithm for multi-commodity flow problems with dynamic edge costs.
    
    Args:
        nodes (list): List of node identifiers in the graph.
        edges (dict): Adjacency list representation of the graph.
                     Keys are node identifiers, values are lists of tuples (neighbor, cost_function).
                     Cost function is a list of (flow, cost) pairs representing a piecewise linear function.
        commodities (list): List of tuples (source, destination, demand) for each commodity.
    
    Returns:
        dict: A dictionary where keys are commodity indices and values are dictionaries mapping
              edges (as tuples of source-destination nodes) to the flow of that commodity on that edge.
    """
    # Initialize the flow for each commodity on each edge to 0
    num_commodities = len(commodities)
    flow = defaultdict(lambda: defaultdict(float))
    
    # Initialize total flow on each edge
    total_flow = defaultdict(float)
    
    # Check if the problem has a feasible solution
    for k, (source, dest, demand) in enumerate(commodities):
        if not has_path(nodes, edges, source, dest):
            # No feasible solution, return empty flows
            return {k: {} for k in range(num_commodities)}
    
    # Create a list of all edges in the network
    all_edges = []
    for u in nodes:
        for v, _ in edges.get(u, []):
            all_edges.append((u, v))
    
    # Frank-Wolfe algorithm parameters
    max_iterations = 100
    convergence_threshold = 1e-4
    
    # Main Frank-Wolfe algorithm loop
    for iteration in range(max_iterations):
        # Compute marginal costs for each edge based on current total flow
        marginal_costs = {}
        for u, v in all_edges:
            cost_function = next(cf for n, cf in edges[u] if n == v)
            marginal_costs[(u, v)] = calculate_marginal_cost(total_flow[(u, v)], cost_function)
        
        # Find the direction of steepest descent for each commodity (shortest path)
        direction = {}
        for k, (source, dest, demand) in enumerate(commodities):
            shortest_path = find_shortest_path(nodes, edges, source, dest, marginal_costs)
            if not shortest_path:
                # No path found, which should not happen if we checked feasibility correctly
                continue
                
            # Convert path to edge flows
            direction[k] = defaultdict(float)
            for i in range(len(shortest_path) - 1):
                u, v = shortest_path[i], shortest_path[i + 1]
                direction[k][(u, v)] = demand
        
        # Compute the step size using line search
        step_size = line_search(flow, direction, total_flow, edges, commodities)
        
        # Update flows
        new_total_flow = defaultdict(float)
        objective_before = calculate_objective(flow, total_flow, edges)
        
        # Update flows for each commodity
        for k in range(num_commodities):
            if k not in direction:
                continue
                
            for edge, dir_flow in direction[k].items():
                flow[k][edge] = (1 - step_size) * flow[k][edge] + step_size * dir_flow
                new_total_flow[edge] += flow[k][edge]
        
        # Update total flows
        total_flow = new_total_flow
        
        # Check for convergence
        objective_after = calculate_objective(flow, total_flow, edges)
        if abs(objective_after - objective_before) < convergence_threshold:
            break
    
    # Clean up the result by removing negligible flows and formatting
    result = {}
    for k in range(num_commodities):
        result[k] = {edge: flow_val for edge, flow_val in flow[k].items() if flow_val > 1e-6}
    
    # Ensure all flow conservation constraints are satisfied
    return adjust_flows_for_conservation(result, commodities)

def has_path(nodes, edges, source, dest):
    """Check if there's a path from source to destination."""
    visited = set()
    queue = [source]
    
    while queue:
        node = queue.pop(0)
        if node == dest:
            return True
        
        if node in visited:
            continue
            
        visited.add(node)
        for neighbor, _ in edges.get(node, []):
            if neighbor not in visited:
                queue.append(neighbor)
    
    return False

def calculate_cost(flow, cost_function):
    """Calculate the cost per unit flow based on a piecewise linear function."""
    if flow <= 0:
        return cost_function[0][1]
    
    for i in range(len(cost_function) - 1):
        flow1, cost1 = cost_function[i]
        flow2, cost2 = cost_function[i + 1]
        
        if flow1 <= flow <= flow2:
            # Linear interpolation
            return cost1 + (flow - flow1) * (cost2 - cost1) / (flow2 - flow1)
    
    # If flow exceeds the maximum defined point, use the last cost
    return cost_function[-1][1]

def calculate_marginal_cost(flow, cost_function):
    """
    Calculate the marginal cost (derivative of the cost function)
    for a given flow value using the piecewise linear cost function.
    """
    if len(cost_function) == 1:
        # Constant cost function
        return cost_function[0][1]
    
    for i in range(len(cost_function) - 1):
        flow1, cost1 = cost_function[i]
        flow2, cost2 = cost_function[i + 1]
        
        if flow1 <= flow <= flow2:
            # Slope of the linear segment
            return (cost2 - cost1) / (flow2 - flow1)
    
    # If flow exceeds the maximum defined point, use the slope of the last segment
    if len(cost_function) > 1:
        flow_n_minus_1, cost_n_minus_1 = cost_function[-2]
        flow_n, cost_n = cost_function[-1]
        return (cost_n - cost_n_minus_1) / (flow_n - flow_n_minus_1)
    
    return 0  # Default marginal cost for constant function

def find_shortest_path(nodes, edges, source, dest, edge_costs):
    """
    Find the shortest path from source to destination using Dijkstra's algorithm
    with the given edge costs.
    """
    # Initialize distances with infinity for all nodes except the source
    distances = {node: float('infinity') for node in nodes}
    distances[source] = 0
    
    # Initialize previous node dictionary for path reconstruction
    previous = {node: None for node in nodes}
    
    # Priority queue for Dijkstra's algorithm
    pq = [(0, source)]
    
    # Set to keep track of visited nodes
    visited = set()
    
    while pq:
        current_distance, current_node = heapq.heappop(pq)
        
        # Skip if we've already processed this node
        if current_node in visited:
            continue
            
        visited.add(current_node)
        
        # If we've reached the destination, we can stop
        if current_node == dest:
            break
        
        # Check all neighbors of the current node
        for neighbor, _ in edges.get(current_node, []):
            # Skip if this neighbor has already been visited
            if neighbor in visited:
                continue
                
            edge = (current_node, neighbor)
            edge_cost = edge_costs.get(edge, float('infinity'))
            
            # Calculate new distance to neighbor
            distance = current_distance + edge_cost
            
            # If we found a shorter path to the neighbor, update it
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_node
                heapq.heappush(pq, (distance, neighbor))
    
    # Reconstruct the path
    if distances[dest] == float('infinity'):
        return []  # No path found
        
    path = []
    current = dest
    while current is not None:
        path.append(current)
        current = previous[current]
    
    # Reverse the path to get it in the correct order
    path.reverse()
    
    return path

def calculate_objective(flow, total_flow, edges):
    """Calculate the total cost of the current flow assignment."""
    total_cost = 0
    
    for edge, edge_flow in total_flow.items():
        u, v = edge
        cost_function = next(cf for n, cf in edges[u] if n == v)
        cost = calculate_cost(edge_flow, cost_function)
        total_cost += cost * edge_flow
    
    return total_cost

def line_search(flow, direction, total_flow, edges, commodities):
    """
    Perform a line search to find the step size that minimizes the objective function.
    """
    # Simple line search using golden section search
    golden_ratio = (math.sqrt(5) - 1) / 2
    a, b = 0, 1  # Search interval [0, 1]
    tol = 1e-4  # Tolerance
    
    c = b - golden_ratio * (b - a)
    d = a + golden_ratio * (b - a)
    
    while abs(b - a) > tol:
        # Evaluate objective function at points c and d
        fc = evaluate_objective_at_step(flow, direction, total_flow, edges, c)
        fd = evaluate_objective_at_step(flow, direction, total_flow, edges, d)
        
        if fc < fd:
            b = d
        else:
            a = c
            
        # Update c and d
        c = b - golden_ratio * (b - a)
        d = a + golden_ratio * (b - a)
    
    # Return the midpoint of the final interval
    return (a + b) / 2

def evaluate_objective_at_step(flow, direction, total_flow, edges, step):
    """Evaluate the objective function at a given step size."""
    # Calculate new flows with the given step size
    new_total_flow = defaultdict(float)
    
    for k, commodity_flow in flow.items():
        if k not in direction:
            for edge, f in commodity_flow.items():
                new_total_flow[edge] += f
        else:
            for edge in set(commodity_flow.keys()) | set(direction[k].keys()):
                new_flow = (1 - step) * commodity_flow.get(edge, 0) + step * direction[k].get(edge, 0)
                new_total_flow[edge] += new_flow
    
    # Calculate the objective value with new flows
    total_cost = 0
    for edge, edge_flow in new_total_flow.items():
        u, v = edge
        cost_function = next(cf for n, cf in edges[u] if n == v)
        cost = calculate_cost(edge_flow, cost_function)
        total_cost += cost * edge_flow
    
    return total_cost

def adjust_flows_for_conservation(flow_result, commodities):
    """
    Adjust flows to ensure flow conservation constraints are satisfied.
    This is a post-processing step to handle numerical imprecisions.
    """
    adjusted_result = {}
    
    for k, (source, dest, demand) in enumerate(commodities):
        if k not in flow_result:
            adjusted_result[k] = {}
            continue
            
        edges_flow = flow_result[k]
        
        # If there's no flow (infeasible problem), skip adjustment
        if not edges_flow:
            adjusted_result[k] = {}
            continue
        
        # Build a graph from the edges with flow
        graph = defaultdict(list)
        for (u, v), flow_val in edges_flow.items():
            if flow_val > 0:
                graph[u].append(v)
        
        # Find all paths from source to destination
        paths = find_all_paths(graph, source, dest)
        
        # If no paths found, return empty flow for this commodity
        if not paths:
            adjusted_result[k] = {}
            continue
        
        # Assign flow proportionally to each path
        path_flows = distribute_flow_to_paths(paths, demand)
        
        # Convert path flows back to edge flows
        edge_flows = defaultdict(float)
        for path, path_flow in path_flows.items():
            path_nodes = path.split('->')
            for i in range(len(path_nodes) - 1):
                u, v = path_nodes[i], path_nodes[i + 1]
                edge_flows[(u, v)] += path_flow
        
        adjusted_result[k] = dict(edge_flows)
    
    return adjusted_result

def find_all_paths(graph, start, end, path=None, all_paths=None):
    """Find all paths from start to end in the graph using DFS."""
    if path is None:
        path = []
    if all_paths is None:
        all_paths = []
    
    path = path + [start]
    
    if start == end:
        all_paths.append('->'.join(path))
        return all_paths
    
    for node in graph.get(start, []):
        if node not in path:  # Prevent cycles
            find_all_paths(graph, node, end, path, all_paths)
    
    return all_paths

def distribute_flow_to_paths(paths, total_flow):
    """Distribute the total flow among the available paths."""
    num_paths = len(paths)
    path_flows = {}
    
    # Simple uniform distribution for now
    flow_per_path = total_flow / num_paths
    
    for path in paths:
        path_flows[path] = flow_per_path
    
    return path_flows