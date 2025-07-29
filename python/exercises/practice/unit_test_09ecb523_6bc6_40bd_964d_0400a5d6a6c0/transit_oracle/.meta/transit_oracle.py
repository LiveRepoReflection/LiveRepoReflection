import math
import heapq
import datetime

def find_routes(network, real_time_updates, query):
    departure_ts = query["departure_time"]
    departure_dt = datetime.datetime.fromtimestamp(departure_ts)
    departure_hour = departure_dt.hour

    source_station = find_nearest_station(query["start"], network["stations"])
    target_station = find_nearest_station(query["end"], network["stations"])

    graph = build_graph(network, real_time_updates, departure_hour)
    routes = dijkstra_paths(graph, source_station, target_station, network, departure_hour)
    routes.sort(key=lambda r: r["total_time"] + r["total_fare"] + r["comfort_score"])
    return routes

def find_nearest_station(coord, stations):
    best_station = None
    best_dist = float('inf')
    for station, pos in stations.items():
        dist = math.sqrt((coord["lat"] - pos["lat"])**2 + (coord["lon"] - pos["lon"])**2)
        if dist < best_dist:
            best_dist = dist
            best_station = station
    return best_station

def build_graph(network, real_time_updates, departure_hour):
    graph = {}
    base_fare = network["pricing"]["base_fare"]
    per_min = network["pricing"]["per_min"]
    dynamic_rules = network["pricing"].get("dynamic_rules", [])
    surge_multiplier = None
    if "surge" in real_time_updates.get("pricing_updates", {}):
        surge_multiplier = real_time_updates["pricing_updates"]["surge"].get("multiplier", None)
    
    def get_multiplier():
        if surge_multiplier is not None:
            return surge_multiplier
        multiplier = 1.0
        for rule in dynamic_rules:
            if rule["start_hour"] <= departure_hour < rule["end_hour"]:
                multiplier = max(multiplier, rule["multiplier"])
        return multiplier

    multiplier = get_multiplier()
    
    for line in network["lines"]:
        line_name = line["name"]
        delay = real_time_updates["delays"].get(line_name, 0)
        stations_list = line["stations"]
        travel_times = line["travel_times"]
        
        line_capacity = network["capacity"].get(line_name, {})
        comfort_penalty = 0
        if "peak_hours" in line_capacity:
            for (start, end) in line_capacity["peak_hours"]:
                if start <= departure_hour < end:
                    comfort_penalty = line_capacity.get("penalty", 0)
                    break

        for i in range(len(stations_list)-1):
            s_from = stations_list[i]
            s_to = stations_list[i+1]
            base_travel = travel_times[i]
            travel_time = base_travel + delay
            fare = (base_fare + per_min * travel_time) * multiplier

            edge = {
                "neighbor": s_to,
                "line": line_name,
                "time": travel_time,
                "fare": fare,
                "comfort": comfort_penalty
            }
            graph.setdefault(s_from, []).append(edge)
            
            edge_rev = {
                "neighbor": s_from,
                "line": line_name,
                "time": travel_time,
                "fare": fare,
                "comfort": comfort_penalty
            }
            graph.setdefault(s_to, []).append(edge_rev)
    return graph

def dijkstra_paths(graph, source, target, network, departure_hour):
    heap = []
    start_state = (0, source, None, [source], [], [], [], 0, 0, 0)
    heapq.heappush(heap, start_state)
    visited = {}
    results = []
    
    while heap:
        composite_cost, current, last_line, path_stations, path_lines, seg_times, seg_fares, total_time, total_fare, total_comfort = heapq.heappop(heap)
        
        if current == target:
            route = {
                "stations": path_stations,
                "lines": path_lines,
                "segment_times": seg_times,
                "segment_fares": seg_fares,
                "total_time": total_time,
                "total_fare": total_fare,
                "comfort_score": total_comfort
            }
            results.append(route)
            continue

        state_key = (current, last_line)
        if state_key in visited and visited[state_key] <= composite_cost:
            continue
        visited[state_key] = composite_cost

        if current not in graph:
            continue

        for edge in graph[current]:
            neighbor = edge["neighbor"]
            line_used = edge["line"]
            transfer_penalty = 0
            if last_line is not None and last_line != line_used:
                for transfer in network.get("transfers", []):
                    if transfer["station"] == current:
                        transfer_penalty = transfer["transfer_time"]
                        break
            new_total_time = total_time + edge["time"] + transfer_penalty
            new_total_fare = total_fare + edge["fare"]
            new_total_comfort = total_comfort + edge["comfort"]
            new_composite = new_total_time + new_total_fare + new_total_comfort
            new_path_stations = path_stations + [neighbor]
            if last_line is None or last_line != line_used:
                new_path_lines = path_lines + [line_used]
            else:
                new_path_lines = path_lines + [line_used]
            new_seg_times = seg_times + [edge["time"] + transfer_penalty]
            new_seg_fares = seg_fares + [edge["fare"]]
            heapq.heappush(heap, (new_composite, neighbor, line_used, new_path_stations, new_path_lines, new_seg_times, new_seg_fares, new_total_time, new_total_fare, new_total_comfort))
    return results