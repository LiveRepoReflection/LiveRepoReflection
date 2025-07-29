import heapq
import collections

class RideSharingSystem:
    def __init__(self):
        # Graph represented as: {start_node: {end_node: {"travel_time": value, "cost": value}}}
        self.graph = {}
        # Drivers stored as: {driver_id: {"current_location": value, "is_available": bool, "driver_multiplier": value}}
        self.drivers = {}

    def add_road(self, start_node, end_node, travel_time, cost):
        if start_node not in self.graph:
            self.graph[start_node] = {}
        self.graph[start_node][end_node] = {"travel_time": travel_time, "cost": cost}
        # Ensure the end_node exists in the graph even if no outgoing roads
        if end_node not in self.graph:
            self.graph[end_node] = {}

    def remove_road(self, start_node, end_node):
        if start_node in self.graph and end_node in self.graph[start_node]:
            del self.graph[start_node][end_node]

    def update_road(self, start_node, end_node, new_travel_time, new_cost):
        # Update if road exists; if not, add the road.
        if start_node in self.graph and end_node in self.graph[start_node]:
            self.graph[start_node][end_node] = {"travel_time": new_travel_time, "cost": new_cost}
        else:
            self.add_road(start_node, end_node, new_travel_time, new_cost)

    def update_driver(self, driver_id, current_location, is_available, driver_multiplier):
        self.drivers[driver_id] = {
            "current_location": current_location,
            "is_available": is_available,
            "driver_multiplier": driver_multiplier
        }

    def _dijkstra(self, source, target, weight_key):
        # Standard Dijkstra algorithm to compute shortest distance from source to target
        # weight_key is either 'travel_time' or 'cost'
        distances = collections.defaultdict(lambda: float('inf'))
        distances[source] = 0
        heap = [(0, source)]
        while heap:
            current_dist, node = heapq.heappop(heap)
            if node == target:
                return current_dist
            if current_dist > distances[node]:
                continue
            if node in self.graph:
                for neighbor, value in self.graph[node].items():
                    weight = value[weight_key]
                    new_dist = current_dist + weight
                    if new_dist < distances[neighbor]:
                        distances[neighbor] = new_dist
                        heapq.heappush(heap, (new_dist, neighbor))
        return float('inf')

    def process_ride_request(self, pickup_location, dropoff_location, max_wait_time):
        candidates = []
        # For each available driver, check if pickup is reachable within max_wait_time
        for driver_id, driver_info in self.drivers.items():
            if driver_info["is_available"]:
                driver_location = driver_info["current_location"]
                pickup_time = self._dijkstra(driver_location, pickup_location, "travel_time")
                if pickup_time <= max_wait_time:
                    ride_cost_value = self._dijkstra(pickup_location, dropoff_location, "cost")
                    if ride_cost_value == float('inf'):
                        continue  # Dropoff not reachable
                    total_cost = ride_cost_value * driver_info["driver_multiplier"]
                    # Append candidate with tuple: (pickup_time, total_cost, driver_id)
                    candidates.append((pickup_time, total_cost, driver_id))
        if not candidates:
            return None
        # Sort candidates: first by pickup time then by total ride cost
        candidates.sort(key=lambda x: (x[0], x[1]))
        chosen_candidate = candidates[0]
        chosen_driver_id = chosen_candidate[2]
        chosen_total_cost = chosen_candidate[1]
        # Mark chosen driver as not available
        self.drivers[chosen_driver_id]["is_available"] = False
        return chosen_driver_id, chosen_total_cost