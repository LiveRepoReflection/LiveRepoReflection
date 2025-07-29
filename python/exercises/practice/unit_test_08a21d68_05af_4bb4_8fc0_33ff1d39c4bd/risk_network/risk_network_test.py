import unittest
import math
from risk_network import compute_risk_paths

class RiskNetworkTest(unittest.TestCase):
    def test_single_source_multiple_updates(self):
        # Graph:
        # 0 -> 1 (10), 0 -> 2 (15), 1 -> 3 (12), 2 -> 3 (10)
        # sources = [0], target = 3
        n = 4
        edges = [(0, 1, 10.0), (0, 2, 15.0), (1, 3, 12.0), (2, 3, 10.0)]
        sources = [0]
        target = 3
        updates = [
            (1, 0, 1, 5.0),   # edge 0->1 becomes 15.0
            (2, 2, 3, 3.0),   # edge 2->3 becomes 13.0
            (3, 1, 3, 7.0)    # edge 1->3 becomes 19.0
        ]
        # After update 1:
        # 0->1:15, 0->2:15, paths: 0->1->3 =15+12 = 27, 0->2->3 =15+10 = 25
        # Expected shortest risk: 25.0
        # After update 2:
        # 0->1:15, 0->2:15, 2->3:13, paths: 0->1->3 =15+12=27, 0->2->3 =15+13 = 28
        # Expected shortest risk: 27.0
        # After update 3:
        # 0->1:15, 1->3:19, 0->2:15, 2->3:13, paths: 0->1->3 =15+19=34, 0->2->3 =15+13=28
        # Expected shortest risk: 28.0
        expected = [25.0, 27.0, 28.0]
        result = compute_risk_paths(n, edges, sources, target, updates)
        self.assertEqual(len(result), len(expected))
        for got, exp in zip(result, expected):
            self.assertAlmostEqual(got, exp, places=5)

    def test_multiple_sources(self):
        # Graph:
        # 0 -> 2 (5), 1 -> 2 (3), 2 -> 3 (2), 3 -> 4 (1), 1 -> 4 (10)
        # sources = [0, 1], target = 4
        n = 5
        edges = [(0, 2, 5.0), (1, 2, 3.0), (2, 3, 2.0), (3, 4, 1.0), (1, 4, 10.0)]
        sources = [0, 1]
        target = 4
        updates = [
            (1, 1, 2, 4.0),   # edge 1->2 becomes 7.0
            (2, 2, 3, 5.0)    # edge 2->3 becomes 7.0
        ]
        # After update 1:
        # Paths:
        # From 0: 0->2->3->4 = 5+2+1 = 8.0
        # From 1: 1->2->3->4 = 7+2+1 = 10.0, or direct 1->4=10.0 => 10.0
        # Expected shortest risk: 8.0
        # After update 2:
        # From 0: 0->2->3->4 = 5+7+1 = 13.0
        # From 1: 1->4 = 10.0 remains the same (direct path unchanged) 
        # Expected shortest risk: 10.0
        expected = [8.0, 10.0]
        result = compute_risk_paths(n, edges, sources, target, updates)
        self.assertEqual(len(result), len(expected))
        for got, exp in zip(result, expected):
            self.assertAlmostEqual(got, exp, places=5)

    def test_no_path_available(self):
        # Graph:
        # 0 -> 1 (1)
        # No edge leading to target (2)
        n = 3
        edges = [(0, 1, 1.0)]
        sources = [0]
        target = 2
        updates = [
            (1, 0, 1, 2.0),  # This update should not produce a path to target
        ]
        expected = [float('inf')]
        result = compute_risk_paths(n, edges, sources, target, updates)
        self.assertEqual(len(result), len(expected))
        for got, exp in zip(result, expected):
            if math.isinf(exp):
                self.assertTrue(math.isinf(got))
            else:
                self.assertAlmostEqual(got, exp, places=5)

    def test_multiple_updates_effect(self):
        # More complex scenario: repeatedly increasing risk on a critical edge.
        # Graph:
        # 0 -> 1 (2), 1 -> 2 (2), 2 -> 3 (2), 0 -> 3 (10)
        # sources = [0], target = 3
        n = 4
        edges = [(0, 1, 2.0), (1, 2, 2.0), (2, 3, 2.0), (0, 3, 10.0)]
        sources = [0]
        target = 3
        updates = [
            (1, 1, 2, 1.0),  # edge 1->2 becomes 3
            (2, 2, 3, 2.0),  # edge 2->3 becomes 4
            (3, 0, 1, 3.0),  # edge 0->1 becomes 5
            (4, 0, 3, 1.0)   # edge 0->3 becomes 11
        ]
        # Initially, best path is 0->1->2->3 = 2+2+2 = 6.0
        # After update 1: path becomes 2+3+2 = 7.0, direct: 10 remains; answer = 7.0
        # After update 2: path becomes 2+3+4 = 9.0, direct: 10 remains; answer = 9.0
        # After update 3: path becomes 5+3+4 = 12.0, direct: 10 remains; answer = 10.0
        # After update 4: direct path becomes 11; compare with 12.0; answer = 11.0
        expected = [7.0, 9.0, 10.0, 11.0]
        result = compute_risk_paths(n, edges, sources, target, updates)
        self.assertEqual(len(result), len(expected))
        for got, exp in zip(result, expected):
            self.assertAlmostEqual(got, exp, places=5)

if __name__ == '__main__':
    unittest.main()