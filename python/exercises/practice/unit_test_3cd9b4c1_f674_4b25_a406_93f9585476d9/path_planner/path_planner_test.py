import unittest
import copy

from path_planner import find_optimal_path, update_edge, remove_edge

class TestPathPlanner(unittest.TestCase):
    def setUp(self):
        # Define a sample graph for testing
        self.graph = {
            1: [
                {"source": 1, "destination": 2, "distance": 10, "energy_cost": 5, "time_cost": 2, "weather_impact": 1.0},
                {"source": 1, "destination": 3, "distance": 20, "energy_cost": 10, "time_cost": 2, "weather_impact": 1.0},
            ],
            2: [
                {"source": 2, "destination": 4, "distance": 15, "energy_cost": 5, "time_cost": 3, "weather_impact": 0.8},
            ],
            3: [
                {"source": 3, "destination": 4, "distance": 5, "energy_cost": 2, "time_cost": 1, "weather_impact": 1.0},
            ],
            4: []
        }
        
        # Default parameters
        self.deadline = 10.0         # seconds (sufficient for any normal path in our test graph)
        self.priority = 1
        self.energy_budget = 15.0    # Enough energy for all paths unless modified
        self.distance_weight = 1.0
        self.energy_weight = 1.0
        self.time_weight = 1.0

    def test_direct_path(self):
        # Test a simple scenario where the optimal path is clearly defined
        # With current weights, path [1,2,4] should be optimal over [1,3,4]
        expected_path = [1, 2, 4]
        result = find_optimal_path(copy.deepcopy(self.graph), 1, 4, self.deadline,
                                   self.priority, self.energy_budget,
                                   self.distance_weight, self.energy_weight,
                                   self.time_weight)
        self.assertEqual(result, expected_path)

    def test_no_feasible_path_due_to_energy(self):
        # Set energy budget too low to handle available routes
        low_energy_budget = 9.0  # Both available paths exceed this budget
        result = find_optimal_path(copy.deepcopy(self.graph), 1, 4, self.deadline,
                                   self.priority, low_energy_budget,
                                   self.distance_weight, self.energy_weight,
                                   self.time_weight)
        self.assertEqual(result, [])

    def test_no_feasible_path_due_to_deadline(self):
        # Set deadline too strict for any path
        strict_deadline = 1.0  # Too short to complete any valid path
        result = find_optimal_path(copy.deepcopy(self.graph), 1, 4, strict_deadline,
                                   self.priority, self.energy_budget,
                                   self.distance_weight, self.energy_weight,
                                   self.time_weight)
        self.assertEqual(result, [])

    def test_updated_edge_improves_path(self):
        # Update edge (1 -> 2) to have a lower energy cost so that it becomes even more favorable
        modified_graph = copy.deepcopy(self.graph)
        update_edge(modified_graph, 1, 2, new_distance=10, new_energy_cost=1, 
                    new_time_cost=2, new_weather_impact=1.0)
        
        expected_path = [1, 2, 4]
        result = find_optimal_path(modified_graph, 1, 4, self.deadline,
                                   self.priority, self.energy_budget,
                                   self.distance_weight, self.energy_weight,
                                   self.time_weight)
        self.assertEqual(result, expected_path)

    def test_removed_edge_forces_alternate_path(self):
        # Remove one edge to force use of the alternative route from 1 -> 3 -> 4
        modified_graph = copy.deepcopy(self.graph)
        remove_edge(modified_graph, 1, 2)
        
        expected_path = [1, 3, 4]
        result = find_optimal_path(modified_graph, 1, 4, self.deadline,
                                   self.priority, self.energy_budget,
                                   self.distance_weight, self.energy_weight,
                                   self.time_weight)
        self.assertEqual(result, expected_path)

    def test_invalid_start_or_end(self):
        # Test with an invalid start node
        result_invalid_start = find_optimal_path(copy.deepcopy(self.graph), 99, 4, self.deadline,
                                                 self.priority, self.energy_budget,
                                                 self.distance_weight, self.energy_weight,
                                                 self.time_weight)
        self.assertEqual(result_invalid_start, [])
        
        # Test with an invalid end node
        result_invalid_end = find_optimal_path(copy.deepcopy(self.graph), 1, 99, self.deadline,
                                               self.priority, self.energy_budget,
                                               self.distance_weight, self.energy_weight,
                                               self.time_weight)
        self.assertEqual(result_invalid_end, [])
    
    def test_complex_graph_multiple_paths(self):
        # Extend graph to have multiple alternating paths and verify that the algorithm picks the correct optimal one.
        extended_graph = copy.deepcopy(self.graph)
        # Add extra node 5 and extra edges to form an alternative longer route
        extended_graph[4] = [{"source": 4, "destination": 5, "distance": 5, "energy_cost": 2, "time_cost": 1, "weather_impact": 1.0}]
        extended_graph[5] = []  # Destination node now is 5
        
        # Now test from 1 to 5.
        # Two candidate paths:
        # Path A: 1->2->4->5: distance=10+15+5=30, energy=5+5+2=12, time=(2+3*0.8+1)=2+2.4+1=5.4, total cost = 30+12+5.4 = 47.4
        # Path B: 1->3->4->5: distance=20+5+5=30, energy=10+2+2=14, time=(2+1+1)=4, total cost = 30+14+4 = 48
        expected_path = [1, 2, 4, 5]
        result = find_optimal_path(extended_graph, 1, 5, self.deadline,
                                   self.priority, self.energy_budget,
                                   self.distance_weight, self.energy_weight,
                                   self.time_weight)
        self.assertEqual(result, expected_path)

if __name__ == '__main__':
    unittest.main()