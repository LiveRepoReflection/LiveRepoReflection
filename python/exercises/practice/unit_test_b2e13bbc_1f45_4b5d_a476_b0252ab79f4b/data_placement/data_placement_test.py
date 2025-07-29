import unittest
from data_placement import find_optimal_data_center_locations

class DataPlacementTest(unittest.TestCase):
    def test_basic_example(self):
        graph = {
            'CityA': {'CityB': 10, 'CityC': 15},
            'CityB': {'CityA': 10, 'CityD': 20},
            'CityC': {'CityA': 15, 'CityE': 25},
            'CityD': {'CityB': 20, 'CityF': 30},
            'CityE': {'CityC': 25, 'CityF': 35},
            'CityF': {'CityD': 30, 'CityE': 35}
        }
        num_data_centers = 2
        latency_radius = 30
        city_demands = {
            'CityA': 1000,
            'CityB': 1500,
            'CityC': 800,
            'CityD': 1200,
            'CityE': 900,
            'CityF': 1100
        }
        
        locations, demand = find_optimal_data_center_locations(graph, num_data_centers, latency_radius, city_demands)
        
        # Assert locations are valid
        self.assertLessEqual(len(locations), num_data_centers)
        self.assertTrue(all(city in graph for city in locations))
        
        # Verify demand covered
        self.assertEqual(demand, self._calculate_covered_demand(graph, locations, latency_radius, city_demands))

    def test_single_data_center(self):
        graph = {
            'CityA': {'CityB': 10},
            'CityB': {'CityA': 10, 'CityC': 15},
            'CityC': {'CityB': 15, 'CityD': 20},
            'CityD': {'CityC': 20}
        }
        num_data_centers = 1
        latency_radius = 25
        city_demands = {
            'CityA': 500,
            'CityB': 700,
            'CityC': 600,
            'CityD': 400
        }
        
        locations, demand = find_optimal_data_center_locations(graph, num_data_centers, latency_radius, city_demands)
        
        self.assertEqual(len(locations), 1)
        # Either CityB or CityC would be optimal for covering most demand
        self.assertIn(locations[0], ['CityB', 'CityC'])
        self.assertEqual(demand, self._calculate_covered_demand(graph, locations, latency_radius, city_demands))

    def test_no_data_center(self):
        graph = {
            'CityA': {'CityB': 10},
            'CityB': {'CityA': 10}
        }
        num_data_centers = 0
        latency_radius = 20
        city_demands = {
            'CityA': 500,
            'CityB': 700
        }
        
        locations, demand = find_optimal_data_center_locations(graph, num_data_centers, latency_radius, city_demands)
        
        self.assertEqual(len(locations), 0)
        self.assertEqual(demand, 0)

    def test_insufficient_data_centers(self):
        graph = {
            'CityA': {'CityB': 50},
            'CityB': {'CityA': 50, 'CityC': 50},
            'CityC': {'CityB': 50, 'CityD': 50},
            'CityD': {'CityC': 50, 'CityE': 50},
            'CityE': {'CityD': 50}
        }
        num_data_centers = 2
        latency_radius = 40  # Not enough to cover all with 2 centers
        city_demands = {
            'CityA': 100,
            'CityB': 100,
            'CityC': 100,
            'CityD': 100,
            'CityE': 100
        }
        
        locations, demand = find_optimal_data_center_locations(graph, num_data_centers, latency_radius, city_demands)
        
        self.assertLessEqual(len(locations), num_data_centers)
        # Should maximize demand coverage
        expected_demand = self._calculate_covered_demand(graph, locations, latency_radius, city_demands)
        self.assertEqual(demand, expected_demand)
        # Some cities won't be covered
        self.assertLess(demand, sum(city_demands.values()))

    def test_isolated_cities(self):
        graph = {
            'CityA': {},
            'CityB': {},
            'CityC': {}
        }
        num_data_centers = 2
        latency_radius = 10
        city_demands = {
            'CityA': 100,
            'CityB': 200,
            'CityC': 300
        }
        
        locations, demand = find_optimal_data_center_locations(graph, num_data_centers, latency_radius, city_demands)
        
        self.assertEqual(len(locations), 2)
        # Should select the two cities with highest demand
        self.assertIn('CityB', locations)
        self.assertIn('CityC', locations)
        self.assertEqual(demand, 500)  # 200 + 300

    def test_zero_latency_radius(self):
        graph = {
            'CityA': {'CityB': 10},
            'CityB': {'CityA': 10, 'CityC': 15},
            'CityC': {'CityB': 15}
        }
        num_data_centers = 2
        latency_radius = 0  # Can only cover a city by placing a data center in it
        city_demands = {
            'CityA': 300,
            'CityB': 200,
            'CityC': 100
        }
        
        locations, demand = find_optimal_data_center_locations(graph, num_data_centers, latency_radius, city_demands)
        
        self.assertEqual(len(locations), 2)
        # Should select the two cities with highest demand
        self.assertIn('CityA', locations)
        self.assertIn('CityB', locations)
        self.assertEqual(demand, 500)  # 300 + 200

    def test_large_network(self):
        # Create a linear network of 10 cities
        graph = {}
        for i in range(1, 10):
            city = f'City{i}'
            next_city = f'City{i+1}'
            
            if city not in graph:
                graph[city] = {}
            if next_city not in graph:
                graph[next_city] = {}
                
            graph[city][next_city] = 10
            graph[next_city][city] = 10
        
        num_data_centers = 3
        latency_radius = 15
        city_demands = {f'City{i}': i*100 for i in range(1, 11)}
        
        locations, demand = find_optimal_data_center_locations(graph, num_data_centers, latency_radius, city_demands)
        
        self.assertLessEqual(len(locations), num_data_centers)
        expected_demand = self._calculate_covered_demand(graph, locations, latency_radius, city_demands)
        self.assertEqual(demand, expected_demand)

    def test_disconnected_components(self):
        graph = {
            # Component 1
            'CityA': {'CityB': 10},
            'CityB': {'CityA': 10, 'CityC': 15},
            'CityC': {'CityB': 15},
            
            # Component 2
            'CityD': {'CityE': 20},
            'CityE': {'CityD': 20, 'CityF': 25},
            'CityF': {'CityE': 25}
        }
        num_data_centers = 2
        latency_radius = 20
        city_demands = {
            'CityA': 300,
            'CityB': 200,
            'CityC': 100,
            'CityD': 250,
            'CityE': 350,
            'CityF': 150
        }
        
        locations, demand = find_optimal_data_center_locations(graph, num_data_centers, latency_radius, city_demands)
        
        self.assertEqual(len(locations), 2)
        # Should select one city from each component to maximize coverage
        component1_cities = ['CityA', 'CityB', 'CityC']
        component2_cities = ['CityD', 'CityE', 'CityF']
        self.assertTrue(any(city in locations for city in component1_cities))
        self.assertTrue(any(city in locations for city in component2_cities))
        expected_demand = self._calculate_covered_demand(graph, locations, latency_radius, city_demands)
        self.assertEqual(demand, expected_demand)

    def test_empty_graph(self):
        graph = {}
        num_data_centers = 2
        latency_radius = 20
        city_demands = {}
        
        locations, demand = find_optimal_data_center_locations(graph, num_data_centers, latency_radius, city_demands)
        
        self.assertEqual(len(locations), 0)
        self.assertEqual(demand, 0)

    def _calculate_all_pairs_shortest_paths(self, graph):
        """Helper method to calculate shortest paths between all pairs of cities"""
        cities = list(graph.keys())
        # Initialize distances with infinity
        distances = {city1: {city2: float('inf') for city2 in cities} for city1 in cities}
        
        # Set distance to self as 0
        for city in cities:
            distances[city][city] = 0
            
        # Set direct connections
        for city, neighbors in graph.items():
            for neighbor, cost in neighbors.items():
                distances[city][neighbor] = cost
                
        # Floyd-Warshall algorithm
        for k in cities:
            for i in cities:
                for j in cities:
                    if distances[i][k] + distances[k][j] < distances[i][j]:
                        distances[i][j] = distances[i][k] + distances[k][j]
                        
        return distances

    def _calculate_covered_demand(self, graph, data_center_locations, latency_radius, city_demands):
        """Helper method to calculate the total demand covered by the given data center locations"""
        if not data_center_locations:
            return 0
            
        distances = self._calculate_all_pairs_shortest_paths(graph)
        covered_demand = 0
        
        for city, demand in city_demands.items():
            # Check if this city is within latency_radius of any data center
            for data_center in data_center_locations:
                if data_center in distances and city in distances[data_center]:
                    if distances[data_center][city] <= latency_radius:
                        covered_demand += demand
                        break
                elif data_center == city:  # Data center in the city itself
                    covered_demand += demand
                    break
                    
        return covered_demand

if __name__ == '__main__':
    unittest.main()