import unittest
from service_router import min_total_latency


class ServiceRouterTest(unittest.TestCase):

    def test_example_case(self):
        N = 3
        dependencies = [(0, 1, 10), (0, 2, 5), (1, 2, 8)]
        D = 2
        G = 5
        expected = 46
        self.assertEqual(min_total_latency(N, dependencies, D, G), expected)

    def test_all_direct_routing(self):
        N = 4
        dependencies = [(0, 1, 5), (1, 2, 3), (2, 3, 7)]
        D = 1
        G = 10
        # Direct routing: 5*1 + 3*1 + 7*1 = 15
        # Group routing would be more expensive due to high G
        expected = 15
        self.assertEqual(min_total_latency(N, dependencies, D, G), expected)

    def test_all_group_routing(self):
        N = 4
        dependencies = [(0, 3, 20), (1, 3, 30), (2, 3, 50)]
        D = 5
        G = 10
        # Direct routing: 20*5 + 30*5 + 50*5 = 500
        # Group routing: (20+30+50)*(5+10/100) = 100*5.1 = 510
        # Direct routing is cheaper here
        expected = 500
        self.assertEqual(min_total_latency(N, dependencies, D, G), expected)

    def test_mixed_routing(self):
        N = 5
        dependencies = [(0, 1, 10), (2, 1, 15), (3, 1, 5), (0, 4, 20), (2, 4, 10)]
        D = 3
        G = 6
        # For destination 1:
        # Direct routing: 10*3 + 15*3 + 5*3 = 90
        # Group routing: (10+15+5)*(3+6/30) = 30*3.2 = 96
        # For destination 4:
        # Direct routing: 20*3 + 10*3 = 90
        # Group routing: (20+10)*(3+6/30) = 30*3.2 = 96
        # Best choice: Direct routing for both destinations = 90 + 90 = 180
        expected = 180
        self.assertEqual(min_total_latency(N, dependencies, D, G), expected)

    def test_group_routing_advantage(self):
        N = 4
        dependencies = [(0, 3, 100), (1, 3, 100), (2, 3, 100)]
        D = 5
        G = 1
        # Direct routing: 100*5 + 100*5 + 100*5 = 1500
        # Group routing: (100+100+100)*(5+1/300) = 300*5.003 = 1500.9 (rounds to 1501)
        # Direct routing is slightly cheaper
        expected = 1500
        self.assertEqual(min_total_latency(N, dependencies, D, G), expected)

    def test_multiple_destinations(self):
        N = 5
        dependencies = [
            (0, 1, 50), (0, 2, 30), (0, 3, 20), (0, 4, 10),
            (1, 2, 40), (1, 3, 30), (1, 4, 20),
            (2, 3, 50), (2, 4, 40),
            (3, 4, 60)
        ]
        D = 2
        G = 4
        # For each destination, we need to decide between direct and group routing
        expected = 700  # Calculated by hand checking each destination separately
        self.assertEqual(min_total_latency(N, dependencies, D, G), expected)

    def test_large_numbers(self):
        N = 3
        dependencies = [(0, 1, 1000), (0, 2, 1000), (1, 2, 1000)]
        D = 1000
        G = 1000
        # Direct routing for service 1: 1000*1000 = 1,000,000
        # Direct routing for service 2: 1000*1000 + 1000*1000 = 2,000,000
        # Group routing for service 2: (1000+1000)*(1000+1000/2000) = 2000*1000.5 = 2,001,000
        expected = 3000000
        self.assertEqual(min_total_latency(N, dependencies, D, G), expected)

    def test_single_message(self):
        N = 2
        dependencies = [(0, 1, 1)]
        D = 5
        G = 10
        # Only one message to send, direct routing: 1*5 = 5
        # Group routing doesn't make sense as there's only one source
        expected = 5
        self.assertEqual(min_total_latency(N, dependencies, D, G), expected)

    def test_no_dependencies(self):
        N = 5
        dependencies = []
        D = 3
        G = 6
        # No messages to send, so total latency is 0
        expected = 0
        self.assertEqual(min_total_latency(N, dependencies, D, G), expected)

    def test_equal_direct_and_group_cost(self):
        N = 3
        dependencies = [(0, 2, 5), (1, 2, 5)]
        D = 10
        G = 50
        # Direct: 5*10 + 5*10 = 100
        # Group: (5+5)*(10+50/10) = 10*15 = 150
        # Direct is cheaper
        expected = 100
        self.assertEqual(min_total_latency(N, dependencies, D, G), expected)


if __name__ == "__main__":
    unittest.main()