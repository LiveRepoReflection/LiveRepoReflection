import unittest
from network_flow_allocation import allocate_flows

class TestNetworkFlowAllocation(unittest.TestCase):

    def test_single_path(self):
        # Graph: 0 -> 1, capacity 50, latency 1.
        # Single commodity: (0, 1, demand 50, priority 1).
        snapshot = {
            'num_nodes': 2,
            'edges': [
                (0, 1, 50, 1)
            ],
            'commodities': [
                (0, 1, 50, 1)
            ]
        }
        result = allocate_flows(snapshot)
        expected = [50]
        self.assertEqual(result, expected, msg="Single path allocation failed.")

    def test_parallel_paths(self):
        # Graph has two parallel paths from 0 to 3:
        # Path1: 0->1 (30, latency 1), 1->3 (30, latency 1)
        # Path2: 0->2 (20, latency 2), 2->3 (20, latency 2)
        # Commodity: (0, 3, demand 40, priority 5)
        snapshot = {
            'num_nodes': 4,
            'edges': [
                (0, 1, 30, 1),
                (1, 3, 30, 1),
                (0, 2, 20, 2),
                (2, 3, 20, 2)
            ],
            'commodities': [
                (0, 3, 40, 5)
            ]
        }
        result = allocate_flows(snapshot)
        expected_total = 40
        self.assertEqual(result[0], expected_total, msg="Parallel paths allocation failed.")

    def test_insufficient_capacity(self):
        # Graph: Single edge from 0 to 1, capacity 30, demand 50.
        snapshot = {
            'num_nodes': 2,
            'edges': [
                (0, 1, 30, 1)
            ],
            'commodities': [
                (0, 1, 50, 1)
            ]
        }
        result = allocate_flows(snapshot)
        # Expected flow is limited by edge capacity.
        expected = [30]
        self.assertEqual(result, expected, msg="Allocation with insufficient capacity failed.")

    def test_priority_allocation(self):
        # Graph: single edge that is shared by two commodities.
        # Edge capacity is 50. Two commodities:
        # Commodity1: (0, 1, demand 30, priority 10) - high priority.
        # Commodity2: (0, 1, demand 30, priority 1)  - low priority.
        # Expected: Commodity1 gets its full 30, Commodity2 gets remaining 20.
        snapshot = {
            'num_nodes': 2,
            'edges': [
                (0, 1, 50, 1)
            ],
            'commodities': [
                (0, 1, 30, 10),
                (0, 1, 30, 1)
            ]
        }
        result = allocate_flows(snapshot)
        expected = [30, 20]
        self.assertEqual(result, expected, msg="Priority allocation failed.")

    def test_path_diversity(self):
        # Graph: Two paths from 0 to 3 with equal capacities.
        # Path1: 0->1 (20, latency 1), 1->3 (20, latency 1)
        # Path2: 0->2 (20, latency 2), 2->3 (20, latency 2)
        # Commodity: (0, 3, demand 35, priority 5)
        # Expected: Total allocated flow is 35 (distributed across both paths).
        snapshot = {
            'num_nodes': 4,
            'edges': [
                (0, 1, 20, 1),
                (1, 3, 20, 1),
                (0, 2, 20, 2),
                (2, 3, 20, 2)
            ],
            'commodities': [
                (0, 3, 35, 5)
            ]
        }
        result = allocate_flows(snapshot)
        expected_total = 35
        self.assertEqual(result[0], expected_total, msg="Flow allocation across diverse paths failed.")

    def test_multiple_snapshots(self):
        # Test multiple snapshots sequentially.
        # Snapshot 1: Similar to test_single_path.
        snapshot1 = {
            'num_nodes': 2,
            'edges': [
                (0, 1, 50, 1)
            ],
            'commodities': [
                (0, 1, 50, 1)
            ]
        }
        # Snapshot 2: Similar to test_insufficient_capacity.
        snapshot2 = {
            'num_nodes': 2,
            'edges': [
                (0, 1, 30, 1)
            ],
            'commodities': [
                (0, 1, 50, 1)
            ]
        }
        result1 = allocate_flows(snapshot1)
        result2 = allocate_flows(snapshot2)
        self.assertEqual(result1, [50], msg="Multiple snapshots: snapshot1 failed.")
        self.assertEqual(result2, [30], msg="Multiple snapshots: snapshot2 failed.")

if __name__ == '__main__':
    unittest.main()