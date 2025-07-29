import unittest
from resource_network import resource_network

class TestResourceNetwork(unittest.TestCase):
    def test_no_transfer_needed(self):
        # Single planet where production exceeds needs; no trade required.
        n = 1
        needs = {0: (5, 5, 5)}
        production = {0: (7, 8, 10)}
        trade_routes = []
        C = 10
        # Expected cost is 0 because the planet already meets its needs.
        result = resource_network(n, needs, production, trade_routes, C)
        self.assertEqual(result, 0)

    def test_disconnected_impossible(self):
        # Two planets that are not connected, and each one lacks sufficient production.
        n = 2
        needs = {
            0: (10, 10, 10),
            1: (5, 5, 5)
        }
        production = {
            0: (5, 5, 5),
            1: (3, 3, 3)
        }
        # No trade routes available.
        trade_routes = []
        C = 50
        # Since each planet is isolated and cannot meet its needs, it is impossible.
        result = resource_network(n, needs, production, trade_routes, C)
        self.assertEqual(result, -1)

    def test_basic_transfer(self):
        # Two connected planets where one has surplus and one has a deficit.
        n = 2
        needs = {
            0: (10, 10, 10),
            1: (10, 10, 10)
        }
        production = {
            0: (20, 10, 10),  # surplus in energy: 10 extra energy
            1: (0, 10, 10)    # deficit in energy: 10 needed
        }
        trade_routes = [(0, 1, 3)]  # cost per unit is 3
        C = 40
        # To cover the 10 missing energy, cost = 10 * 3 = 30.
        result = resource_network(n, needs, production, trade_routes, C)
        self.assertEqual(result, 30)

    def test_multi_transfer(self):
        # Three planets with deficits in complementary resources.
        n = 3
        needs = {
            0: (15, 15, 15),
            1: (15, 15, 15),
            2: (15, 15, 15)
        }
        production = {
            0: (20, 15, 10),  # surplus energy=5, deficit water=5
            1: (10, 20, 15),  # surplus mineral=5, deficit energy=5
            2: (15, 10, 20)   # surplus water=5, deficit mineral=5
        }
        trade_routes = [
            (0, 1, 2),
            (1, 2, 2),
            (0, 2, 5)
        ]
        C = 50
        # Optimal transfers:
        # Planet 1 -> Planet 0: transfer 5 units of minerals: cost = 5*2 = 10.
        # Planet 0 -> Planet 1: transfer 5 units of energy: cost = 5*2 = 10.
        # Planet 2 -> Planet 0: transfer 5 units of water via (2->1->0) route with cost 2+2=4 each unit: cost = 5*4 = 20.
        # Total cost = 10 + 10 + 20 = 40.
        result = resource_network(n, needs, production, trade_routes, C)
        self.assertEqual(result, 40)

    def test_credit_line_failure(self):
        # Similar to basic transfer but credit line is insufficient.
        n = 2
        needs = {
            0: (10, 10, 10),
            1: (10, 10, 10)
        }
        production = {
            0: (20, 10, 10),  # surplus in energy: 10 extra energy
            1: (0, 10, 10)    # deficit in energy: 10 needed
        }
        trade_routes = [(0, 1, 3)]  # cost per unit is 3, so needed cost is 30.
        C = 25  # Credit line is too low.
        result = resource_network(n, needs, production, trade_routes, C)
        self.assertEqual(result, -1)

if __name__ == '__main__':
    unittest.main()