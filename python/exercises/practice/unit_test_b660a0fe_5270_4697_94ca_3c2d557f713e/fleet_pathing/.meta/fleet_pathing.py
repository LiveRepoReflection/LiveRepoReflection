import heapq
from collections import defaultdict

def calculate_routes(graph, vehicles, static_obstacles):
    vehicle_dict = {v['vehicle_id']: v for v in vehicles}
    routes = {}
    time_table = defaultdict(dict)  # node: {time: [vehicle_ids]}
    
    # Sort vehicles by priority (lower ID first)
    sorted_vehicles = sorted(vehicles, key=lambda x: x['vehicle_id'])
    
    for vehicle in sorted_vehicles:
        vehicle_id = vehicle['vehicle_id']
        start = vehicle['current_location']
        end = vehicle['destination']
        
        # Check if start or end is an obstacle
        if start in static_obstacles or end in static_obstacles:
            routes[vehicle_id] = None
            continue
            
        # Find shortest path using A* algorithm
        path = a_star(graph, start, end, static_obstacles)
        if not path:
            routes[vehicle_id] = None
            continue
            
        # Check for collisions and adjust path if needed
        adjusted_path = avoid_collisions(vehicle, path, time_table, graph)
        if adjusted_path:
            routes[vehicle_id] = adjusted_path
            # Update time table with this vehicle's path
            update_time_table(vehicle, adjusted_path, time_table, graph)
        else:
            routes[vehicle_id] = None
            
    return routes

def a_star(graph, start, end, obstacles):
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {node: float('inf') for node in graph}
    g_score[start] = 0
    f_score = {node: float('inf') for node in graph}
    f_score[start] = heuristic(start, end)
    
    open_set_hash = {start}
    
    while open_set:
        current = heapq.heappop(open_set)[1]
        open_set_hash.remove(current)
        
        if current == end:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path
            
        for neighbor, edge_data in graph[current]:
            if neighbor in obstacles:
                continue
                
            tentative_g_score = g_score[current] + edge_data['length']
            
            if tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, end)
                if neighbor not in open_set_hash:
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
                    open_set_hash.add(neighbor)
                    
    return None

def heuristic(node, end):
    # Simple heuristic - can be improved with actual coordinates
    return abs(node - end)

def avoid_collisions(vehicle, path, time_table, graph):
    vehicle_id = vehicle['vehicle_id']
    safety_radius = vehicle['safety_radius']
    speed = vehicle['speed']
    acceleration = vehicle['acceleration_rate']
    
    adjusted_path = path.copy()
    current_time = 0
    
    for i in range(len(adjusted_path) - 1):
        current_node = adjusted_path[i]
        next_node = adjusted_path[i + 1]
        edge_data = get_edge_data(graph, current_node, next_node)
        
        if not edge_data:
            return None
            
        length = edge_data['length']
        speed_limit = edge_data['speed_limit']
        max_speed = min(speed + acceleration, speed_limit)
        travel_time = length / max_speed
        
        # Check for collisions at next_node
        for time in time_table[next_node]:
            if abs(time - (current_time + travel_time)) < safety_radius / max_speed:
                for other_vehicle in time_table[next_node][time]:
                    if other_vehicle != vehicle_id:
                        # Try to find alternative path
                        alternative_path = find_alternative_path(
                            vehicle, adjusted_path[:i+1], time_table, graph
                        )
                        if alternative_path:
                            return alternative_path
                        else:
                            return None
                            
        current_time += travel_time
        
    return adjusted_path

def find_alternative_path(vehicle, current_path, time_table, graph):
    current_node = current_path[-1]
    end = vehicle['destination']
    visited = set(current_path)
    
    queue = [(current_node, [])]
    
    while queue:
        node, path = queue.pop(0)
        if node == end:
            return current_path + path
            
        for neighbor, edge_data in graph[node]:
            if neighbor in visited or neighbor in time_table:
                continue
                
            new_path = path + [neighbor]
            queue.append((neighbor, new_path))
            visited.add(neighbor)
            
    return None

def update_time_table(vehicle, path, time_table, graph):
    vehicle_id = vehicle['vehicle_id']
    current_time = 0
    speed = vehicle['speed']
    acceleration = vehicle['acceleration_rate']
    
    for i in range(len(path) - 1):
        current_node = path[i]
        next_node = path[i + 1]
        edge_data = get_edge_data(graph, current_node, next_node)
        
        if not edge_data:
            continue
            
        length = edge_data['length']
        speed_limit = edge_data['speed_limit']
        max_speed = min(speed + acceleration, speed_limit)
        travel_time = length / max_speed
        
        arrival_time = current_time + travel_time
        if arrival_time not in time_table[next_node]:
            time_table[next_node][arrival_time] = []
        time_table[next_node][arrival_time].append(vehicle_id)
        
        current_time = arrival_time

def get_edge_data(graph, node1, node2):
    for neighbor, edge_data in graph.get(node1, []):
        if neighbor == node2:
            return edge_data
    return None