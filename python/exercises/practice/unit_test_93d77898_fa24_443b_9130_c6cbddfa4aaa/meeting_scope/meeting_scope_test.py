import unittest
from meeting_scope import Node, find_meeting_scope

class MeetingScopeTest(unittest.TestCase):
    def setUp(self):
        # Constructing a sample corporate hierarchy tree:
        #         1 (CEO)
        #        /      \
        #      2         3
        #     / \       /  \
        #    4   5     6    7
        #       /     /|\    
        #      8     9 10 11  
        #
        # Each node: Node(employee_id, department, children)
        
        # Leaf nodes
        self.node8 = Node(8, "Sales", [])
        self.node9 = Node(9, "HR", [])
        self.node10 = Node(10, "HR", [])
        self.node11 = Node(11, "Engineering", [])
        self.node4 = Node(4, "Engineering", [])
        
        # Intermediate nodes
        self.node5 = Node(5, "Sales", [self.node8])
        self.node6 = Node(6, "HR", [self.node9, self.node10, self.node11])
        self.node7 = Node(7, "Engineering", [])
        
        # More intermediate nodes
        self.node2 = Node(2, "Sales", [self.node4, self.node5])
        self.node3 = Node(3, "Engineering", [self.node6, self.node7])
        
        # Root node
        self.root = Node(1, "Executive", [self.node2, self.node3])

    def test_single_attendee(self):
        # When the attendee is a leaf node
        result = find_meeting_scope(self.root, [8])
        self.assertIsNotNone(result)
        self.assertEqual(result.employee_id, 8)
        
        # When the attendee is an internal node
        result = find_meeting_scope(self.root, [3])
        self.assertIsNotNone(result)
        self.assertEqual(result.employee_id, 3)

    def test_small_subtree(self):
        # Attendees are within the same immediate subtree of node2: [4, 8]
        # Expected smallest subtree is rooted at node2.
        result = find_meeting_scope(self.root, [4, 8])
        self.assertIsNotNone(result)
        self.assertEqual(result.employee_id, 2)

    def test_subtree_across_branches(self):
        # Attendees located in different branches:
        # For instance, attendee 8 (under node5) and attendee 11 (under node6)
        # The expected smallest subtree that includes both should be the entire tree root node (1).
        result = find_meeting_scope(self.root, [8, 11])
        self.assertIsNotNone(result)
        self.assertEqual(result.employee_id, 1)

    def test_multiple_attendees_in_one_subbranch(self):
        # Attendees all under node6: [9, 10, 11]
        # Expected smallest subtree is node6.
        result = find_meeting_scope(self.root, [9, 11, 10])
        self.assertIsNotNone(result)
        self.assertEqual(result.employee_id, 6)

    def test_all_attendees(self):
        # All nodes are attendees, so the smallest subtree is the whole tree
        attendee_ids = [1,2,3,4,5,6,7,8,9,10,11]
        result = find_meeting_scope(self.root, attendee_ids)
        self.assertIsNotNone(result)
        self.assertEqual(result.employee_id, 1)
        
    def test_empty_attendees(self):
        # When no attendees are provided, expected behavior can be to return None
        result = find_meeting_scope(self.root, [])
        self.assertIsNone(result)
        
    def test_attendees_with_overlapping_subtrees(self):
        # Attendees: 4 (under node2), 5 (under node2), and 7 (under node3).
        # The minimal subtree that includes both branches is the root (1).
        result = find_meeting_scope(self.root, [4, 5, 7])
        self.assertIsNotNone(result)
        self.assertEqual(result.employee_id, 1)

if __name__ == '__main__':
    unittest.main()