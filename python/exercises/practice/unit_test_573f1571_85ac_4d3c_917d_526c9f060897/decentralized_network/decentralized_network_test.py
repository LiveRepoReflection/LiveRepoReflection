import unittest
from decentralized_network import estimate_components


class DecentralizedNetworkTest(unittest.TestCase):
    def test_simple_network(self):
        n = 5
        user_data = [{}, {}, {}, {}, {}]
        friendships = [
            {1, 2},  # User 0's friends
            {0},     # User 1's friends
            {0},     # User 2's friends
            {4},     # User 3's friends
            {3}      # User 4's friends
        ]
        knowledge_depth = 2
        self.assertEqual(estimate_components(n, user_data, friendships, knowledge_depth), 2)

    def test_single_component(self):
        n = 4
        user_data = [{}, {}, {}, {}]
        friendships = [
            {1, 2, 3},
            {0, 2},
            {0, 1},
            {0}
        ]
        knowledge_depth = 2
        self.assertEqual(estimate_components(n, user_data, friendships, knowledge_depth), 1)

    def test_isolated_nodes(self):
        n = 5
        user_data = [{}, {}, {}, {}, {}]
        friendships = [
            set(),
            set(),
            set(),
            set(),
            set()
        ]
        knowledge_depth = 3
        self.assertEqual(estimate_components(n, user_data, friendships, knowledge_depth), 5)

    def test_complex_network(self):
        n = 8
        user_data = [{} for _ in range(n)]
        friendships = [
            {1, 2},      # Component 1
            {0, 2},
            {0, 1},
            {4},         # Component 2
            {3, 5},
            {4},
            set(),       # Component 3 (isolated)
            set()        # Component 4 (isolated)
        ]
        knowledge_depth = 2
        self.assertEqual(estimate_components(n, user_data, friendships, knowledge_depth), 4)

    def test_large_knowledge_depth(self):
        n = 6
        user_data = [{} for _ in range(n)]
        friendships = [
            {1},
            {0, 2},
            {1, 3},
            {2, 4},
            {3, 5},
            {4}
        ]
        knowledge_depth = 5
        self.assertEqual(estimate_components(n, user_data, friendships, knowledge_depth), 1)

    def test_limited_knowledge_depth(self):
        n = 6
        user_data = [{} for _ in range(n)]
        friendships = [
            {1},
            {0, 2},
            {1, 3},
            {2, 4},
            {3, 5},
            {4}
        ]
        knowledge_depth = 1
        result = estimate_components(n, user_data, friendships, knowledge_depth)
        self.assertGreaterEqual(result, 1)

    def test_medium_network(self):
        n = 10
        user_data = [{} for _ in range(n)]
        friendships = [
            {1, 2},      # Component 1
            {0, 2},
            {0, 1},
            {4, 5},      # Component 2
            {3, 5},
            {3, 4},
            {7, 8, 9},   # Component 3
            {6, 8},
            {6, 7},
            {6}
        ]
        knowledge_depth = 3
        self.assertEqual(estimate_components(n, user_data, friendships, knowledge_depth), 3)

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            estimate_components(0, [], [], 2)
        
        with self.assertRaises(ValueError):
            estimate_components(5, [{} for _ in range(5)], [], 2)
        
        with self.assertRaises(ValueError):
            estimate_components(5, [{} for _ in range(5)], 
                             [{1}, {0}, {3}, {2}, {5}], 0)

    def test_large_network(self):
        n = 100
        user_data = [{} for _ in range(n)]
        # Create 10 separate components of 10 nodes each
        friendships = [set() for _ in range(n)]
        for i in range(0, n, 10):
            for j in range(i, i + 9):
                friendships[j].add(j + 1)
                friendships[j + 1].add(j)
        
        knowledge_depth = 3
        self.assertEqual(estimate_components(n, user_data, friendships, knowledge_depth), 10)

if __name__ == '__main__':
    unittest.main()