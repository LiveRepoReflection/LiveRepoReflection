import unittest
from transit_optimizer import optimize_routes

class TransitOptimizerTest(unittest.TestCase):
    def test_single_direct_route(self):
        """Test with a single direct route available."""
        stations = {1: ["bus"], 2: ["bus"]}
        routes = [(1, 2, "bus", 5.0, 10.0)]
        requests = [(1, 2, 10.0, 15.0, 0.5)]
        
        results = optimize_routes(stations, routes, requests)
        self.assertEqual(results, [[1, 2]])

    def test_direct_vs_indirect_route(self):
        """Test case where both direct and indirect routes are available."""
        stations = {1: ["bus", "subway"], 2: ["subway"], 3: ["bus"]}
        routes = [
            (1, 2, "subway", 5.0, 10.0),
            (1, 3, "bus", 3.0, 15.0),
            (2, 3, "bus", 2.0, 8.0)
        ]
        requests = [(1, 3, 10.0, 20.0, 0.7)]
        
        results = optimize_routes(stations, routes, requests)
        self.assertEqual(results, [[1, 3]])

    def test_prefer_indirect_route(self):
        """Test case where an indirect route is better than a direct one."""
        stations = {1: ["bus", "subway"], 2: ["subway", "bus"], 3: ["bus"]}
        routes = [
            (1, 2, "subway", 2.0, 5.0),
            (1, 3, "bus", 10.0, 20.0),
            (2, 3, "bus", 1.0, 3.0)
        ]
        requests = [(1, 3, 15.0, 25.0, 0.6)]
        
        results = optimize_routes(stations, routes, requests)
        self.assertEqual(results, [[1, 2, 3]])

    def test_no_suitable_route(self):
        """Test case where no route satisfies the constraints."""
        stations = {1: ["bus"], 2: ["bus"], 3: ["bus"]}
        routes = [
            (1, 2, "bus", 5.0, 10.0),
            (2, 3, "bus", 7.0, 12.0)
        ]
        requests = [(1, 3, 10.0, 20.0, 0.5)]
        
        results = optimize_routes(stations, routes, requests)
        self.assertEqual(results, ["No suitable route found"])

    def test_cost_constraint(self):
        """Test case where a route violates the cost constraint."""
        stations = {1: ["bus"], 2: ["bus"]}
        routes = [(1, 2, "bus", 15.0, 5.0)]
        requests = [(1, 2, 10.0, 10.0, 0.5)]
        
        results = optimize_routes(stations, routes, requests)
        self.assertEqual(results, ["No suitable route found"])

    def test_time_constraint(self):
        """Test case where a route violates the time constraint."""
        stations = {1: ["bus"], 2: ["bus"]}
        routes = [(1, 2, "bus", 5.0, 15.0)]
        requests = [(1, 2, 10.0, 10.0, 0.5)]
        
        results = optimize_routes(stations, routes, requests)
        self.assertEqual(results, ["No suitable route found"])

    def test_multiple_requests(self):
        """Test multiple passenger requests."""
        stations = {1: ["bus", "subway"], 2: ["subway", "tram"], 3: ["bus", "tram"]}
        routes = [
            (1, 2, "subway", 5.0, 10.0),
            (1, 3, "bus", 3.0, 15.0),
            (2, 3, "tram", 2.0, 8.0)
        ]
        requests = [
            (1, 3, 10.0, 20.0, 0.7),
            (1, 2, 6.0, 15.0, 0.3),
            (2, 3, 3.0, 10.0, 0.5)
        ]
        
        results = optimize_routes(stations, routes, requests)
        self.assertEqual(results, [[1, 3], [1, 2], [2, 3]])

    def test_complex_network(self):
        """Test with a more complex network."""
        stations = {
            1: ["bus", "subway"],
            2: ["bus", "tram"],
            3: ["subway", "tram"],
            4: ["bus", "subway", "tram"],
            5: ["subway", "tram"]
        }
        routes = [
            (1, 2, "bus", 3.0, 8.0),
            (1, 3, "subway", 5.0, 6.0),
            (2, 4, "tram", 2.0, 7.0),
            (3, 4, "subway", 4.0, 5.0),
            (3, 5, "tram", 3.0, 9.0),
            (4, 5, "bus", 1.0, 4.0)
        ]
        requests = [(1, 5, 15.0, 20.0, 0.6)]
        
        results = optimize_routes(stations, routes, requests)
        # Multiple paths possible, check for one of them
        possible_paths = [[1, 3, 5], [1, 3, 4, 5], [1, 2, 4, 5]]
        self.assertTrue(results[0] in possible_paths)

    def test_multiple_routes_between_stations(self):
        """Test with multiple routes between the same stations."""
        stations = {1: ["bus", "subway"], 2: ["bus", "subway"]}
        routes = [
            (1, 2, "bus", 5.0, 10.0),
            (1, 2, "subway", 8.0, 5.0)
        ]
        requests = [(1, 2, 10.0, 15.0, 0.7)]
        
        results = optimize_routes(stations, routes, requests)
        self.assertEqual(results, [[1, 2]])  # Subway should be chosen due to weight

    def test_cyclic_graph(self):
        """Test with a graph containing cycles."""
        stations = {1: ["bus"], 2: ["bus"], 3: ["bus"]}
        routes = [
            (1, 2, "bus", 3.0, 5.0),
            (2, 3, "bus", 2.0, 4.0),
            (3, 1, "bus", 4.0, 6.0)
        ]
        requests = [(1, 3, 10.0, 15.0, 0.5)]
        
        results = optimize_routes(stations, routes, requests)
        self.assertEqual(results, [[1, 2, 3]])

    def test_disconnected_graph(self):
        """Test with a disconnected graph."""
        stations = {1: ["bus"], 2: ["bus"], 3: ["bus"], 4: ["bus"]}
        routes = [
            (1, 2, "bus", 3.0, 5.0),
            (3, 4, "bus", 2.0, 4.0)
        ]
        requests = [(1, 4, 10.0, 15.0, 0.5)]
        
        results = optimize_routes(stations, routes, requests)
        self.assertEqual(results, ["No suitable route found"])

if __name__ == "__main__":
    unittest.main()