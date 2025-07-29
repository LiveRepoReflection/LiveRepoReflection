import heapq
from collections import defaultdict, deque
import copy

def solve_flow_network(graph, commodities, time_limit):
    """
    Solves the multi-commodity flow problem with time windows and capacity constraints.
    
    Args:
        graph: Dictionary representing the road network.
        commodities: List of dictionaries representing commodities.
        time_limit: Maximum allowed time for simulation.
    
    Returns:
        Dictionary representing the flow schedule.
    """
    # Create a time-expanded network to handle capacity over time
    time_expanded_graph = create_time_expanded_network(graph, time_limit)
    
    # Sort commodities by end time to prioritize those with tighter deadlines
    sorted_commodities = sorted(enumerate(commodities), key=lambda x: x[1]['end_time'])
    
    solution = {}
    
    # Handle each commodity sequentially
    for commodity_id, commodity in sorted_commodities:
        origin = commodity['origin']
        destination = commodity['destination']
        demand = commodity['demand']
        start_time = commodity['start_time']
        end_time = commodity['end_time']
        
        # Try to find paths for this commodity
        flow_events = route_commodity(time_expanded_graph, origin, destination, demand, 
                                     start_time, end_time, time_limit, graph)
        
        if not flow_events:
            # If we can't route this commodity, there's no feasible solution
            return {}
        
        # Update the remaining capacities in the time-expanded network
        update_network_capacities(time_expanded_graph, flow_events, graph)
        
        solution[commodity_id] = flow_events
    
    # Verify the solution is feasible
    if verify_solution(solution, graph, commodities, time_limit):
        return solution
    else:
        return {}

def create_time_expanded_network(graph, time_limit):
    """
    Creates a time-expanded network to handle flow over time.
    
    Each node in the original graph is expanded to a set of nodes
    (one for each time step), and capacities are tracked per time step.
    """
    time_expanded_graph = {}
    
    for time in range(time_limit + 1):  # +1 to include the time_limit itself
        for node in graph:
            # Create a time-expanded node (node, time)
            time_expanded_node = (node, time)
            time_expanded_graph[time_expanded_node] = []
            
            # Add edges to future time steps
            for neighbor, travel_time, capacity in graph[node]:
                if time + travel_time <= time_limit:
                    future_node = (neighbor, time + travel_time)
                    time_expanded_graph[time_expanded_node].append((future_node, travel_time, capacity))
            
            # Add waiting edge (stay at the same node)
            if time < time_limit:
                next_time_node = (node, time + 1)
                time_expanded_graph[time_expanded_node].append((next_time_node, 1, float('inf')))
    
    return time_expanded_graph

def route_commodity(time_expanded_graph, origin, destination, demand, start_time, end_time, time_limit, original_graph):
    """
    Routes a single commodity through the time-expanded network.
    
    Args:
        time_expanded_graph: The time-expanded network.
        origin: Origin node.
        destination: Destination node.
        demand: Demand to be fulfilled.
        start_time: Earliest start time.
        end_time: Latest end time.
        time_limit: Maximum time limit.
        original_graph: The original graph.
    
    Returns:
        List of flow events or None if routing is not possible.
    """
    flow_events = []
    remaining_demand = demand
    
    while remaining_demand > 0:
        # Find shortest feasible path from origin to destination within time window
        path_info = find_shortest_path(time_expanded_graph, origin, destination, 
                                       start_time, end_time, time_limit)
        
        if not path_info:
            return None  # No feasible path found
        
        time_expanded_path, path_departure_time, min_capacity = path_info
        
        # Convert time-expanded path to original path
        original_path = [node for node, _ in time_expanded_path]
        
        # Calculate the amount that can be sent along this path
        amount = min(remaining_demand, min_capacity)
        
        flow_events.append((path_departure_time, original_path, amount))
        remaining_demand -= amount
        
        # Temporarily reduce capacity on the time-expanded path
        for i in range(len(time_expanded_path) - 1):
            from_node = time_expanded_path[i]
            for j, (to_node, travel_time, capacity) in enumerate(time_expanded_graph[from_node]):
                if to_node == time_expanded_path[i + 1]:
                    time_expanded_graph[from_node][j] = (to_node, travel_time, capacity - amount)
                    break
    
    return flow_events

