import unittest
from unittest.mock import patch
import random
import json
import math
import datetime
from urban_delivery import (
    Depot, Vehicle, Order, RoutePlanner, DeliverySystem,
    calculate_distance, calculate_travel_time, is_feasible_insertion
)

class TestUrbanDelivery(unittest.TestCase):
    def setUp(self):
        # Set a fixed seed for reproducibility
        random.seed(42)
        
        # Setup test data
        self.depots = [
            Depot(1, 40.7128, -74.0060, 3, 100),  # NYC
            Depot(2, 40.7300, -73.9350, 2, 80)    # Queens
        ]
        
        self.vehicles = [
            Vehicle(101, 1, 100, 8*3600),  # 8 hours max duration for depot 1
            Vehicle(102, 1, 100, 8*3600),
            Vehicle(103, 1, 100, 8*3600),
            Vehicle(201, 2, 80, 8*3600),   # 8 hours max duration for depot 2
            Vehicle(202, 2, 80, 8*3600)
        ]
        
        # Current time is 9:00 AM
        self.current_time = 9 * 3600
        
        # Orders with time windows, size, and profit
        self.orders = [
            Order(1001, 40.7500, -74.0100, 10*3600, 11*3600, 15, 100),  # 10-11 AM window
            Order(1002, 40.7400, -73.9900, 11*3600, 12*3600, 10, 80),   # 11-12 AM window
            Order(1003, 40.7200, -73.9800, 12*3600, 13*3600, 20, 120),  # 12-1 PM window
            Order(1004, 40.7350, -73.9400, 10*3600, 11.5*3600, 15, 90), # 10-11:30 AM window
            Order(1005, 40.7250, -73.9300, 11*3600, 12.5*3600, 25, 150) # 11-12:30 PM window
        ]
        
        # Parameters
        self.speed = 10  # m/s (36 km/h)
        self.max_route_duration = 8 * 3600  # 8 hours in seconds
        self.service_time = 300  # 5 minutes per delivery
        
        # Setup planning system
        self.delivery_system = DeliverySystem(self.depots, self.vehicles, self.speed, self.service_time)

    def test_distance_calculation(self):
        # Test Haversine distance calculation
        lat1, lon1 = 40.7128, -74.0060  # NYC
        lat2, lon2 = 40.7300, -73.9350  # Queens
        distance = calculate_distance(lat1, lon1, lat2, lon2)
        self.assertGreater(distance, 0)
        
        # Check if the distance is approximately correct
        expected_distance = 6.2  # km, approximate distance between coordinates
        self.assertAlmostEqual(distance, expected_distance, delta=1.0)

    def test_travel_time_calculation(self):
        # Test travel time calculation
        distance = 5.0  # km
        speed = 10.0    # m/s (36 km/h)
        
        travel_time = calculate_travel_time(distance, speed)
        # Expected: 5000 meters / 10 m/s = 500 seconds
        self.assertEqual(travel_time, 500)

    def test_order_feasibility(self):
        # Create a simple route with one vehicle
        vehicle = self.vehicles[0]
        route = []
        
        # Check if it's feasible to add the first order to an empty route
        order = self.orders[0]
        depot = next(d for d in self.depots if d.id == vehicle.depot_id)
        
        # Test if insertion is feasible at position 0
        is_feasible, _ = is_feasible_insertion(
            route, order, 0, vehicle, depot, self.current_time, 
            self.speed, self.service_time, self.max_route_duration
        )
        self.assertTrue(is_feasible)
        
        # Add order to route
        route.append(order)
        
        # Test insertion of second order at position 1
        order2 = self.orders[1]
        is_feasible, _ = is_feasible_insertion(
            route, order2, 1, vehicle, depot, self.current_time, 
            self.speed, self.service_time, self.max_route_duration
        )
        self.assertTrue(is_feasible)

    def test_order_assignment(self):
        # Test assigning orders to vehicles
        planner = RoutePlanner(self.delivery_system)
        
        # Process each order
        decisions = []
        for order in self.orders:
            decision = planner.process_new_order(order, self.current_time)
            decisions.append(decision)
            self.current_time += 600  # 10 minutes between orders
        
        # Verify that at least some orders were assigned
        assigned_count = sum(1 for d in decisions if d.get("status") == "Assigned")
        self.assertGreater(assigned_count, 0)

    def test_capacity_constraint(self):
        # Test that vehicle capacity constraints are enforced
        planner = RoutePlanner(self.delivery_system)
        
        # Create a large order that should exceed vehicle capacity
        large_order = Order(9999, 40.7200, -73.9800, 12*3600, 13*3600, 200, 500)
        
        decision = planner.process_new_order(large_order, self.current_time)
        
        # The order should be rejected due to capacity constraints
        self.assertEqual(decision.get("status"), "Rejected")

    def test_time_window_constraint(self):
        # Test that time window constraints are enforced
        planner = RoutePlanner(self.delivery_system)
        
        # Create an order with an impossible time window (already passed)
        past_order = Order(9998, 40.7200, -73.9800, 6*3600, 7*3600, 10, 100)
        
        decision = planner.process_new_order(past_order, self.current_time)
        
        # The order should be rejected due to time window constraints
        self.assertEqual(decision.get("status"), "Rejected")

    def test_dynamic_order_insertion(self):
        # Test the dynamic insertion of orders into existing routes
        planner = RoutePlanner(self.delivery_system)
        
        # First, assign some initial orders
        for i in range(3):
            planner.process_new_order(self.orders[i], self.current_time)
            self.current_time += 600
        
        # Now, try to insert a new order that should fit into an existing route
        new_order = Order(2001, 40.7300, -73.9950, 11*3600, 12*3600, 5, 70)
        decision = planner.process_new_order(new_order, self.current_time)
        
        # The order should be assigned
        self.assertEqual(decision.get("status"), "Assigned")

    def test_complete_system(self):
        # Test the complete system with a series of orders
        delivery_system = DeliverySystem(self.depots, self.vehicles, self.speed, self.service_time)
        planner = RoutePlanner(delivery_system)
        
        # Generate a larger set of test orders
        test_orders = []
        for i in range(30):
            # Random location within a reasonable distance from depots
            lat = 40.72 + random.uniform(-0.05, 0.05)
            lon = -74.00 + random.uniform(-0.05, 0.05)
            
            # Random time window (between 9 AM and 5 PM)
            start_time = (9 + random.randint(0, 7)) * 3600
            end_time = start_time + random.randint(1, 3) * 3600
            
            # Random size and profit
            size = random.randint(5, 30)
            profit = size * random.randint(5, 10)
            
            order = Order(3000 + i, lat, lon, start_time, end_time, size, profit)
            test_orders.append(order)
        
        # Process all orders
        current_time = 9 * 3600
        decisions = []
        for order in test_orders:
            decision = planner.process_new_order(order, current_time)
            decisions.append(decision)
            current_time += random.randint(300, 900)  # 5-15 minutes between orders
        
        # Calculate statistics
        assigned = sum(1 for d in decisions if d.get("status") == "Assigned")
        rejected = sum(1 for d in decisions if d.get("status") == "Rejected")
        
        # Print statistics for debugging
        print(f"Assigned: {assigned}, Rejected: {rejected}")
        
        # Verify that routes are valid
        for vehicle_id, route in planner.routes.items():
            if route:
                vehicle = next(v for v in self.vehicles if v.id == vehicle_id)
                depot = next(d for d in self.depots if d.id == vehicle.depot_id)
                
                # Check capacity constraint
                total_size = sum(order.size for order in route)
                self.assertLessEqual(total_size, vehicle.capacity)
                
                # Check that the route starts and ends at the depot
                # (This is implicitly checked in the is_feasible_insertion function)
                
                # Verify that orders are delivered within their time windows
                # (This would require a more complex simulation)

    def test_json_serialization(self):
        # Test that the objects can be properly serialized to JSON
        order = self.orders[0]
        order_dict = {
            "id": order.id,
            "lat": order.lat,
            "lon": order.lon,
            "start_time": order.start_time,
            "end_time": order.end_time,
            "size": order.size,
            "profit": order.profit
        }
        
        # Test serialization
        json_str = json.dumps(order_dict)
        self.assertIsInstance(json_str, str)
        
        # Test deserialization
        parsed_dict = json.loads(json_str)
        self.assertEqual(parsed_dict["id"], order.id)
        self.assertEqual(parsed_dict["size"], order.size)
        self.assertEqual(parsed_dict["profit"], order.profit)

    def test_large_scale_simulation(self):
        # Test with a larger number of orders (100)
        delivery_system = DeliverySystem(self.depots, self.vehicles, self.speed, self.service_time)
        planner = RoutePlanner(delivery_system)
        
        # Generate 100 random orders
        large_test_orders = []
        for i in range(100):
            lat = 40.72 + random.uniform(-0.08, 0.08)
            lon = -74.00 + random.uniform(-0.08, 0.08)
            
            # Random time window (between 9 AM and 5 PM)
            start_time = (9 + random.randint(0, 7)) * 3600
            end_time = start_time + random.randint(1, 3) * 3600
            
            size = random.randint(5, 30)
            profit = size * random.randint(5, 10)
            
            order = Order(5000 + i, lat, lon, start_time, end_time, size, profit)
            large_test_orders.append(order)
        
        # Process all orders and measure time
        start_processing_time = datetime.datetime.now()
        current_time = 9 * 3600
        decisions = []
        
        for order in large_test_orders:
            decision = planner.process_new_order(order, current_time)
            decisions.append(decision)
            current_time += random.randint(60, 300)  # 1-5 minutes between orders
        
        end_processing_time = datetime.datetime.now()
        processing_duration = (end_processing_time - start_processing_time).total_seconds()
        
        # The total processing time should be reasonable
        self.assertLess(processing_duration, 10)  # should complete in less than 10 seconds
        
        # Calculate statistics
        assigned = sum(1 for d in decisions if d.get("status") == "Assigned")
        
        # At least some orders should be assigned
        self.assertGreater(assigned, 0)
        
        # Print statistics
        print(f"Large scale test: {assigned} orders assigned, processed in {processing_duration:.2f} seconds")

    @patch('random.random')
    def test_deterministic_behavior(self, mock_random):
        # Test that with a fixed seed, the algorithm produces deterministic results
        mock_random.return_value = 0.5  # Fix random value
        
        # Run the algorithm twice with the same input
        planner1 = RoutePlanner(self.delivery_system)
        planner2 = RoutePlanner(self.delivery_system)
        
        decisions1 = []
        decisions2 = []
        
        current_time = 9 * 3600
        
        for order in self.orders:
            decisions1.append(planner1.process_new_order(order, current_time))
            decisions2.append(planner2.process_new_order(order, current_time))
            current_time += 600
        
        # Decisions should be identical
        for i in range(len(decisions1)):
            self.assertEqual(decisions1[i].get("status"), decisions2[i].get("status"))
            if decisions1[i].get("status") == "Assigned":
                self.assertEqual(decisions1[i].get("vehicle_id"), decisions2[i].get("vehicle_id"))
                self.assertEqual(decisions1[i].get("position"), decisions2[i].get("position"))

if __name__ == '__main__':
    unittest.main()