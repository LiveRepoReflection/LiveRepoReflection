import heapq

class RideMatchingSystem:
    def __init__(self, city_graph):
        # Convert the input graph (adjacency list with list of tuples) into a dict of dicts
        self.graph = {}
        for node, neighbors in city_graph.items():
            self.graph[node] = {}
            for neighbor, travel_time in neighbors:
                self.graph[node][neighbor] = travel_time
        self.drivers = {}  # driver_id -> {'location': current_location, 'available': bool, 'update_time': timestamp}
        self.rides = {}    # rider_id -> {'pickup': pickup_location, 'destination': destination_location, 'max_wait_time': max_wait,
                           #             'request_time': request_time, 'status': matched_driver_id or "NO_MATCH" or "CANCELLED", 'matched_driver': driver_id or None}

    def update_driver(self, driver_id, current_location, available, update_time):
        self.drivers[driver_id] = {
            'location': current_location,
            'available': available,
            'update_time': update_time
        }

    def update_traffic(self, start_node, end_node, new_travel_time, update_time):
        # Update the edge from start_node to end_node if it exists
        if start_node in self.graph and end_node in self.graph[start_node]:
            self.graph[start_node][end_node] = new_travel_time
        # Assuming bidirectional road, update the reverse edge if it exists
        if end_node in self.graph and start_node in self.graph[end_node]:
            self.graph[end_node][start_node] = new_travel_time

    def request_ride(self, rider_id, pickup_location, destination_location, max_wait_time, request_time):
        # Run Dijkstra's algorithm from pickup_location to get travel times to all nodes
        distances = {node: float('inf') for node in self.graph}
        distances[pickup_location] = 0
        heap = [(0, pickup_location)]
        while heap:
            current_distance, current_node = heapq.heappop(heap)
            if current_distance > distances[current_node]:
                continue
            for neighbor, weight in self.graph.get(current_node, {}).items():
                distance = current_distance + weight
                if distance < distances.get(neighbor, float('inf')):
                    distances[neighbor] = distance
                    heapq.heappush(heap, (distance, neighbor))
        
        best_driver = None
        best_time = float('inf')
        # Check all available drivers
        for driver_id, info in self.drivers.items():
            if info['available']:
                driver_location = info['location']
                travel_time = distances.get(driver_location, float('inf'))
                if travel_time <= max_wait_time and travel_time < best_time:
                    best_time = travel_time
                    best_driver = driver_id

        if best_driver is not None:
            # Mark the ride as matched and mark the driver as unavailable
            self.rides[rider_id] = {
                'pickup': pickup_location,
                'destination': destination_location,
                'max_wait_time': max_wait_time,
                'request_time': request_time,
                'status': best_driver,
                'matched_driver': best_driver
            }
            self.drivers[best_driver]['available'] = False
            return best_driver
        else:
            self.rides[rider_id] = {
                'pickup': pickup_location,
                'destination': destination_location,
                'max_wait_time': max_wait_time,
                'request_time': request_time,
                'status': "NO_MATCH",
                'matched_driver': None
            }
            return "NO_MATCH"

    def cancel_ride(self, rider_id):
        if rider_id in self.rides:
            self.rides[rider_id]['status'] = "CANCELLED"

    def get_match_status(self, rider_id):
        if rider_id in self.rides:
            return self.rides[rider_id]['status']
        return None