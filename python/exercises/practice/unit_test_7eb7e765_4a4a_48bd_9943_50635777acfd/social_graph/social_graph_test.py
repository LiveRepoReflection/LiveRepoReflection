import unittest
from social_graph import SocialGraph

class TestSocialGraph(unittest.TestCase):
    def setUp(self):
        self.graph = SocialGraph()
        # Setup test users
        self.users = [1, 2, 3, 4, 5, 6, 7, 8]
        for user in self.users:
            self.graph.add_user(user)
        # Setup connections
        self.connections = [(1, 2), (2, 3), (3, 4), (4, 1), (5, 6), (6, 7), (7, 5), (8, 8)]
        for u, v in self.connections:
            self.graph.add_connection(u, v)

    def test_add_remove_users(self):
        self.graph.add_user(9)
        self.assertIn(9, self.graph.get_users())
        self.graph.remove_user(9)
        self.assertNotIn(9, self.graph.get_users())

    def test_add_remove_connections(self):
        self.graph.add_connection(1, 5)
        self.assertIn(5, self.graph.get_friends(1))
        self.graph.remove_connection(1, 5)
        self.assertNotIn(5, self.graph.get_friends(1))

    def test_get_friends(self):
        self.assertEqual(set(self.graph.get_friends(1)), {2, 4})
        self.assertEqual(set(self.graph.get_friends(8)), {8})

    def test_degree_of_separation(self):
        self.assertEqual(self.graph.degree_of_separation(1, 3), 2)
        self.assertEqual(self.graph.degree_of_separation(1, 5), -1)
        self.assertEqual(self.graph.degree_of_separation(8, 8), 0)

    def test_strongly_connected_components(self):
        sccs = self.graph.get_strongly_connected_components()
        expected_sccs = [{1, 2, 3, 4}, {5, 6, 7}, {8}]
        self.assertEqual(len(sccs), len(expected_sccs))
        for scc in sccs:
            self.assertIn(set(scc), expected_sccs)

    def test_betweenness_centrality(self):
        centrality = self.graph.calculate_betweenness_centrality(2)
        self.assertGreater(centrality, 0)
        self.assertLessEqual(centrality, 1)

    def test_concurrent_operations(self):
        import threading
        def add_users():
            for i in range(10, 15):
                self.graph.add_user(i)
        def add_connections():
            for i in range(10, 14):
                self.graph.add_connection(i, i+1)
        t1 = threading.Thread(target=add_users)
        t2 = threading.Thread(target=add_connections)
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        self.assertEqual(len(self.graph.get_users()), len(self.users) + 5)
        self.assertEqual(len(self.graph.get_friends(11)), 2)

    def test_network_partition(self):
        partition = self.graph.create_network_partition([1, 2, 3, 4])
        self.assertEqual(set(partition.get_users()), {1, 2, 3, 4})
        self.assertEqual(set(partition.get_friends(1)), {2, 4})

    def test_remove_user_cascading(self):
        self.graph.remove_user(2)
        self.assertNotIn(2, self.graph.get_users())
        self.assertNotIn(2, self.graph.get_friends(1))
        self.assertNotIn(2, self.graph.get_friends(3))

if __name__ == '__main__':
    unittest.main()