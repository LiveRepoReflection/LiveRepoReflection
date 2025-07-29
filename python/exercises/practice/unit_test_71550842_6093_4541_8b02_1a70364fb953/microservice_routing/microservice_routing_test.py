import unittest
from microservice_routing import min_router_capacity

class MicroserviceRoutingTest(unittest.TestCase):

    def test_single_service(self):
        # Only one microservice. No routers required.
        N = 1
        k = 2  # k can be arbitrary because there is no internal node.
        T = [[0]]
        expected = 0
        self.assertEqual(min_router_capacity(N, k, T), expected)

    def test_no_messages(self):
        # Multiple services but no messages sent.
        N = 4
        k = 2
        T = [
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ]
        expected = 0
        self.assertEqual(min_router_capacity(N, k, T), expected)
    
    def test_binary_tree_sample(self):
        # Provided sample with a complete binary tree (N = 4, k = 2)
        N = 4
        k = 2
        T = [
            [0, 5, 2, 1],
            [8, 0, 3, 7],
            [4, 6, 0, 2],
            [5, 1, 9, 0]
        ]
        # Calculation:
        # Left router (covering leaves 0 and 1) gets:
        #   Intra-group: T[0][1] + T[1][0] = 5 + 8 = 13
        #   Left->Right: sum_{i in {0,1}, j in {2,3]} = (2+1) + (3+7) = 13
        #   Right->Left: sum_{i in {2,3}, j in {0,1]} = (4+6) + (5+1) = 16
        # Total load on left router = 13 + 13 + 16 = 42
        # Right router (covering leaves 2 and 3) gets:
        #   Intra-group: T[2][3] + T[3][2] = 2 + 9 = 11
        #   Left->Right and Right->Left also contribute 13 and 16 respectively.
        # Total load on right router = 13 + 16 + 11 = 40
        # Root router gets:
        #   Only messages crossing between left and right subtrees:
        #   Load = 13 (left->right) + 16 (right->left) = 29
        # Max load among internal routers = 42
        expected = 42
        self.assertEqual(min_router_capacity(N, k, T), expected)

    def test_uniform_messages_binary(self):
        # Test with a uniform traffic matrix on a complete binary tree (N = 4, k = 2)
        N = 4
        k = 2
        # All off-diagonal entries are 1
        T = []
        for i in range(N):
            row = []
            for j in range(N):
                row.append(0 if i == j else 1)
            T.append(row)
        # Analysis:
        # For left router covering leaves 0 and 1:
        #   Intra-group: T[0][1] + T[1][0] = 1 + 1 = 2
        #   Left->Right: For leaves 0,1 to leaves 2,3 = 1*4 = 4
        #   Right->Left: Similarly, 4
        # Total load = 2 + 4 + 4 = 10
        # For right router, similar load = 10. Root gets 4 + 4 = 8.
        # Maximum capacity = 10.
        expected = 10
        self.assertEqual(min_router_capacity(N, k, T), expected)

    def test_ternary_tree(self):
        # Test with a complete ternary tree (N = 9, k = 3).
        N = 9
        k = 3
        # Create a traffic matrix with most entries 0 and some selected non-zero messages.
        T = [[0 for _ in range(N)] for _ in range(N)]
        # Define messages:
        # Message from leaf 0 to leaf 4 with weight 10.
        T[0][4] = 10
        # Message from leaf 4 to leaf 7 with weight 20.
        T[4][7] = 20
        # Message from leaf 7 to leaf 0 with weight 5.
        T[7][0] = 5
        # In the ternary tree with 9 leaves arranged as:
        #   Child 1 covers leaves 0,1,2
        #   Child 2 covers leaves 3,4,5
        #   Child 3 covers leaves 6,7,8
        #
        # For message from 0 to 4:
        #   Path: 0 -> A (child1) -> Root -> B (child2) -> 4.
        #   Loads: A += 10, Root += 10, B += 10.
        # For message from 4 to 7:
        #   Path: 4 -> B (child2) -> Root -> C (child3) -> 7.
        #   Loads: B += 20, Root += 20, C += 20.
        # For message from 7 to 0:
        #   Path: 7 -> C (child3) -> Root -> A (child1) -> 0.
        #   Loads: C += 5, Root += 5, A += 5.
        # Total loads:
        #   A: 10 + 5 = 15, B: 10 + 20 = 30, C: 20 + 5 = 25, Root: 10 + 20 + 5 = 35.
        # Maximum load = 35.
        expected = 35
        self.assertEqual(min_router_capacity(N, k, T), expected)

if __name__ == '__main__':
    unittest.main()