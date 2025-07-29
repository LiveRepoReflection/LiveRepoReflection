import math
import unittest
from data_xfer import min_total_cost

class DataXferTest(unittest.TestCase):
    def test_all_replication_available(self):
        N = 3
        dependencies = [
            (0, 1, 101, 50),
            (1, 2, 102, 30),
            (0, 2, 101, 20)
        ]
        bandwidth = [
            [0, 10, 5],
            [10, 0, 8],
            [5, 8, 0]
        ]
        cost = [
            [float('inf'), 2, 3],
            [2, float('inf'), 1],
            [3, 1, float('inf')]
        ]
        data_replication = {101: {0}, 102: {1}}
        result = min_total_cost(N, dependencies, bandwidth, cost, data_replication)
        self.assertEqual(result, 0)

    def test_direct_transfer(self):
        N = 2
        dependencies = [
            (0, 1, 101, 100)
        ]
        bandwidth = [
            [0, 10],
            [10, 0]
        ]
        cost = [
            [float('inf'), 2],
            [2, float('inf')]
        ]
        data_replication = {}
        result = min_total_cost(N, dependencies, bandwidth, cost, data_replication)
        self.assertEqual(result, 200)

    def test_best_source_selection(self):
        N = 4
        dependencies = [
            (0, 3, 101, 50)
        ]
        bandwidth = [
            [0, 10, 5, 3],
            [10, 0, 8, 4],
            [5, 8, 0, 6],
            [3, 4, 6, 0]
        ]
        cost = [
            [float('inf'), 3, 2, 10],
            [3, float('inf'), 4, 7],
            [2, 4, float('inf'), 6],
            [10, 7, 6, float('inf')]
        ]
        data_replication = {101: {1, 2}}
        result = min_total_cost(N, dependencies, bandwidth, cost, data_replication)
        self.assertEqual(result, 100)

    def test_no_bandwidth_available(self):
        N = 2
        dependencies = [
            (0, 1, 101, 50)
        ]
        bandwidth = [
            [0, 0],
            [0, 0]
        ]
        cost = [
            [float('inf'), 2],
            [2, float('inf')]
        ]
        data_replication = {}
        result = min_total_cost(N, dependencies, bandwidth, cost, data_replication)
        self.assertEqual(result, float('inf'))

    def test_mixed_dependencies(self):
        N = 5
        dependencies = [
            (0, 4, 201, 40),
            (1, 4, 202, 60),
            (2, 3, 203, 30),
            (0, 2, 204, 20)
        ]
        bandwidth = [
            [0, 8, 10, 5, 3],
            [8, 0, 6, 7, 4],
            [10, 6, 0, 9, 2],
            [5, 7, 9, 0, 8],
            [3, 4, 2, 8, 0]
        ]
        cost = [
            [float('inf'), 4, 3, 8, 7],
            [4, float('inf'), 5, 2, 6],
            [3, 5, float('inf'), 1, 9],
            [8, 2, 1, float('inf'), 3],
            [7, 6, 9, 3, float('inf')]
        ]
        # For dependency (0, 4, 201, 40): 201 is replicated in {0, 1}. Since 0 already has it, cost = 0.
        # For dependency (1, 4, 202, 60): no replication, so transfer from 1 to 4 costs 6 * 60 = 360.
        # For dependency (2, 3, 203, 30): 203 is replicated in {2, 3}. Since 2 or 3 has it, cost = 0.
        # For dependency (0, 2, 204, 20): no replication, so transfer from 0 to 2 costs 3 * 20 = 60.
        # Total expected cost = 0 + 360 + 0 + 60 = 420.
        data_replication = {201: {0, 1}, 203: {2, 3}}
        result = min_total_cost(N, dependencies, bandwidth, cost, data_replication)
        self.assertEqual(result, 420)

if __name__ == '__main__':
    unittest.main()