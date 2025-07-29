import math
import heapq
import random
from typing import List, Dict, Tuple, Optional, Any

class Depot:
    def __init__(self, id: int, lat: float, lon: float, num_vehicles: int, vehicle_capacity: int):
        self.id = id
        self.lat = lat
        self.lon = lon
        self.num_vehicles = num_vehicles
        self.vehicle_capacity = vehicle_capacity

class Vehicle:
    def __init__(self, id: int, depot_id: int, capacity: int, max_duration: int):
        self.id = id
        self.depot_id = depot_id
        self.capacity = capacity
        self.max_duration = max_duration

class Order:
    def __init__(self, id: int, lat: float, lon: float, start_time: float, end_time: float, size: int, profit: int):
        self.id = id
        self.lat = lat
        self.lon = lon
        self.start_time = start_time
        self.end_time = end_time
        self.size = size
        self.profit = profit

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in kilometers between two points using Haversine formula."""
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    # Radius of Earth in kilometers
    r = 6371
    
    return c * r

def calculate_travel_time(distance: float, speed: float) -> float:
    """Calculate travel time in seconds given distance in kilometers and speed in m/s."""
    # Convert distance from km to m
    distance_m = distance * 1000
    # Calculate time in seconds
    time_seconds = distance_m / speed
    return time_seconds

def calculate_route_metrics(route: List[Order], vehicle: Vehicle, depot: Depot, 
                           speed: float, service_time: int) -> Tuple[float, float, float]:
    """Calculate total route duration, earliest completion time, and total size for a route."""
    if not route:
        return 0, 0, 0
    
    total_size = sum(order.size for order in route)
    
    # Start at depot
    current_lat, current_lon = depot.lat, depot.lon
    current_time = 0
    total_distance = 0
    
    # Visit each order in the route
    for order in route:
        # Travel to the order location
        distance = calculate_distance(current_lat, current_lon, order.lat, order.lon)
        travel_time = calculate_travel_time(distance, speed)
        
        total_distance += distance
        current_time += travel_time
        
        # Wait if arrived before the start time window
        if current_time < order.start_time:
            current_time = order.start_time
        
        # Perform service
        current_time += service_time
        
        # Update current location
        current_lat, current_lon = order.lat, order.lon
    
    # Return to depot
    distance_to_depot = calculate_distance(current_lat, current_lon, depot.lat, depot.lon)
    travel_time_to_depot = calculate_travel_time(distance_to_depot, speed)
    
    total_distance += distance_to_depot
    current_time += travel_time_to_depot
    
    return current_time, total_distance, total_size

def is_feasible_insertion(route: List[Order], new_order: Order, position: int, 
                         vehicle: Vehicle, depot: Depot, current_time: float,
                         speed: float, service_time: int, max_route_duration: float) -> Tuple[bool, float]:
    """Check if inserting a new order at the given position is feasible and calculate the cost."""
    
    # Create a new route with the order inserted
    new_route = route.copy()
    new_route.insert(position, new_order)
    
    # Calculate total size
    total_size = sum(order.size for order in new_route)
    
    # Check capacity constraint
    if total_size > vehicle.capacity:
        return False, float('inf')
    
    # Start at depot
    current_lat, current_lon = depot.lat, depot.lon
    earliest_arrival_time = current_time
    latest_departure_time = float('inf')
    total_duration = 0
    
    # Visit each order in the route
    for i, order in enumerate(new_route):
        # Travel to the order location
        distance = calculate_distance(current_lat, current_lon, order.lat, order.lon)
        travel_time = calculate_travel_time(distance, speed)
        
        earliest_arrival_time += travel_time
        
        # Check time window constraint
        if earliest_arrival_time > order.end_time:
            return False, float('inf')
        
        service_start_time = max(earliest_arrival_time, order.start_time)
        
        # Update time after service
        earliest_arrival_time = service_start_time + service_time
        
        # Update current location
        current_lat, current_lon = order.lat, order.lon
    
    # Return to depot
    distance_to_depot = calculate_distance(current_lat, current_lon, depot.lat, depot.lon)
    travel_time_to_depot = calculate_travel_time(distance_to_depot, speed)
    
    earliest_arrival_time += travel_time_to_depot
    
    # Check maximum route duration constraint
    total_duration = earliest_arrival_time - current_time
    if total_duration > max_route_duration:
        return False, float('inf')
    
    # Calculate insertion cost (increase in route duration)
    # For simplicity, we'll use the increase in route duration as the cost
    original_duration = 0
    if route:
        original_route_metrics = calculate_route_metrics(route, vehicle, depot, speed, service_time)
        original_duration = original_route_metrics[0]
    
    insertion_cost = total_duration - original_duration
    
    return True, insertion_cost

class DeliverySystem:
    def __init__(self, depots: List[Depot], vehicles: List[Vehicle], speed: float, service_time: int):
        self.depots = depots
        self.vehicles = vehicles
        self.speed = speed
        self.service_time = service_time
        
        # Create a lookup from vehicle ID to vehicle object
        self.vehicle_map = {vehicle.id: vehicle for vehicle in vehicles}
        
        # Create a lookup from depot ID to depot object
        self.depot_map = {depot.id: depot for depot in depots}
        
        # Create a lookup from depot ID to list of vehicles
        self.depot_vehicles = {}
        for depot in depots:
            self.depot_vehicles[depot.id] = [
                vehicle for vehicle in vehicles if vehicle.depot_id == depot.id
            ]

class RoutePlanner:
    def __init__(self, delivery_system: DeliverySystem):
        self.delivery_system = delivery_system
        self.routes = {}  # vehicle_id -> List[Order]
        self.vehicle_loads = {}  # vehicle_id -> current_load
        
        # Initialize empty routes for all vehicles
        for vehicle in delivery_system.vehicles:
            self.routes[vehicle.id] = []
            self.vehicle_loads[vehicle.id] = 0
    
    def process_new_order(self, order: Order, current_time: float) -> Dict[str, Any]:
        """Process a new order and decide whether to accept or reject it."""
        best_vehicle_id = None
        best_position = None
        best_cost = float('inf')
        
        # Try to insert the order into existing routes
        for vehicle_id, route in self.routes.items():
            vehicle = self.delivery_system.vehicle_map[vehicle_id]
            depot = self.delivery_system.depot_map[vehicle.depot_id]
            
            # Skip if the vehicle doesn't have enough capacity
            if self.vehicle_loads[vehicle_id] + order.size > vehicle.capacity:
                continue
            
            # Try all possible insertion positions
            for position in range(len(route) + 1):
                is_feasible, cost = is_feasible_insertion(
                    route, order, position, vehicle, depot, current_time,
                    self.delivery_system.speed, self.delivery_system.service_time,
                    vehicle.max_duration
                )
                
                if is_feasible and cost < best_cost:
                    best_vehicle_id = vehicle_id
                    best_position = position
                    best_cost = cost
        
        # If no feasible insertion found, try to create a new route (if any vehicle is unused)
        if best_vehicle_id is None:
            for vehicle_id, route in self.routes.items():
                if not route:  # Empty route
                    vehicle = self.delivery_system.vehicle_map[vehicle_id]
                    depot = self.delivery_system.depot_map[vehicle.depot_id]
                    
                    if order.size <= vehicle.capacity:
                        is_feasible, cost = is_feasible_insertion(
                            [], order, 0, vehicle, depot, current_time,
                            self.delivery_system.speed, self.delivery_system.service_time,
                            vehicle.max_duration
                        )
                        
                        if is_feasible and cost < best_cost:
                            best_vehicle_id = vehicle_id
                            best_position = 0
                            best_cost = cost
        
        # Assign the order to the best vehicle and position if found
        if best_vehicle_id is not None:
            self.routes[best_vehicle_id].insert(best_position, order)
            self.vehicle_loads[best_vehicle_id] += order.size
            
            return {
                "status": "Assigned",
                "vehicle_id": best_vehicle_id,
                "position": best_position,
                "cost": best_cost
            }
        else:
            return {
                "status": "Rejected",
                "reason": "No feasible insertion found"
            }
    
    def optimize_routes(self):
        """Optimize existing routes to improve overall profit."""
        # This is a placeholder for a more sophisticated optimization algorithm
        # Real implementation would use techniques like simulated annealing, 
        # genetic algorithms, or local search heuristics
        
        # For now, we'll just shuffle a few orders between routes randomly
        for _ in range(10):  # Perform 10 random swaps
            # Select two random vehicles that have orders
            active_vehicles = [v_id for v_id, route in self.routes.items() if route]
            if len(active_vehicles) < 2:
                break
                
            v1_id, v2_id = random.sample(active_vehicles, 2)
            
            # Select a random order from each route
            if not self.routes[v1_id] or not self.routes[v2_id]:
                continue
                
            pos1 = random.randint(0, len(self.routes[v1_id]) - 1)
            pos2 = random.randint(0, len(self.routes[v2_id]) - 1)
            
            order1 = self.routes[v1_id][pos1]
            order2 = self.routes[v2_id][pos2]
            
            # Check if the swap is feasible
            vehicle1 = self.delivery_system.vehicle_map[v1_id]
            vehicle2 = self.delivery_system.vehicle_map[v2_id]
            depot1 = self.delivery_system.depot_map[vehicle1.depot_id]
            depot2 = self.delivery_system.depot_map[vehicle2.depot_id]
            
            # Update loads for feasibility check
            new_load1 = self.vehicle_loads[v1_id] - order1.size + order2.size
            new_load2 = self.vehicle_loads[v2_id] - order2.size + order1.size
            
            if new_load1 > vehicle1.capacity or new_load2 > vehicle2.capacity:
                continue
                
            # Create temporary routes for feasibility check
            temp_route1 = self.routes[v1_id].copy()
            temp_route1[pos1] = order2
            
            temp_route2 = self.routes[v2_id].copy()
            temp_route2[pos2] = order1
            
            current_time = 0  # This would normally be the current simulation time
            
            # Check if both new routes are feasible
            route1_feasible, _ = is_feasible_insertion(
                temp_route1[:pos1] + temp_route1[pos1+1:], 
                order2, pos1, vehicle1, depot1, current_time,
                self.delivery_system.speed, self.delivery_system.service_time,
                vehicle1.max_duration
            )
            
            route2_feasible, _ = is_feasible_insertion(
                temp_route2[:pos2] + temp_route2[pos2+1:], 
                order1, pos2, vehicle2, depot2, current_time,
                self.delivery_system.speed, self.delivery_system.service_time,
                vehicle2.max_duration
            )
            
            # If both routes are feasible, perform the swap
            if route1_feasible and route2_feasible:
                self.routes[v1_id][pos1] = order2
                self.routes[v2_id][pos2] = order1
                
                # Update loads
                self.vehicle_loads[v1_id] = new_load1
                self.vehicle_loads[v2_id] = new_load2
    
    def get_total_profit(self) -> float:
        """Calculate the total profit of all assigned orders."""
        total_profit = 0
        for route in self.routes.values():
            for order in route:
                total_profit += order.profit
        return total_profit