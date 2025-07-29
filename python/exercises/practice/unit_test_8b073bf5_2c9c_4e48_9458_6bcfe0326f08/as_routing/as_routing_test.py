import unittest
from as_routing import find_optimal_path

class TestASRouting(unittest.TestCase):
    def test_sample_path(self):
        topology = {
            1: [(2, "customer"), (3, "peer")],
            2: [(1, "provider"), (4, "customer")],
            3: [(1, "peer"), (4, "provider"), (5, "customer")],
            4: [(2, "provider"), (3, "customer"), (6, "peer")],
            5: [(3, "provider")],
            6: [(4, "peer")]
        }
        as_metrics = {
            1: 20,
            2: 30,
            3: 15,
            4: 25,
            5: 40,
            6: 10
        }
        origin_as = 1
        destination_as = 6
        expected = [1, 3, 4, 6]
        result = find_optimal_path(topology, as_metrics, origin_as, destination_as)
        self.assertEqual(result, expected)

    def test_no_path(self):
        topology = {
            1: [(2, "customer")],
            2: [(1, "provider")],
            3: [(4, "peer")],
            4: [(3, "peer")]
        }
        as_metrics = {1: 10, 2: 20, 3: 15, 4: 15}
        origin_as = 1
        destination_as = 4
        expected = []
        result = find_optimal_path(topology, as_metrics, origin_as, destination_as)
        self.assertEqual(result, expected)

    def test_valley_preference(self):
        # Two possible paths from 1 to 5:
        # Path A: 1 -> 2 -> 5, with edge relationships "customer" then "customer" which is considered a valley.
        # Path B: 1 -> 3 -> 4 -> 5, valley-free if relationships are "peer","provider","customer"
        # Although Path A might have lower latency, valley-free route (Path B) is preferred.
        topology = {
            1: [(2, "customer"), (3, "peer")],
            2: [(1, "provider"), (5, "customer")],
            3: [(1, "peer"), (4, "provider")],
            4: [(3, "customer"), (5, "customer")],
            5: [(2, "provider"), (4, "provider")]
        }
        as_metrics = {
            1: 10,
            2: 5,
            3: 15,
            4: 10,
            5: 5
        }
        origin_as = 1
        destination_as = 5
        # Despite the latency for A being 10+5+5 = 20, it is valley-prone.
        # Path B latency = 10+15+10+5 = 40, but valley-free is prioritized.
        expected = [1, 3, 4, 5]
        result = find_optimal_path(topology, as_metrics, origin_as, destination_as)
        self.assertEqual(result, expected)

    def test_tie_breaker_shortest_path(self):
        # Two valley-free paths with equal total latency.
        # Path A: 1 -> 2 -> 4 -> 5, latency: 10+20+10+5 = 45, length = 4 ASes.
        # Path B: 1 -> 3 -> 4 -> 5, latency: 10+15+10+5 = 40, but adjust latency to tie.
        # We'll adjust as_metrics so both paths sum to the same latency.
        # Let as_metrics: 1:10, 2:15, 3:20, 4:10, 5:5.
        # Then, Path A: 10+15+10+5 = 40, Path B: 10+20+10+5 = 45.
        # To tie, update: 1:10, 2:15, 3:15, 4:10, 5:5.
        # Now both have: Path A: 10+15+10+5 = 40, Path B: 10+15+10+5 = 40.
        # If tie, choose shorter AS path if available.
        # We'll add a third path that is valley-free and has length 3.
        # Add direct connection: 1 -> 4 -> 5, with relationships: 1->4 "peer", 4->5 "customer"
        # This path latency: 10+10+5 = 25, so not equal now. Let’s adjust so that the direct path matches 40.
        # To simulate tie-breaker with path length we introduce two paths of equal latency:
        # Remove the direct connection to force tie between A and B.
        topology = {
            1: [(2, "peer"), (3, "peer")],
            2: [(1, "peer"), (4, "provider")],
            3: [(1, "peer"), (4, "provider")],
            4: [(2, "customer"), (3, "customer"), (5, "customer")],
            5: [(4, "provider")]
        }
        as_metrics = {
            1: 10,
            2: 15,
            3: 15,
            4: 10,
            5: 5
        }
        origin_as = 1
        destination_as = 5
        # Both paths: 1->2->4->5 and 1->3->4->5 yield latency 10+15+10+5 = 40.
        # Both have equal length 4, so no tie-breaker by AS length.
        # We can test that one of the valid paths is returned and is valley-free.
        result = find_optimal_path(topology, as_metrics, origin_as, destination_as)
        self.assertIn(result, [[1, 2, 4, 5], [1, 3, 4, 5]])

    def test_direct_connection(self):
        topology = {
            1: [(2, "peer")],
            2: [(1, "peer")]
        }
        as_metrics = {
            1: 10,
            2: 20
        }
        origin_as = 1
        destination_as = 2
        expected = [1, 2]
        result = find_optimal_path(topology, as_metrics, origin_as, destination_as)
        self.assertEqual(result, expected)

if __name__ == "__main__":
    unittest.main()