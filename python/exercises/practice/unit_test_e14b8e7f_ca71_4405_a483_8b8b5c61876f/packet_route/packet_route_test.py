import unittest
from packet_route import optimal_packet_route

class TestOptimalPacketRoute(unittest.TestCase):
    def test_direct_route(self):
        network = {
            1: {2: {'cost': 5, 'bandwidth': 100}},
            2: {}
        }
        self.assertEqual(optimal_packet_route(network, 1, 2, 1), [1, 2])

    def test_source_equals_destination(self):
        network = {
            1: {}
        }
        self.assertEqual(optimal_packet_route(network, 1, 1, 1), [1])

    def test_bandwidth_zero(self):
        network = {
            1: {2: {'cost': 10, 'bandwidth': 0}},
            2: {}
        }
        self.assertEqual(optimal_packet_route(network, 1, 2, 1), [])

    def test_no_path(self):
        network = {
            1: {2: {'cost': 5, 'bandwidth': 100}},
            2: {},
            3: {4: {'cost': 1, 'bandwidth': 100}},
            4: {}
        }
        self.assertEqual(optimal_packet_route(network, 1, 4, 1), [])

    def test_congestion_penalty_no_extra(self):
        # This test uses a packet size that does not trigger the congestion penalty.
        network = {
            1: {
                2: {'cost': 10, 'bandwidth': 100},
                3: {'cost': 5, 'bandwidth': 50}
            },
            2: {4: {'cost': 10, 'bandwidth': 60}},
            3: {4: {'cost': 20, 'bandwidth': 200}},
            4: {}
        }
        # For packet_size = 1 MB, the utilization ratios are below 0.8 for all edges.
        # Expected optimal route: [1, 2, 4] with total cost 10 + 10 = 20 versus [1, 3, 4] with cost 5 + 20 = 25.
        self.assertEqual(optimal_packet_route(network, 1, 4, 1), [1, 2, 4])

    def test_congestion_penalty_with_extra(self):
        # This test uses a packet size that triggers the congestion penalty.
        network = {
            1: {
                2: {'cost': 10, 'bandwidth': 100},
                3: {'cost': 5, 'bandwidth': 100}
            },
            2: {4: {'cost': 10, 'bandwidth': 100}},
            3: {4: {'cost': 20, 'bandwidth': 500}},
            4: {}
        }
        # For packet_size = 11 MB:
        # Route [1,2,4]:
        #   Edge (1,2): utilization = (11*8)/100 = 0.88, penalty = 10*(0.08)*5 = 4, effective cost = 14.
        #   Edge (2,4): utilization = 0.88, penalty = 10*(0.08)*5 = 4, effective cost = 14.
        #   Total cost = 28.
        # Route [1,3,4]:
        #   Edge (1,3): utilization = 0.88, penalty = 5*(0.08)*5 = 2, effective cost = 7.
        #   Edge (3,4): utilization = (11*8)/500 = 0.176, no penalty, effective cost = 20.
        #   Total cost = 27.
        # Expected optimal route: [1, 3, 4]
        self.assertEqual(optimal_packet_route(network, 1, 4, 11), [1, 3, 4])

if __name__ == '__main__':
    unittest.main()