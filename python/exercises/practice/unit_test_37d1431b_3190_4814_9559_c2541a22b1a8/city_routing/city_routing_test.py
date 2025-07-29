import unittest
from city_routing import CityRoutingNetwork

class CityRoutingTests(unittest.TestCase):
    def setUp(self):
        # Create a fresh network for each test.
        self.network = CityRoutingNetwork()

    def test_single_route(self):
        # Simple case: one direct route with sufficient capacity.
        self.network.add_route("A", "B", capacity=100, transit_time=5, cost_per_package=5)
        # Request 50 packages from A to B: cost = 50*5 = 250
        cost = self.network.process_delivery_request("A", "B", 50)
        self.assertEqual(cost, 250, "The cost for 50 packages on a single route should be 250.")

    def test_route_splitting(self):
        # Two parallel routes from A to B
        # First route: capacity 30, cost 5, second route: capacity 40, cost 6.
        self.network.add_route("A", "B", capacity=30, transit_time=4, cost_per_package=5)
        self.network.add_route("A", "B", capacity=40, transit_time=6, cost_per_package=6)
        # Request 50 packages. Expected:
        # Use route1 fully: 30*5 = 150; remaining 20 on route2: 20*6 = 120; total = 270.
        cost = self.network.process_delivery_request("A", "B", 50)
        self.assertEqual(cost, 270, "The cost should be split between two routes with total 270.")

    def test_dynamic_update(self):
        # Add a route and then update its parameters
        self.network.add_route("A", "B", capacity=30, transit_time=4, cost_per_package=10)
        cost_before = self.network.process_delivery_request("A", "B", 30)
        self.assertEqual(cost_before, 30 * 10, "Initial cost should be 300 with cost 10 each.")
        
        # Update the route to have a lower cost and higher capacity
        self.network.update_route("A", "B", capacity=50, transit_time=4, cost_per_package=7)
        cost_after = self.network.process_delivery_request("A", "B", 30)
        self.assertEqual(cost_after, 30 * 7, "After update, cost should be 210 with cost 7 each.")

    def test_multiple_paths(self):
        # Create a network with an intermediate node
        # Direct route from A to C (capacity 20, cost 30)
        self.network.add_route("A", "C", capacity=20, transit_time=3, cost_per_package=30)
        # Two routes: A->B and B->C (both with capacity 50, combined cost 10+15=25)
        self.network.add_route("A", "B", capacity=50, transit_time=2, cost_per_package=10)
        self.network.add_route("B", "C", capacity=50, transit_time=2, cost_per_package=15)
        # Request 60 packages from A to C.
        # Best split: Send 50 on A->B->C, cost = 50*25 = 1250; remaining 10 on direct route, cost = 10*30 = 300.
        # Total expected cost = 1250 + 300 = 1550.
        cost = self.network.process_delivery_request("A", "C", 60)
        self.assertEqual(cost, 1550, "The cost for 60 packages should be optimally split among available routes.")

    def test_no_possible_route(self):
        # Scenario where available capacity is insufficient.
        # Single route from A to B with small capacity.
        self.network.add_route("A", "B", capacity=10, transit_time=4, cost_per_package=5)
        # Request more packages than available, expect -1.
        cost = self.network.process_delivery_request("A", "B", 20)
        self.assertEqual(cost, -1, "Should return -1 if request cannot be fulfilled due to capacity limits.")

    def test_complex_scenario(self):
        # Large network with multiple updates and route splits.
        # Setup network:
        # A->B: capacity 40, cost 8
        # A->B: capacity 30, cost 9
        # B->C: capacity 50, cost 7
        # A->C: capacity 25, cost 20
        self.network.add_route("A", "B", capacity=40, transit_time=3, cost_per_package=8)
        self.network.add_route("A", "B", capacity=30, transit_time=3, cost_per_package=9)
        self.network.add_route("B", "C", capacity=50, transit_time=4, cost_per_package=7)
        self.network.add_route("A", "C", capacity=25, transit_time=5, cost_per_package=20)
        
        # Request 60 packages from A to C.
        # Check cost via two potential paths:
        # Path 1 (A->B->C): maximum capacity min(70,50) = 50 packages.
        #   Cost for using A->B: if using cheapest first: up to 40 at 8, then 10 at 9 = 40*8+10*9 = 320+90 = 410.
        #   Cost for B->C: 50*7 = 350.
        #   Total for 50 packages = 410+350 = 760.
        # Path 2 (A->C direct): up to 25 packages at 20 = 500.
        # Best combination: Use A->B->C for 50 and A->C direct for 10.
        # Direct route cannot deliver more than 25, so 10 is valid.
        # So total cost = 760 (for 50) + 10*20 (for 10) = 760 + 200 = 960.
        cost = self.network.process_delivery_request("A", "C", 60)
        self.assertEqual(cost, 960, "The cost should be optimally computed from multiple splitting routes.")

if __name__ == "__main__":
    unittest.main()