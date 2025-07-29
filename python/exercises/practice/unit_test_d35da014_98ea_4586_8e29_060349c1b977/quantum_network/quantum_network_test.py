import unittest
from quantum_network import find_most_resilient_component

class QuantumNetworkTest(unittest.TestCase):
    def test_empty_network(self):
        self.assertEqual(find_most_resilient_component(0, []), 0)

    def test_single_lab_no_links(self):
        self.assertEqual(find_most_resilient_component(1, []), 0)

    def test_two_labs_single_link(self):
        self.assertEqual(find_most_resilient_component(2, [(0, 1, 5)]), 5)

    def test_self_loop(self):
        self.assertEqual(find_most_resilient_component(2, [(0, 0, 10), (0, 1, 5)]), 5)

    def test_multiple_components(self):
        links = [
            (0, 1, 10),
            (1, 2, 15),
            (3, 4, 20),
            (4, 5, 25)
        ]
        self.assertEqual(find_most_resilient_component(6, links), 20)

    def test_complex_network(self):
        links = [
            (0, 1, 100),
            (1, 2, 200),
            (2, 3, 50),
            (3, 0, 75),
            (4, 5, 300),
            (5, 6, 250),
            (6, 4, 150)
        ]
        self.assertEqual(find_most_resilient_component(7, links), 150)

    def test_disconnected_labs(self):
        links = [
            (0, 1, 10),
            (2, 3, 20),
            (4, 5, 30),
            (6, 7, 40)
        ]
        self.assertEqual(find_most_resilient_component(9, links), 40)

    def test_single_component_varying_fragility(self):
        links = [
            (0, 1, 100),
            (1, 2, 50),
            (2, 3, 75),
            (3, 0, 25)
        ]
        self.assertEqual(find_most_resilient_component(4, links), 25)

    def test_invalid_lab_number(self):
        with self.assertRaises(ValueError):
            find_most_resilient_component(-1, [(0, 1, 5)])

    def test_invalid_fragility(self):
        with self.assertRaises(ValueError):
            find_most_resilient_component(2, [(0, 1, -5)])

    def test_invalid_lab_index(self):
        with self.assertRaises(ValueError):
            find_most_resilient_component(2, [(0, 2, 5)])

    def test_duplicate_links(self):
        links = [
            (0, 1, 10),
            (1, 0, 20),  # Same link as above but different fragility
            (1, 2, 30)
        ]
        self.assertEqual(find_most_resilient_component(3, links), 20)

    def test_large_network(self):
        # Create a large network to test performance
        links = []
        n = 1000
        for i in range(n-1):
            links.append((i, i+1, i+100))
        self.assertEqual(find_most_resilient_component(n, links), 100)

    def test_maximum_constraints(self):
        # Test with maximum allowed constraints
        n = 10**5
        links = []
        for i in range(min(2 * 10**5, n-1)):
            links.append((i, i+1, 10**9))
        self.assertEqual(find_most_resilient_component(n, links), 10**9)

if __name__ == '__main__':
    unittest.main()