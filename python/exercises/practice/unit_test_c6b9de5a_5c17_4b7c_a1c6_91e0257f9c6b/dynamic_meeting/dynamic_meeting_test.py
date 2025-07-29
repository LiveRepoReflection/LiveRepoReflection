import unittest
from dynamic_meeting import optimal_meeting_point

class DynamicMeetingTest(unittest.TestCase):
    def test_case_simple_updates(self):
        # Graph: 4 nodes in a straight line.
        n = 4
        edges = [(0, 1, 1), (1, 2, 1), (2, 3, 1)]
        group = [0, 3]
        updates = [(1, 2, 10), (2, 3, 5)]
        # After update1:
        #   Edges become: (0,1)=1, (1,2)=10, (2,3)=1.
        #   Distances from 0: [0, 1, 11, 12]
        #   Distances from 3: [12, 11, 1, 0]
        #   Optimal meeting: For candidate nodes:
        #       0 -> max(0,12)=12, 
        #       1 -> max(1,11)=11, 
        #       2 -> max(11,1)=11, 
        #       3 -> max(12,0)=12. => choose 1 (smallest index among tied).
        # After update2:
        #   Edges become: (0,1)=1, (1,2)=10, (2,3)=5.
        #   Distances from 0: [0, 1, 11, 16]
        #   Distances from 3: [16, 15, 5, 0]
        #   Candidate 0: max(0,16)=16, 
        #   Candidate 1: max(1,15)=15, 
        #   Candidate 2: max(11,5)=11, 
        #   Candidate 3: max(16,0)=16. => choose candidate 2.
        expected = [1, 2]
        result = optimal_meeting_point(n, edges, group, updates)
        self.assertEqual(result, expected)

    def test_case_disconnected(self):
        # Graph: 4 nodes, but the update disconnects part of the graph.
        n = 4
        edges = [(0, 1, 2), (1, 2, 2), (2, 3, 2)]
        group = [0, 3]
        updates = [(1, 2, 0)]  # Road between 1 and 2 closed.
        # With the road closed, there is no path between some nodes.
        # Therefore, no candidate meeting point is reachable from both group members.
        expected = [-1]
        result = optimal_meeting_point(n, edges, group, updates)
        self.assertEqual(result, expected)

    def test_case_complete_graph(self):
        # Graph: 3 nodes fully connected.
        n = 3
        edges = [(0, 1, 3), (1, 2, 4), (0, 2, 10)]
        group = [0, 2]
        updates = [(0, 2, 2), (1, 2, 1)]
        # After update1:
        #   Edges become: (0,1)=3, (1,2)=4, (0,2)=2.
        #   Distances from 0: [0,3,2]
        #   Distances from 2: [2,4,0]
        #   Candidate 0: max(0,2)=2, candidate 1: max(3,4)=4, candidate 2: max(2,0)=2.
        #   Tie between node 0 and node 2 => choose 0.
        # After update2:
        #   Edges become: (0,1)=3, (1,2)=1, (0,2)=2.
        #   Distances from 0: [0,3,2]
        #   Distances from 2: [2,1,0]
        #   Candidate 0: max(0,2)=2, candidate 1: max(3,1)=3, candidate 2: max(2,0)=2.
        #   Optimal is node 0 again.
        expected = [0, 0]
        result = optimal_meeting_point(n, edges, group, updates)
        self.assertEqual(result, expected)

    def test_case_complex_graph(self):
        # Graph: 6 nodes with multiple connections.
        n = 6
        edges = [
            (0, 1, 2),
            (0, 2, 4),
            (1, 2, 1),
            (1, 3, 7),
            (2, 4, 3),
            (3, 4, 2),
            (3, 5, 5),
            (4, 5, 1)
        ]
        group = [0, 3, 5]
        updates = [(1, 3, 10), (3, 5, 3)]
        # After update1:
        #   Updated edge: (1,3)=10.
        #   Based on manual computation, the optimal meeting point is node 2.
        # After update2:
        #   Updated edge: (3,5)=3.
        #   The optimal meeting point remains node 2.
        expected = [2, 2]
        result = optimal_meeting_point(n, edges, group, updates)
        self.assertEqual(result, expected)

    def test_case_no_updates(self):
        # If there are no updates, the function should return an empty list.
        n = 5
        edges = [(0, 1, 3), (1, 2, 5), (2, 3, 2), (3, 4, 4)]
        group = [0, 4]
        updates = []
        expected = []
        result = optimal_meeting_point(n, edges, group, updates)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()