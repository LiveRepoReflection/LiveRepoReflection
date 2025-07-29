import heapq
import math

def calculate_travel_time(edge, current_hour):
    speed_kmh = edge['speed_limit']
    length_km = edge['length'] / 1000
    congestion = edge['congestion_factors'][current_hour % 24]
    return (length_km / speed_kmh) * congestion

def haversine_distance(coord1, coord2):
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat/2) * math.sin(dlat/2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon/2) * math.sin(dlon/2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def find_optimal_path(graph, start_node, destination_node, departure_time, max_budget, earliest_arrival, latest_arrival, alpha):
    if start_node == destination_node:
        return ([start_node], 0.0, graph[start_node]['traffic_density'], 0)

    open_set = []
    heapq.heappush(open_set, (0, 0, departure_time, start_node, [], 0, 0))
    
    visited = {}
    visited[(start_node, 0)] = (0, 0, departure_time, [])

    while open_set:
        _, current_cost, current_time, current_node, path, current_risk, current_toll = heapq.heappop(open_set)

        if current_node == destination_node:
            if earliest_arrival <= (current_time - departure_time) <= latest_arrival:
                return (path + [current_node], current_time - departure_time, current_risk, current_toll)
            continue

        if current_time - departure_time > latest_arrival:
            continue

        for neighbor, edge in graph[current_node]['edges'].items():
            if current_toll + edge['toll_cost'] > max_budget:
                continue

            travel_time = calculate_travel_time(edge, int(current_time))
            arrival_time = current_time + travel_time
            new_toll = current_toll + edge['toll_cost']
            new_risk = current_risk + graph[neighbor]['traffic_density']
            
            cost = alpha * new_risk + (1 - alpha) * (arrival_time - departure_time)

            if (neighbor, new_toll) not in visited or cost < visited[(neighbor, new_toll)][0]:
                visited[(neighbor, new_toll)] = (cost, new_risk, arrival_time, path + [current_node])
                heuristic = haversine_distance(graph[neighbor]['coordinates'], graph[destination_node]['coordinates']) / 50
                heapq.heappush(open_set, (cost + heuristic, cost, arrival_time, neighbor, path + [current_node], new_risk, new_toll))

    return ([], 0.0, 0.0, 0)