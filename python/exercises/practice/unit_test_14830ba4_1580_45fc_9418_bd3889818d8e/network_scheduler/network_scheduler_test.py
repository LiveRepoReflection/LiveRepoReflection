import unittest
import time
from network_scheduler import network_scheduler

class TestNetworkScheduler(unittest.TestCase):
    def test_single_edge_conflict(self):
        # Network: 2 nodes, one link with capacity 10.
        n = 2
        links = [(0, 1, 10)]
        current_time = int(time.time())
        # Two jobs competing for the same link:
        # Job0: require 5 units, priority 1; Job1: require 7 units, priority 2.
        # Only one job can be scheduled due to capacity constraints.
        jobs = [
            (0, 1, 5, current_time + 100, 1), 
            (0, 1, 7, current_time + 100, 2)
        ]
        # Expected: only the higher priority job (job1) is scheduled.
        expected = [1]
        result = network_scheduler(n, links, jobs, current_time)
        self.assertEqual(sorted(result), expected)

    def test_multipath_single_job(self):
        # Network: 3 nodes with two paths from 0 to 2.
        # Path1: 0-1 (capacity 5) and 1-2 (capacity 5).
        # Path2: direct from 0 to 2 (capacity 2) which is insufficient.
        n = 3
        links = [
            (0, 1, 5),
            (1, 2, 5),
            (0, 2, 2)
        ]
        current_time = int(time.time())
        # Single job that requires 5 units bandwidth from 0 to 2.
        jobs = [
            (0, 2, 5, current_time + 100, 10)
        ]
        expected = [0]
        result = network_scheduler(n, links, jobs, current_time)
        self.assertEqual(sorted(result), expected)

    def test_expired_job(self):
        # Network: simple 2 node network.
        n = 2
        links = [(0, 1, 10)]
        current_time = int(time.time())
        # Job already expired (deadline in the past)
        jobs = [
            (0, 1, 5, current_time - 1, 10)
        ]
        expected = []
        result = network_scheduler(n, links, jobs, current_time)
        self.assertEqual(sorted(result), expected)

    def test_multiple_jobs_sufficient_capacity(self):
        # Network: 3 nodes with single clear path 0->1->2.
        n = 3
        links = [
            (0, 1, 10),
            (1, 2, 10)
        ]
        current_time = int(time.time())
        # Two jobs that can use the same route concurrently since total demand is 9 <= 10.
        jobs = [
            (0, 2, 5, current_time + 50, 3),  # Job0
            (0, 2, 4, current_time + 50, 2)   # Job1
        ]
        expected = [0, 1]
        result = network_scheduler(n, links, jobs, current_time)
        self.assertEqual(sorted(result), expected)

    def test_complex_scenario(self):
        # Network: 4 nodes with multiple paths.
        n = 4
        links = [
            (0, 1, 5),
            (1, 2, 5),
            (2, 3, 5),
            (0, 3, 5),
            (1, 3, 1)
        ]
        current_time = int(time.time())
        # Four jobs with potential conflicts:
        # Job0: (0->3) require 5, priority 10. Can use direct link (0,3).
        # Job1: (0->3) require 3, priority 7. Can use path 0->1->2->3.
        # Job2: (0->2) require 4, priority 5. Shares link (0,1) with job1.
        # Job3: (1->3) require 2, priority 8. Can potentially be routed via (1,2)->(2,3).
        # Optimal selection should consider maximizing total priority.
        # Best selection is Job0, Job1, and Job3, which gives a total priority of 10+7+8.
        jobs = [
            (0, 3, 5, current_time + 50, 10),  # Job0
            (0, 3, 3, current_time + 50, 7),   # Job1
            (0, 2, 4, current_time + 50, 5),   # Job2 - likely dropped due to resource contention.
            (1, 3, 2, current_time + 50, 8)    # Job3
        ]
        expected = [0, 1, 3]
        result = network_scheduler(n, links, jobs, current_time)
        self.assertEqual(sorted(result), expected)

if __name__ == '__main__':
    unittest.main()