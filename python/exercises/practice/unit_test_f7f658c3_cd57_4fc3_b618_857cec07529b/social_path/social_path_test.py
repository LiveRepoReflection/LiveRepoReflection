import unittest

# Global variable to simulate the network mapping from user_id to its corresponding node.
user_to_node = {}

def fake_get_node(user_id):
    return user_to_node.get(user_id, None)

class FakeNode:
    def __init__(self, users):
        # users is a dictionary mapping user_id to list of friend user_ids.
        self.users = users

    def get_friends(self, user_id):
        if user_id in self.users:
            return self.users[user_id]
        return []

# Import the function to be tested from the social_path module.
# We assume that the solution defines a function called find_path(start_user_id, target_user_id)
# that uses the get_node() function in its implementation.
from social_path import find_path

# Patch the module's get_node reference to use our fake_get_node for testing.
# This ensures that when find_path queries for a node, it gets our simulated result.
find_path.__globals__['get_node'] = fake_get_node

class SocialPathTest(unittest.TestCase):

    def setUp(self):
        global user_to_node
        user_to_node.clear()

    def test_valid_path(self):
        # Setup network:
        # Node1: owns {1, 2, 3}
        # Node2: owns {4, 5, 6}
        # Connections:
        # Node1: 1 -> [2, 3], 2 -> [1, 4], 3 -> [1]
        # Node2: 4 -> [2, 5], 5 -> [4, 6], 6 -> [5]
        node1_users = {
            1: [2, 3],
            2: [1, 4],
            3: [1]
        }
        node2_users = {
            4: [2, 5],
            5: [4, 6],
            6: [5]
        }
        node1 = FakeNode(node1_users)
        node2 = FakeNode(node2_users)
        # Map user id to corresponding FakeNode.
        user_to_node[1] = node1
        user_to_node[2] = node1
        user_to_node[3] = node1
        user_to_node[4] = node2
        user_to_node[5] = node2
        user_to_node[6] = node2

        # Expected shortest path from 1 to 6 is [1, 2, 4, 5, 6]
        result = find_path(1, 6)
        self.assertIsNotNone(result, "Expected a valid path but got None.")
        self.assertEqual(result[0], 1, "Path should start with the start user.")
        self.assertEqual(result[-1], 6, "Path should end with the target user.")
        # Verify that consecutive nodes in the path are connected.
        for i in range(len(result) - 1):
            node = fake_get_node(result[i])
            friends = node.get_friends(result[i])
            self.assertIn(result[i+1], friends, f"User {result[i]} should be connected to {result[i+1]}.")

    def test_no_path(self):
        # Setup network with two disconnected components:
        # Component 1: Node1 owns {1, 2} with connections 1 -> [2], 2 -> [1]
        # Component 2: Node2 owns {3, 4} with connections 3 -> [4], 4 -> [3]
        node1_users = {
            1: [2],
            2: [1]
        }
        node2_users = {
            3: [4],
            4: [3]
        }
        node1 = FakeNode(node1_users)
        node2 = FakeNode(node2_users)
        user_to_node[1] = node1
        user_to_node[2] = node1
        user_to_node[3] = node2
        user_to_node[4] = node2

        # There is no path between user 1 and user 3.
        result = find_path(1, 3)
        self.assertIsNone(result, "Expected None as there is no path between disconnected components.")

    def test_nonexistent_user(self):
        # Setup network where only user 1 exists.
        node_users = {
            1: [2],
            2: [1, 3],
            3: [2]
        }
        node = FakeNode(node_users)
        user_to_node[1] = node
        user_to_node[2] = node
        user_to_node[3] = node

        # Start user exists but target does not.
        result = find_path(1, 99)
        self.assertIsNone(result, "Expected None when target user does not exist.")

        # Target user exists but start does not.
        result = find_path(99, 1)
        self.assertIsNone(result, "Expected None when start user does not exist.")

    def test_cycle_handling(self):
        # Setup a graph with cycles:
        # Single node owns {1, 2, 3, 4} with cyclic connections:
        # 1 -> [2]
        # 2 -> [3, 1]
        # 3 -> [2, 4]
        # 4 -> [3]
        node_users = {
            1: [2],
            2: [3, 1],
            3: [2, 4],
            4: [3]
        }
        node = FakeNode(node_users)
        user_to_node[1] = node
        user_to_node[2] = node
        user_to_node[3] = node
        user_to_node[4] = node

        # Expected shortest path from 1 to 4 is [1, 2, 3, 4]
        result = find_path(1, 4)
        self.assertIsNotNone(result, "Expected a valid path in a cyclic graph but got None.")
        self.assertEqual(result[0], 1, "Path should start with the start user.")
        self.assertEqual(result[-1], 4, "Path should end with the target user.")
        # Verify that consecutive nodes in the path are connected.
        for i in range(len(result) - 1):
            node_inst = fake_get_node(result[i])
            friends = node_inst.get_friends(result[i])
            self.assertIn(result[i+1], friends, f"User {result[i]} should be connected to {result[i+1]}.")

    def test_multiple_shortest_paths(self):
        # Setup network where multiple shortest paths exist.
        # Node owns all users {1, 2, 3, 4}
        # 1 -> [2, 3]
        # 2 -> [4]
        # 3 -> [4]
        # 4 -> []
        node_users = {
            1: [2, 3],
            2: [4],
            3: [4],
            4: []
        }
        node = FakeNode(node_users)
        user_to_node[1] = node
        user_to_node[2] = node
        user_to_node[3] = node
        user_to_node[4] = node

        result = find_path(1, 4)
        self.assertIsNotNone(result, "Expected a valid path when multiple shortest paths exist.")
        self.assertEqual(result[0], 1, "Path should start with the start user.")
        self.assertEqual(result[-1], 4, "Path should end with the target user.")
        # The shortest path length should be 3.
        self.assertEqual(len(result), 3, "Shortest path length should be 3.")
        # Verify connectivity.
        for i in range(len(result) - 1):
            node_inst = fake_get_node(result[i])
            friends = node_inst.get_friends(result[i])
            self.assertIn(result[i+1], friends, f"User {result[i]} should be connected to {result[i+1]}.")

if __name__ == '__main__':
    unittest.main()