import unittest
import itertools
from collections import deque
from tower_placement import optimal_tower_placement

class TestTowerPlacement(unittest.TestCase):

    def calculate_profit(self, placement, graph, location_data, revenue_per_person, interference_distance, interference_penalty):
        total_profit = 0
        # Helper function to determine if a tower at node is interfered by at least one other tower.
        def is_interfered(node, placement_set):
            visited = set()
            queue = deque([(node, 0)])
            visited.add(node)
            while queue:
                current, dist = queue.popleft()
                if dist > 0 and current in placement_set:
                    return True
                if dist < interference_distance:
                    for neighbor in graph.get(current, []):
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append((neighbor, dist + 1))
            return False

        for node in placement:
            data = location_data[node]
            revenue = data['population'] * revenue_per_person
            if is_interfered(node, placement):
                revenue *= (1 - interference_penalty)
            total_profit += revenue - data['cost']
        return total_profit

    def brute_force_optimal(self, graph, location_data, revenue_per_person, interference_distance, interference_penalty):
        nodes = list(graph.keys())
        best_profit = float('-inf')
        best_placement = set()

        def profit_for_placement(placement_set):
            tot = 0
            def node_interfered(node, placement_set):
                visited = set()
                queue = deque([(node, 0)])
                visited.add(node)
                while queue:
                    current, dist = queue.popleft()
                    if dist > 0 and current in placement_set:
                        return True
                    if dist < interference_distance:
                        for neighbor in graph.get(current, []):
                            if neighbor not in visited:
                                visited.add(neighbor)
                                queue.append((neighbor, dist + 1))
                return False
            for node in placement_set:
                data = location_data[node]
                revenue = data['population'] * revenue_per_person
                if node_interfered(node, placement_set):
                    revenue *= (1 - interference_penalty)
                tot += revenue - data['cost']
            return tot

        for r in range(len(nodes) + 1):
            for combo in itertools.combinations(nodes, r):
                placement_set = set(combo)
                current_profit = profit_for_placement(placement_set)
                if current_profit > best_profit:
                    best_profit = current_profit
                    best_placement = placement_set
        return best_profit, best_placement

    def test_basic_graph(self):
        graph = {
            1: [2, 3],
            2: [1, 4],
            3: [1, 4, 5],
            4: [2, 3, 6],
            5: [3],
            6: [4]
        }
        location_data = {
            1: {'population': 1000, 'cost': 500},
            2: {'population': 1500, 'cost': 700},
            3: {'population': 800, 'cost': 400},
            4: {'population': 1200, 'cost': 600},
            5: {'population': 500, 'cost': 300},
            6: {'population': 700, 'cost': 350}
        }
        revenue_per_person = 0.5
        interference_distance = 2
        interference_penalty = 0.3

        result = optimal_tower_placement(graph, location_data, revenue_per_person, interference_distance, interference_penalty)
        self.assertIsInstance(result, set)

        expected_profit, expected_placement = self.brute_force_optimal(graph, location_data,
                                                                         revenue_per_person,
                                                                         interference_distance,
                                                                         interference_penalty)
        result_profit = self.calculate_profit(result, graph, location_data, revenue_per_person, interference_distance, interference_penalty)
        self.assertEqual(result_profit, expected_profit)

    def test_single_node_profitable(self):
        graph = {1: []}
        location_data = {1: {'population': 1000, 'cost': 400}}
        revenue_per_person = 0.5
        interference_distance = 1
        interference_penalty = 0.2

        result = optimal_tower_placement(graph, location_data, revenue_per_person, interference_distance, interference_penalty)
        self.assertIsInstance(result, set)
        # For a single-node graph, interference does not apply
        profit_with = (1000 * revenue_per_person) - 400
        profit_without = 0
        expected = {1} if profit_with > profit_without else set()
        self.assertEqual(result, expected)

    def test_isolated_nodes(self):
        graph = {
            1: [],
            2: [],
            3: []
        }
        location_data = {
            1: {'population': 500, 'cost': 600},
            2: {'population': 800, 'cost': 700},
            3: {'population': 1000, 'cost': 900}
        }
        revenue_per_person = 1.0
        interference_distance = 1
        interference_penalty = 0.5

        result = optimal_tower_placement(graph, location_data, revenue_per_person, interference_distance, interference_penalty)
        expected = set()
        for node, data in location_data.items():
            profit = (data['population'] * revenue_per_person) - data['cost']
            if profit > 0:
                expected.add(node)
        self.assertEqual(result, expected)

    def test_negative_profit_all(self):
        graph = {
            1: [2],
            2: [1]
        }
        location_data = {
            1: {'population': 100, 'cost': 200},
            2: {'population': 150, 'cost': 300}
        }
        revenue_per_person = 1.0
        interference_distance = 1
        interference_penalty = 0.5

        result = optimal_tower_placement(graph, location_data, revenue_per_person, interference_distance, interference_penalty)
        self.assertEqual(result, set())

    def test_non_connected_graph(self):
        graph = {
            1: [2],
            2: [1],
            3: [4],
            4: [3],
            5: []
        }
        location_data = {
            1: {'population': 800, 'cost': 500},
            2: {'population': 900, 'cost': 600},
            3: {'population': 850, 'cost': 550},
            4: {'population': 700, 'cost': 400},
            5: {'population': 1000, 'cost': 800}
        }
        revenue_per_person = 0.8
        interference_distance = 2
        interference_penalty = 0.25

        result = optimal_tower_placement(graph, location_data, revenue_per_person, interference_distance, interference_penalty)
        self.assertIsInstance(result, set)
        # Verify that the result contains valid nodes
        for node in result:
            self.assertIn(node, graph)

if __name__ == '__main__':
    unittest.main()