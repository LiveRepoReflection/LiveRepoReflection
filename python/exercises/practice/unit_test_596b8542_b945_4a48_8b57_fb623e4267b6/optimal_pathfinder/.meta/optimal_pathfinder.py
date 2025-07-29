import heapq
import math

def get_travel_time(edge, timestamp):
    if "event" in edge:
        event = edge["event"]
        if event["start_time"] <= timestamp <= event["end_time"]:
            if event.get("block", False):
                return float('inf')
            return edge["base_time"] * event.get("multiplier", 1)
    if "time_variation" in edge and callable(edge["time_variation"]):
        return edge["time_variation"](timestamp)
    return edge["base_time"]

def get_vehicle_count(edge):
    return edge.get("current_vehicle_count", 0)

def receive_event_update():
    pass

def find_optimal_path(graph, start_node, end_node, departure_time):
    # Priority queue: each element is a tuple (arrival_time, node, path)
    # We use arrival_time as the cost to decide the next node.
    pq = []
    heapq.heappush(pq, (departure_time, start_node, [start_node]))
    
    # To store the earliest arrival times for nodes.
    best_arrival = {start_node: departure_time}
    
    while pq:
        current_time, node, path = heapq.heappop(pq)
        
        # Call to update dynamic events; function provided externally.
        receive_event_update()
        
        # If we reached the destination, return the path and total travel time.
        if node == end_node:
            return (path, current_time - departure_time)
        
        # Process outgoing edges.
        for edge in graph.get(node, []):
            travel_time = get_travel_time(edge, current_time)
            # If road is blocked, skip this edge.
            if math.isinf(travel_time):
                continue
            arrival_time = current_time + travel_time
            neighbor = edge["to"]
            # If this arrival time is better than previously found, update and push to queue.
            if neighbor not in best_arrival or arrival_time < best_arrival[neighbor]:
                best_arrival[neighbor] = arrival_time
                new_path = path + [neighbor]
                heapq.heappush(pq, (arrival_time, neighbor, new_path))
    
    # No possible path found.
    return ([], float('inf'))