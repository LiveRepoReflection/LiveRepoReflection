import unittest
import heapq

from geo_network_opt import optimize_network

def build_adjacency_list(graph):
    adj = {node: [] for node in graph['nodes']}
    for edge in graph['edges']:
        # Assuming undirected graph
        node1, node2, distance, travel_time = edge
        adj[node1].append((node2, travel_time))
        adj[node2].append((node1, travel_time))
    return adj

def dijkstra(adj, start, service_radius):
    # Returns a dictionary mapping node to minimum travel_time from start (only if <= service_radius)
    dist = {node: float('inf') for node in adj}
    dist[start] = 0
    heap = [(0, start)]
    while heap:
        current_time, node = heapq.heappop(heap)
        if current_time > service_radius:
            continue
        if current_time > dist[node]:
            continue
        for neighbor, travel_time in adj[node]:
            time = current_time + travel_time
            if time < dist[neighbor] and time <= service_radius:
                dist[neighbor] = time
                heapq.heappush(heap, (time, neighbor))
    # Only return nodes within the service_radius
    return {node for node, time in dist.items() if time <= service_radius}

def compute_union_coverage(graph, chosen_nodes, service_radius):
    adj = build_adjacency_list(graph)
    covered = set()
    for node in chosen_nodes:
        reachable = dijkstra(adj, node, service_radius)
        covered |= reachable
    total_population = sum(graph['nodes'][node]['population'] for node in covered)
    return total_population

def compute_total_installation_cost(graph, chosen_nodes):
    return sum(graph['nodes'][node]['installation_cost'] for node in chosen_nodes)

class GeoNetworkOptTest(unittest.TestCase):

    def test_basic_coverage(self):
        # Using the example provided in the problem description.
        graph = {
            'nodes': {
                'A': {'population': 1000, 'installation_cost': 5000},
                'B': {'population': 1500, 'installation_cost': 7000},
                'C': {'population': 800,  'installation_cost': 4000},
                'D': {'population': 1200, 'installation_cost': 6000},
            },
            'edges': [
                ('A', 'B', 5, 10),
                ('A', 'C', 3, 5),
                ('B', 'D', 2, 3),
                ('C', 'D', 4, 7),
            ],
        }
        budget = 15000
        service_radius = 8
        station_capacity_per_population = 0.001
        min_stations = 2

        result = optimize_network(graph, budget, service_radius, station_capacity_per_population, min_stations)
        # Check that we have at least the minimum number of stations
        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), min_stations)
        # Each selected station should be a valid node
        for node in result:
            self.assertIn(node, graph['nodes'])
        # Total installation cost must be within budget
        cost = compute_total_installation_cost(graph, result)
        self.assertLessEqual(cost, budget)
        # Compute union coverage and check if total covered population matches expected.
        # For this setup, an optimal selection is expected to cover all nodes.
        total_population = sum(info['population'] for info in graph['nodes'].values())
        coverage = compute_union_coverage(graph, result, service_radius)
        self.assertEqual(coverage, total_population)

    def test_insufficient_budget(self):
        # Graph with a single node that is too expensive for the provided budget.
        graph = {
            'nodes': {
                'X': {'population': 2000, 'installation_cost': 10000},
            },
            'edges': []
        }
        budget = 5000
        service_radius = 5
        station_capacity_per_population = 0.001
        min_stations = 1

        result = optimize_network(graph, budget, service_radius, station_capacity_per_population, min_stations)
        # Expecting no valid configuration due to insufficient budget.
        self.assertEqual(result, [])

    def test_min_stations_requirement(self):
        # Graph with two nodes, but min_stations requirement is higher than available nodes.
        graph = {
            'nodes': {
                'X': {'population': 1000, 'installation_cost': 2000},
                'Y': {'population': 1500, 'installation_cost': 2500},
            },
            'edges': [
                ('X', 'Y', 2, 3)
            ]
        }
        budget = 10000
        service_radius = 5
        station_capacity_per_population = 0.001
        min_stations = 3  # More than available nodes

        result = optimize_network(graph, budget, service_radius, station_capacity_per_population, min_stations)
        # Should return empty list since cannot satisfy min_stations constraint.
        self.assertEqual(result, [])

    def test_complex_graph(self):
        # A more complex graph to test integration of coverage and budget constraints.
        graph = {
            'nodes': {
                'A': {'population': 500,  'installation_cost': 2000},
                'B': {'population': 1000, 'installation_cost': 4000},
                'C': {'population': 750,  'installation_cost': 3000},
                'D': {'population': 1200, 'installation_cost': 5000},
                'E': {'population': 900,  'installation_cost': 3500},
            },
            'edges': [
                ('A', 'B', 1, 2),
                ('A', 'C', 2, 3),
                ('B', 'C', 1, 1),
                ('B', 'D', 3, 5),
                ('C', 'E', 2, 4),
                ('D', 'E', 1, 2),
            ],
        }
        budget = 10000
        service_radius = 4
        station_capacity_per_population = 0.001
        min_stations = 2

        result = optimize_network(graph, budget, service_radius, station_capacity_per_population, min_stations)
        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), min_stations)
        # All chosen nodes should be valid.
        for node in result:
            self.assertIn(node, graph['nodes'])
        # Total installation cost must be within budget.
        cost = compute_total_installation_cost(graph, result)
        self.assertLessEqual(cost, budget)
        # Check that union coverage is as good as possible.
        # In this case, an optimal selection should cover all nodes.
        total_population = sum(info['population'] for info in graph['nodes'].values())
        coverage = compute_union_coverage(graph, result, service_radius)
        self.assertEqual(coverage, total_population)

    def test_no_edges_graph(self):
        # Graph with multiple nodes but no edges, so each node covers only itself.
        graph = {
            'nodes': {
                'A': {'population': 800, 'installation_cost': 1500},
                'B': {'population': 1200, 'installation_cost': 2000},
                'C': {'population': 600, 'installation_cost': 1000},
            },
            'edges': []
        }
        budget = 5000
        service_radius = 1  # With no edges, only the node itself is covered.
        station_capacity_per_population = 0.001
        min_stations = 2

        result = optimize_network(graph, budget, service_radius, station_capacity_per_population, min_stations)
        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), min_stations)
        # Verify each station is from the graph.
        for node in result:
            self.assertIn(node, graph['nodes'])
        cost = compute_total_installation_cost(graph, result)
        self.assertLessEqual(cost, budget)
        # The coverage is simply the sum of populations of the chosen nodes.
        coverage = sum(graph['nodes'][node]['population'] for node in result)
        computed_coverage = compute_union_coverage(graph, result, service_radius)
        self.assertEqual(coverage, computed_coverage)

if __name__ == '__main__':
    unittest.main()