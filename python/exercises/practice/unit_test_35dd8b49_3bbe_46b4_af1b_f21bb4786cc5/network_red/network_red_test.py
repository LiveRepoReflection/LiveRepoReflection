import unittest
from network_red import process_packets
import random

class NetworkRedTest(unittest.TestCase):
    def setUp(self):
        # Fix random seed for reproducible tests
        random.seed(42)

    def test_single_output_no_congestion(self):
        packets = [(0, 0, 5), (1, 0, 5)]  # Two small packets for output 0
        num_outputs = 1
        bandwidth_capacities = [10]  # Can handle 10 bytes per time unit
        queue_size_limit = 10
        red_parameters = {
            'min_threshold': 3,
            'max_threshold': 8,
            'max_p': 0.7
        }

        transmitted, dropped, final_queues = process_packets(
            packets, num_outputs, bandwidth_capacities, 
            queue_size_limit, red_parameters
        )

        self.assertEqual(len(transmitted), 2)  # Both packets should be transmitted
        self.assertEqual(len(dropped), 0)  # No packets should be dropped
        self.assertEqual(final_queues, [[]])  # Queue should be empty at end

    def test_queue_size_limit(self):
        # Create packets that would overflow the queue
        packets = [(0, 0, 5)] * 12  # 12 packets for output 0
        num_outputs = 1
        bandwidth_capacities = [5]  # Can handle 5 bytes per time unit
        queue_size_limit = 10
        red_parameters = {
            'min_threshold': 3,
            'max_threshold': 8,
            'max_p': 0.7
        }

        transmitted, dropped, final_queues = process_packets(
            packets, num_outputs, bandwidth_capacities, 
            queue_size_limit, red_parameters
        )

        self.assertTrue(len(dropped) > 0)  # Some packets should be dropped
        self.assertTrue(len(final_queues[0]) <= queue_size_limit)

    def test_multiple_outputs(self):
        packets = [
            (0, 0, 5),  # For output 0
            (0, 1, 5),  # For output 1
            (1, 0, 5),
            (1, 1, 5)
        ]
        num_outputs = 2
        bandwidth_capacities = [10, 10]
        queue_size_limit = 10
        red_parameters = {
            'min_threshold': 3,
            'max_threshold': 8,
            'max_p': 0.7
        }

        transmitted, dropped, final_queues = process_packets(
            packets, num_outputs, bandwidth_capacities, 
            queue_size_limit, red_parameters
        )

        self.assertEqual(len(transmitted), 4)  # All packets should be transmitted
        self.assertEqual(len(dropped), 0)  # No packets should be dropped
        self.assertEqual(final_queues, [[], []])  # Both queues should be empty

    def test_red_dropping(self):
        # Create enough packets to trigger RED dropping
        packets = [(i, 0, 5) for i in range(20)]  # 20 packets arriving sequentially
        num_outputs = 1
        bandwidth_capacities = [2]  # Slow bandwidth to cause congestion
        queue_size_limit = 15
        red_parameters = {
            'min_threshold': 5,
            'max_threshold': 10,
            'max_p': 1.0  # 100% drop probability at max threshold
        }

        transmitted, dropped, final_queues = process_packets(
            packets, num_outputs, bandwidth_capacities, 
            queue_size_limit, red_parameters
        )

        self.assertTrue(len(dropped) > 0)  # Some packets should be dropped due to RED
        self.assertTrue(len(final_queues[0]) <= queue_size_limit)

    def test_partial_packet_transmission(self):
        packets = [(0, 0, 15)]  # One large packet
        num_outputs = 1
        bandwidth_capacities = [10]  # Can only transmit 10 bytes per time unit
        queue_size_limit = 10
        red_parameters = {
            'min_threshold': 3,
            'max_threshold': 8,
            'max_p': 0.7
        }

        transmitted, dropped, final_queues = process_packets(
            packets, num_outputs, bandwidth_capacities, 
            queue_size_limit, red_parameters
        )

        self.assertEqual(len(transmitted), 1)  # Packet should be transmitted
        self.assertEqual(transmitted[0][2], 15)  # Full packet size should be recorded
        self.assertEqual(len(dropped), 0)  # No packets should be dropped

    def test_empty_input(self):
        packets = []
        num_outputs = 1
        bandwidth_capacities = [10]
        queue_size_limit = 10
        red_parameters = {
            'min_threshold': 3,
            'max_threshold': 8,
            'max_p': 0.7
        }

        transmitted, dropped, final_queues = process_packets(
            packets, num_outputs, bandwidth_capacities, 
            queue_size_limit, red_parameters
        )

        self.assertEqual(len(transmitted), 0)
        self.assertEqual(len(dropped), 0)
        self.assertEqual(final_queues, [[]])

    def test_invalid_output_port(self):
        packets = [(0, 1, 5)]  # Output port 1, but only 1 output exists
        num_outputs = 1
        bandwidth_capacities = [10]
        queue_size_limit = 10
        red_parameters = {
            'min_threshold': 3,
            'max_threshold': 8,
            'max_p': 0.7
        }

        with self.assertRaises(ValueError):
            process_packets(packets, num_outputs, bandwidth_capacities, 
                          queue_size_limit, red_parameters)

    def test_max_constraints(self):
        # Test with maximum allowed constraints
        packets = [(i, i % 100, 1000) for i in range(1000)]
        num_outputs = 100
        bandwidth_capacities = [1000] * 100
        queue_size_limit = 1000
        red_parameters = {
            'min_threshold': 0,
            'max_threshold': 1000,
            'max_p': 1.0
        }

        transmitted, dropped, final_queues = process_packets(
            packets, num_outputs, bandwidth_capacities, 
            queue_size_limit, red_parameters
        )

        self.assertTrue(len(transmitted) + len(dropped) == len(packets))
        self.assertTrue(all(len(q) <= queue_size_limit for q in final_queues))

if __name__ == '__main__':
    unittest.main()