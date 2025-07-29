import unittest
from optimal_rail import design_rail_network
import math

class OptimalRailTest(unittest.TestCase):
    def test_simple_case(self):
        cities = ["A", "B", "C", "D", "E"]
        coordinates = {
            "A": (0, 0),
            "B": (1, 0),
            "C": (0, 1),
            "D": (1, 1),
            "E": (0.5, 0.5)
        }
        budget = 6.0
        cost_per_distance = 1.0
        
        result = design_rail_network(cities, coordinates, budget, cost_per_distance)
        
        # Validate the result
        self.assertIsInstance(result, list)
        self.assertTrue(all(isinstance(edge, tuple) and len(edge) == 2 for edge in result))
        
        # Build a graph from the result
        graph = {city: [] for city in cities}
        total_cost = 0
        
        for city1, city2 in result:
            graph[city1].append(city2)
            graph[city2].append(city1)
            
            # Calculate cost
            lat1, lon1 = coordinates[city1]
            lat2, lon2 = coordinates[city2]
            distance = math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2)
            total_cost += distance * cost_per_distance
        
        # Check connectivity
        visited = set()
        
        def dfs(node):
            visited.add(node)
            for neighbor in graph[node]:
                if neighbor not in visited:
                    dfs(neighbor)
        
        dfs(cities[0])
        self.assertEqual(visited, set(cities), "The network is not fully connected")
        
        # Check budget constraint
        self.assertLessEqual(total_cost, budget, f"Budget exceeded: {total_cost} > {budget}")
        
        # Check redundancy by removing each edge and testing connectivity
        for city1, city2 in result:
            # Remove the edge
            graph[city1].remove(city2)
            graph[city2].remove(city1)
            
            # Check if the graph is still connected
            visited = set()
            dfs(cities[0])
            
            # If removing any single edge disconnects the graph, we don't have redundancy
            if visited != set(cities):
                self.fail(f"Removing edge ({city1}, {city2}) disconnects the network, not enough redundancy")
            
            # Restore the edge for the next iteration
            graph[city1].append(city2)
            graph[city2].append(city1)
    
    def test_no_solution_within_budget(self):
        cities = ["A", "B", "C", "D", "E"]
        coordinates = {
            "A": (0, 0),
            "B": (10, 0),
            "C": (0, 10),
            "D": (10, 10),
            "E": (5, 5)
        }
        budget = 5.0  # Too small for any valid solution
        cost_per_distance = 1.0
        
        result = design_rail_network(cities, coordinates, budget, cost_per_distance)
        self.assertEqual(result, [], "Should return empty list when no solution exists within budget")
    
    def test_larger_network(self):
        cities = ["A", "B", "C", "D", "E", "F", "G", "H"]
        coordinates = {
            "A": (0, 0),
            "B": (1, 0),
            "C": (2, 0),
            "D": (0, 1),
            "E": (1, 1),
            "F": (2, 1),
            "G": (0, 2),
            "H": (1, 2)
        }
        budget = 20.0
        cost_per_distance = 1.0
        
        result = design_rail_network(cities, coordinates, budget, cost_per_distance)
        
        # Validate the result
        self.assertIsInstance(result, list)
        self.assertTrue(all(isinstance(edge, tuple) and len(edge) == 2 for edge in result))
        
        # Build a graph from the result
        graph = {city: [] for city in cities}
        total_cost = 0
        
        for city1, city2 in result:
            graph[city1].append(city2)
            graph[city2].append(city1)
            
            # Calculate cost
            lat1, lon1 = coordinates[city1]
            lat2, lon2 = coordinates[city2]
            distance = math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2)
            total_cost += distance * cost_per_distance
        
        # Check connectivity
        visited = set()
        
        def dfs(node):
            visited.add(node)
            for neighbor in graph[node]:
                if neighbor not in visited:
                    dfs(neighbor)
        
        dfs(cities[0])
        self.assertEqual(visited, set(cities), "The network is not fully connected")
        
        # Check budget constraint
        self.assertLessEqual(total_cost, budget, f"Budget exceeded: {total_cost} > {budget}")
    
    def test_exactly_redundant(self):
        cities = ["A", "B", "C", "D"]
        coordinates = {
            "A": (0, 0),
            "B": (1, 0),
            "C": (1, 1),
            "D": (0, 1)
        }
        budget = 10.0
        cost_per_distance = 1.0
        
        result = design_rail_network(cities, coordinates, budget, cost_per_distance)
        
        # For 4 cities in a square, we need at least 4 edges for minimum redundancy
        # (forming a cycle)
        self.assertGreaterEqual(len(result), 4, 
                              "Need at least 4 edges for redundancy in a 4-city network")
        
        # Build a graph
        graph = {city: [] for city in cities}
        for city1, city2 in result:
            graph[city1].append(city2)
            graph[city2].append(city1)
        
        # Each city should have at least 2 connections for redundancy
        for city, neighbors in graph.items():
            self.assertGreaterEqual(len(neighbors), 2, 
                                  f"City {city} has fewer than 2 connections")
    
    def test_edge_case_five_cities_minimum_budget(self):
        cities = ["A", "B", "C", "D", "E"]
        coordinates = {
            "A": (0, 0),
            "B": (0, 1),
            "C": (1, 1),
            "D": (1, 0),
            "E": (0.5, 0.5)
        }
        
        # Calculate minimum distance for a cycle + additional connections for redundancy
        min_cycle_dist = 4.0  # Square perimeter
        additional_dist = math.sqrt(0.5**2 + 0.5**2) * 2  # Additional connections to center
        min_budget = (min_cycle_dist + additional_dist) * 0.9  # Just below required
        
        # Test with insufficient budget
        result_insufficient = design_rail_network(cities, coordinates, min_budget, 1.0)
        self.assertEqual(result_insufficient, [], 
                       "Should return empty list when budget is insufficient for redundancy")
        
        # Test with exactly sufficient budget (with small margin)
        sufficient_budget = (min_cycle_dist + additional_dist) * 1.1  # Just above required
        result_sufficient = design_rail_network(cities, coordinates, sufficient_budget, 1.0)
        self.assertNotEqual(result_sufficient, [], 
                          "Should find a solution when budget is sufficient")

    def test_random_coordinates(self):
        import random
        random.seed(42)  # For reproducibility
        
        num_cities = 10
        cities = [chr(65 + i) for i in range(num_cities)]  # A, B, C, ...
        coordinates = {}
        
        for city in cities:
            coordinates[city] = (random.uniform(0, 10), random.uniform(0, 10))
        
        budget = 100.0  # Large enough budget for testing
        cost_per_distance = 1.0
        
        result = design_rail_network(cities, coordinates, budget, cost_per_distance)
        
        # Build a graph from the result
        graph = {city: [] for city in cities}
        total_cost = 0
        
        for city1, city2 in result:
            graph[city1].append(city2)
            graph[city2].append(city1)
            
            # Calculate cost
            lat1, lon1 = coordinates[city1]
            lat2, lon2 = coordinates[city2]
            distance = math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2)
            total_cost += distance * cost_per_distance
        
        # Check connectivity and redundancy
        for city in cities:
            self.assertGreaterEqual(len(graph[city]), 2, 
                                 f"City {city} should have at least 2 connections for redundancy")

        # Check budget constraint
        self.assertLessEqual(total_cost, budget, f"Budget exceeded: {total_cost} > {budget}")

    def test_check_redundancy_requirement(self):
        cities = ["A", "B", "C", "D", "E"]
        coordinates = {
            "A": (0, 0),
            "B": (1, 0),
            "C": (0, 1),
            "D": (1, 1),
            "E": (2, 2)
        }
        budget = 20.0
        cost_per_distance = 1.0
        
        result = design_rail_network(cities, coordinates, budget, cost_per_distance)
        
        # Build a graph
        graph = {city: [] for city in cities}
        for city1, city2 in result:
            graph[city1].append(city2)
            graph[city2].append(city1)
        
        # For each pair of cities, check if removing any single node (except the pair)
        # still allows a path between them
        for i, start in enumerate(cities):
            for end in cities[i+1:]:
                for node_to_remove in cities:
                    if node_to_remove == start or node_to_remove == end:
                        continue
                    
                    # Create a copy of the graph without the node_to_remove
                    temp_graph = {city: [n for n in neighbors if n != node_to_remove] 
                                 for city, neighbors in graph.items() 
                                 if city != node_to_remove}
                    
                    # Check if there's still a path from start to end
                    queue = [start]
                    visited = {start}
                    path_exists = False
                    
                    while queue and not path_exists:
                        current = queue.pop(0)
                        if current == end:
                            path_exists = True
                            break
                        
                        for neighbor in temp_graph.get(current, []):
                            if neighbor not in visited:
                                visited.add(neighbor)
                                queue.append(neighbor)
                    
                    self.assertTrue(path_exists, 
                                 f"Removing node {node_to_remove} should not disconnect {start} from {end}")

if __name__ == '__main__':
    unittest.main()