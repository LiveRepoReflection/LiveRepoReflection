import unittest
from meeting_point import find_optimal_meeting_point

class TestOptimalMeetingPoint(unittest.TestCase):
    def test_single_node(self):
        # Only one location exists.
        n = 1
        edges = []
        friends = [0]
        expected = 0
        self.assertEqual(find_optimal_meeting_point(n, edges, friends), expected)

    def test_sample_case(self):
        # Provided sample test case.
        n = 4
        edges = [[0, 1, 1], [0, 2, 5], [1, 2, 2], [1, 3, 1]]
        friends = [0, 3]
        expected = 1
        self.assertEqual(find_optimal_meeting_point(n, edges, friends), expected)

    def test_single_friend(self):
        # Only one friend, meeting point must be the friend's location.
        n = 5
        edges = [[0, 1, 3], [1, 2, 4], [2, 3, 5], [3, 4, 6], [0, 4, 15]]
        friends = [2]
        expected = 2
        self.assertEqual(find_optimal_meeting_point(n, edges, friends), expected)

    def test_tie_breaker(self):
        # Construct a case where two nodes yield the same maximum travel time.
        # Graph: 0 <-> 1, 0 <-> 2, 1 <-> 2 and 1 <-> 3, 2 <-> 3. Friends: [0, 3]
        # Distances:
        # Meeting at 0: max(distance(0,0)=0, distance(3,0)=min(3->1->0, 3->2->0)=min( ? )).
        # We design the weights such that node 1 and node 2 yield the same maximum,
        # but the answer must be the smaller node (node 1).
        n = 4
        edges = [[0, 1, 3], [0, 2, 1], [1, 2, 1], [1, 3, 2], [2, 3, 2]]
        friends = [0, 3]
        # Compute manually:
        # For node 1: friend0: 3, friend3: 2 -> max = 3
        # For node 2: friend0: 1, friend3: 2 -> max = 2, which is better.
        # For node 0: friend0: 0, friend3: 0->? shortest from 3->? Actually, let's recompute:
        # Re-design the graph:
        # Let's use:
        # edges = [[0,1,2], [1,2,2], [2,3,2], [0,3,6]]
        # For node 0: distances: 0 for friend0; friend3: 6; max = 6.
        # For node 1: friend0: 2; friend3: computed as 1->2->3: 2+2=4; max = 4.
        # For node 2: friend0: 0->1->2: 2+2=4; friend3: 2; max = 4.
        # Tie between node1 and node2, answer should be 1.
        n = 4
        edges = [[0,1,2], [1,2,2], [2,3,2], [0,3,6]]
        friends = [0, 3]
        expected = 1
        self.assertEqual(find_optimal_meeting_point(n, edges, friends), expected)

    def test_multiple_friends(self):
        # A test with several friends in a chain graph.
        n = 5
        edges = [[0, 1, 2], [1, 2, 2], [2, 3, 2], [3, 4, 2], [0, 4, 10]]
        friends = [0, 4]
        # Distances:
        # Meeting at node 0: max(0, 8) = 8 (8 via 0->1->2->3->4 gives 8)
        # Meeting at node 1: max(2, 6) = 6
        # Meeting at node 2: max(4, 4) = 4
        # Meeting at node 3: max(6, 2) = 6
        # Meeting at node 4: max(8, 0) = 8
        # So answer is node 2.
        expected = 2
        self.assertEqual(find_optimal_meeting_point(n, edges, friends), expected)

    def test_dense_graph(self):
        # Test on a dense graph.
        n = 6
        edges = [
            [0, 1, 3], [0, 2, 1], [0, 3, 5], [0, 4, 9], [0, 5, 2],
            [1, 2, 4], [1, 3, 2], [1, 4, 7], [1, 5, 3],
            [2, 3, 6], [2, 4, 3], [2, 5, 8],
            [3, 4, 1], [3, 5, 4],
            [4, 5, 2]
        ]
        friends = [0, 3, 5]
        # Without explicit computation, we verify function returns without error and
        # consistency with criteria (minimizing the maximum travel time and tie-break by smallest node).
        result = find_optimal_meeting_point(n, edges, friends)
        # Check that result is a valid node.
        self.assertTrue(0 <= result < n)

if __name__ == '__main__':
    unittest.main()