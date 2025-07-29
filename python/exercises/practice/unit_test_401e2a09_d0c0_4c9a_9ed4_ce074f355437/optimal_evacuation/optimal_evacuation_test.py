import unittest
from optimal_evacuation import optimal_evacuation

class OptimalEvacuationTest(unittest.TestCase):

    def test_example_case(self):
        graph = {
            1: [(2, 1), (3, 5)],
            2: [(1, 1), (4, 2)],
            3: [(1, 5), (4, 1)],
            4: [(2, 2), (3, 1)]
        }
        population = {
            1: 100,
            2: 50,
            3: 75,
            4: 25
        }
        evacuation_centers = [1, 4]
        result = optimal_evacuation(graph, population, evacuation_centers)
        self.assertEqual(result, 1)

    def test_chain_graph(self):
        graph = {
            1: [(2, 2)],
            2: [(1, 2), (3, 2)],
            3: [(2, 2), (4, 2)],
            4: [(3, 2)]
        }
        population = {
            1: 10,
            2: 20,
            3: 30,
            4: 40
        }
        evacuation_centers = [1]
        # Distances from node 1: 1->0, 2->2, 3->4, 4->6, max time = 6.
        result = optimal_evacuation(graph, population, evacuation_centers)
        self.assertEqual(result, 6)

    def test_unreachable_node(self):
        # Graph where node 3 is disconnected from nodes 1 and 2.
        graph = {
            1: [(2, 1)],
            2: [(1, 1)],
            3: []  # Node 3 is isolated.
        }
        population = {
            1: 5,
            2: 10,
            3: 15
        }
        evacuation_centers = [1]
        # Node 3 is unreachable from evacuation center.
        result = optimal_evacuation(graph, population, evacuation_centers)
        self.assertEqual(result, -1)

    def test_cycle_graph(self):
        # Create a cycle: 1-2-3-4-5-1 with weight 1 on each edge.
        graph = {
            1: [(2, 1), (5, 1)],
            2: [(1, 1), (3, 1)],
            3: [(2, 1), (4, 1)],
            4: [(3, 1), (5, 1)],
            5: [(4, 1), (1, 1)]
        }
        population = {
            1: 10,
            2: 10,
            3: 10,
            4: 10,
            5: 10
        }
        evacuation_centers = [3, 5]
        # Expected distances:
        # Node 1: min(distance to 5=1, to 3= ? via 2 or 5) = 1
        # Node 2: distance to 3=1, Node 3:0, Node 4:1, Node 5:0.
        # Maximum is 1.
        result = optimal_evacuation(graph, population, evacuation_centers)
        self.assertEqual(result, 1)

if __name__ == '__main__':
    unittest.main()