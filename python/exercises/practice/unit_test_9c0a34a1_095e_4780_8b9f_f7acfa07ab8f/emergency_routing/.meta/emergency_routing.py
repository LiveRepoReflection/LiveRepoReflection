import heapq
from collections import defaultdict

def dijkstra(graph, start):
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    heap = [(0, start)]
    
    while heap:
        current_dist, current_node = heapq.heappop(heap)
        
        if current_dist > distances[current_node]:
            continue
            
        for neighbor, weight in graph.get(current_node, {}).items():
            distance = current_dist + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(heap, (distance, neighbor))
    
    return distances

def optimal_routing(graph, fire_stations, emergencies):
    if not emergencies:
        return {}
        
    # Precompute distances from all fire stations to all nodes
    station_distances = {}
    for station in fire_stations:
        station_distances[station] = dijkstra(graph, station)
    
    # Create list of available trucks per station
    available_trucks = defaultdict(int)
    for station, count in fire_stations.items():
        available_trucks[station] = count
    
    # For each emergency, find the best available station
    assignments = {}
    emergency_counts = defaultdict(int)
    
    # Count occurrences of each emergency location
    for emergency in emergencies:
        emergency_counts[emergency] += 1
    
    # Process emergencies in order of most frequent first
    sorted_emergencies = sorted(emergency_counts.items(), key=lambda x: -x[1])
    
    for emergency, count in sorted_emergencies:
        # Find all stations that can reach this emergency
        reachable_stations = []
        for station in fire_stations:
            if emergency in station_distances[station] and available_trucks[station] > 0:
                reachable_stations.append((
                    station_distances[station][emergency],
                    station
                ))
        
        if not reachable_stations:
            return None
        
        # Sort stations by distance to emergency
        reachable_stations.sort()
        
        # Assign trucks to this emergency
        remaining = count
        for dist, station in reachable_stations:
            assign = min(remaining, available_trucks[station])
            if assign > 0:
                for _ in range(assign):
                    assignments[emergency] = station
                available_trucks[station] -= assign
                remaining -= assign
                if remaining == 0:
                    break
        
        if remaining > 0:
            return None
    
    return assignments