def find_shortest_path(time_expanded_graph, origin, destination, start_time, end_time, time_limit):
    """
    Finds the shortest feasible path from origin to destination within the time window.
    Uses Dijkstra's algorithm on the time-expanded network.
    
    Returns:
        Tuple of (path, departure_time, min_capacity) or None if no path is found.
    """
    best_path = None
    best_departure_time = None
    best_min_capacity = 0
    best_total_time = float('inf')
    
    # Try different departure times
    for departure_time in range(start_time, min(end_time, time_limit) + 1):
        source = (origin, departure_time)
        
        # Skip if source node doesn't exist in the time-expanded graph
        if source not in time_expanded_graph:
            continue
        
        # Initialize Dijkstra's algorithm
        distances = {node: float('inf') for node in time_expanded_graph}
        distances[source] = 0
        pq = [(0, source)]
        predecessors = {}
        capacities = {}
        
        while pq:
            dist, current = heapq.heappop(pq)
            
            if dist > distances[current]:
                continue
                
            # Found path to destination
            if current[0] == destination and current[1] <= end_time:
                # Reconstruct path
                path = []
                node = current
                min_capacity = float('inf')
                
                while node != source:
                    path.append(node)
                    if node in predecessors:
                        prev = predecessors[node]
                        min_capacity = min(min_capacity, capacities.get((prev, node), float('inf')))
                        node = prev
                    else:
                        # Path reconstruction failed
                        break
                
                if node == source:  # Ensure we reached the source
                    path.append(source)
                    path.reverse()
                    
                    # Calculate total travel time
                    total_time = current[1] - departure_time
                    
                    # Update best path if this is better
                    if total_time < best_total_time and min_capacity > 0:
                        best_path = path
                        best_departure_time = departure_time
                        best_min_capacity = min_capacity
                        best_total_time = total_time
                
                continue
            
            # Explore neighbors
            for neighbor, travel_time, capacity in time_expanded_graph[current]:
                if capacity <= 0:
                    continue  # Skip edges with no capacity
                
                new_dist = dist + travel_time
                
                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    predecessors[neighbor] = current
                    capacities[(current, neighbor)] = capacity
                    heapq.heappush(pq, (new_dist, neighbor))
    
    if best_path:
        return best_path, best_departure_time, best_min_capacity
    return None

def update_network_capacities(time_expanded_graph, flow_events, original_graph):
    """
    Updates the capacities in the time-expanded network after routing a commodity.
    """
    for departure_time, path, amount in flow_events:
        for i in range(len(path) - 1):
            from_node = path[i]
            to_node = path[i+1]
            
            # Find the travel time for this edge in the original graph
            travel_time = None
            for edge in original_graph[from_node]:
                if edge[0] == to_node:
                    travel_time = edge[1]
                    break
            
            if travel_time is None:
                continue  # Edge not found (should not happen)
            
            # Calculate the time at which the flow starts this edge
            edge_time = departure_time
            for j in range(i):
                prev_from, prev_to = path[j], path[j+1]
                for edge in original_graph[prev_from]:
                    if edge[0] == prev_to:
                        edge_time += edge[1]
                        break
            
            # Update capacity for this edge at this time
            te_from_node = (from_node, edge_time)
            if te_from_node in time_expanded_graph:
                for j, (te_to_node, te_travel_time, te_capacity) in enumerate(time_expanded_graph[te_from_node]):
                    if te_to_node[0] == to_node and te_travel_time == travel_time:
                        time_expanded_graph[te_from_node][j] = (te_to_node, te_travel_time, max(0, te_capacity - amount))
                        break

def verify_solution(solution, graph, commodities, time_limit):
    """
    Verifies that the solution is feasible.
    
    Checks:
    1. All demands are satisfied
    2. Capacity constraints are respected
    3. Time windows are respected
    4. All paths are valid
    """
    # Check demand satisfaction
    for commodity_id, flow_events in solution.items():
        commodity = commodities[commodity_id]
        total_flow = sum(amount for _, _, amount in flow_events)
        if total_flow != commodity['demand']:
            return False
    
    # Check time windows and path validity
    for commodity_id, flow_events in solution.items():
        commodity = commodities[commodity_id]
        for departure_time, path, amount in flow_events:
            if departure_time < commodity['start_time']:
                return False
            
            arrival_time = departure_time
            for i in range(len(path) - 1):
                from_node, to_node = path[i], path[i+1]
                
                # Check if edge exists in graph
                edge_found = False
                for edge in graph[from_node]:
                    if edge[0] == to_node:
                        arrival_time += edge[1]
                        edge_found = True
                        break
                
                if not edge_found:
                    return False
            
            if arrival_time > commodity['end_time'] or arrival_time > time_limit:
                return False
    
    # Check capacity constraints
    # Create a timeline of flows for each edge
    edge_timelines = defaultdict(lambda: defaultdict(int))
    
    for commodity_id, flow_events in solution.items():
        for departure_time, path, amount in flow_events:
            edge_time = departure_time
            
            for i in range(len(path) - 1):
                from_node, to_node = path[i], path[i+1]
                
                # Find travel time
                travel_time = None
                capacity = None
                for edge in graph[from_node]:
                    if edge[0] == to_node:
                        travel_time = edge[1]
                        capacity = edge[2]
                        break
                
                if travel_time is None:
                    return False  # Edge not found
                
                # Update flow on this edge for each time unit
                for t in range(edge_time, edge_time + travel_time):
                    if t > time_limit:
                        return False  # Exceeds time limit
                    edge_timelines[(from_node, to_node)][t] += amount
                    
                    # Check capacity constraint
                    if edge_timelines[(from_node, to_node)][t] > capacity:
                        return False
                
                edge_time += travel_time
    
    return True