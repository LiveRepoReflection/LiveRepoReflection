import copy
import heapq
from collections import defaultdict, deque

def optimize_traffic_flow(graph, sources, destinations, road_closures, emergency_requests, time):
    """
    Optimizes traffic flow in a city represented as a directed graph.
    
    Args:
        graph: A dictionary representing the directed graph where keys are intersection names,
               and values are dictionaries representing outgoing edges. Each outgoing edge is 
               represented by the destination intersection as the key, and a function 
               capacity_function(time) as the value.
        sources: A list of source intersection names.
        destinations: A list of destination intersection names.
        road_closures: A list of tuples (start_time, end_time, road_start, road_end).
        emergency_requests: A list of tuples (time, source, destination, num_vehicles, path).
        time: An integer representing the current time.
    
    Returns:
        A dictionary representing the optimal traffic flow for the given time.
    """
    # Create a residual graph to work with
    residual_graph = create_residual_graph(graph, road_closures, time)
    
    # Handle emergency vehicles first
    emergency_flow = {}
    for req_time, source, destination, num_vehicles, path in emergency_requests:
        if req_time <= time:
            # Reserve capacity for emergency vehicles along their path
            for i in range(len(path) - 1):
                start, end = path[i], path[i+1]
                if (start, end) in emergency_flow:
                    emergency_flow[(start, end)] += num_vehicles
                else:
                    emergency_flow[(start, end)] = num_vehicles
                
                # Reduce capacity in residual graph
                if start in residual_graph and end in residual_graph[start]:
                    residual_graph[start][end] -= num_vehicles
    
    # Find maximum flow in the remaining residual graph
    max_flow = ford_fulkerson(residual_graph, sources, destinations)
    
    # Combine emergency flow with regular flow
    for edge, flow in emergency_flow.items():
        start, end = edge
        if start in max_flow and end in max_flow[start]:
            max_flow[start][end] += flow
        elif start in max_flow:
            max_flow[start][end] = flow
        else:
            max_flow[start] = {end: flow}
    
    # Convert the flow to the required output format
    result = {}
    for start in max_flow:
        for end, flow in max_flow[start].items():
            result[(start, end)] = flow
    
    return result

def create_residual_graph(graph, road_closures, time):
    """
    Creates a residual graph based on the original graph, with capacities at the given time
    and considering road closures.
    """
    residual_graph = {}
    
    # Set up nodes and capacities
    for node, edges in graph.items():
        residual_graph[node] = {}
        for target, capacity_function in edges.items():
            # Get capacity at the current time
            capacity = capacity_function(time)
            residual_graph[node][target] = capacity
    
    # Apply road closures
    for start_time, end_time, road_start, road_end in road_closures:
        if start_time <= time <= end_time:
            if road_start in residual_graph and road_end in residual_graph[road_start]:
                residual_graph[road_start][road_end] = 0
    
    return residual_graph

def ford_fulkerson(graph, sources, destinations):
    """
    Implements the Ford-Fulkerson algorithm to find the maximum flow.
    Returns a graph where each edge has a flow value.
    """
    # Create a flow graph initialized with zero flow
    flow = {}
    for node in graph:
        flow[node] = {}
        for target in graph[node]:
            flow[node][target] = 0
    
    # Add a super source and super sink to simplify the algorithm
    super_source = "super_source"
    super_sink = "super_sink"
    
    # Augment the graph with super source and super sink
    augmented_graph = copy.deepcopy(graph)
    augmented_graph[super_source] = {}
    for source in sources:
        augmented_graph[super_source][source] = float('inf')
    
    for destination in destinations:
        if destination not in augmented_graph:
            augmented_graph[destination] = {}
        augmented_graph[destination][super_sink] = float('inf')
    
    # Augment the flow graph too
    flow[super_source] = {}
    for source in sources:
        flow[super_source][source] = 0
    
    if super_sink not in flow:
        flow[super_sink] = {}
    for destination in destinations:
        if destination not in flow:
            flow[destination] = {}
        flow[destination][super_sink] = 0
    
    # Find paths and augment flow until no more paths are found
    while True:
        # Find an augmenting path
        path, bottleneck = find_augmenting_path(augmented_graph, flow, super_source, super_sink)
        if not path:
            break
        
        # Augment flow along the path
        augment_flow(flow, path, bottleneck)
    
    # Remove super source and super sink from the flow graph
    del flow[super_source]
    for node in flow:
        if super_sink in flow[node]:
            del flow[node][super_sink]
    
    return flow

def find_augmenting_path(graph, flow, start, end):
    """
    Finds an augmenting path from start to end using BFS.
    Returns the path and the bottleneck capacity.
    """
    visited = set([start])
    queue = deque([(start, [])])
    parent = {start: None}
    
    while queue:
        current, path = queue.popleft()
        
        if current == end:
            # Found a path to the end
            path.append(current)
            bottleneck = find_bottleneck(graph, flow, path)
            return path, bottleneck
        
        for neighbor in graph.get(current, {}):
            # Check if there's residual capacity
            residual_capacity = graph[current][neighbor] - flow[current].get(neighbor, 0)
            if residual_capacity > 0 and neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [current]))
                parent[neighbor] = current
    
    # No path found
    return None, 0

def find_bottleneck(graph, flow, path):
    """
    Finds the bottleneck capacity of a path.
    """
    bottleneck = float('inf')
    for i in range(len(path) - 1):
        current, next_node = path[i], path[i + 1]
        residual_capacity = graph[current][next_node] - flow[current].get(next_node, 0)
        bottleneck = min(bottleneck, residual_capacity)
    return bottleneck

def augment_flow(flow, path, bottleneck):
    """
    Augments the flow along a path by the bottleneck value.
    """
    for i in range(len(path) - 1):
        current, next_node = path[i], path[i + 1]
        if next_node in flow[current]:
            flow[current][next_node] += bottleneck
        else:
            flow[current][next_node] = bottleneck
        
        # Add reverse edge for the residual graph
        if current not in flow[next_node]:
            flow[next_node][current] = 0
        flow[next_node][current] -= bottleneck