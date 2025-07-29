import unittest

from social_analyzer import SocialNetworkAnalyzer

class TestSocialAnalyzer(unittest.TestCase):
    def setUp(self):
        # Initialize the social network analyzer with a sample graph
        self.analyzer = SocialNetworkAnalyzer()
        # Add users A, B, C, D, E
        for user in ['A', 'B', 'C', 'D', 'E']:
            self.analyzer.add_user(user)
        # Create connections:
        # A follows B and C
        self.analyzer.add_connection('A', 'B')
        self.analyzer.add_connection('A', 'C')
        # B follows C and D
        self.analyzer.add_connection('B', 'C')
        self.analyzer.add_connection('B', 'D')
        # C follows D
        self.analyzer.add_connection('C', 'D')
        # D follows E
        self.analyzer.add_connection('D', 'E')
        # E follows A to form a cycle
        self.analyzer.add_connection('E', 'A')
    
    def test_influence_score_convergence(self):
        # Test that influence scores are computed correctly and converge.
        threshold = 1e-5
        scores = self.analyzer.calculate_influence_scores(threshold=threshold)
        self.assertIsInstance(scores, dict)
        # Check that every user has an influence score and that scores are positive.
        for user in ['A', 'B', 'C', 'D', 'E']:
            self.assertIn(user, scores)
            self.assertGreater(scores[user], 0)
    
    def test_community_detection(self):
        # Test community detection using the Louvain algorithm.
        communities = self.analyzer.detect_communities()
        self.assertIsInstance(communities, dict)
        # Ensure all existing users are assigned to a community.
        for user in ['A', 'B', 'C', 'D', 'E']:
            self.assertIn(user, communities)
        # Verify that there is at least one community.
        self.assertGreaterEqual(len(set(communities.values())), 1)
    
    def test_shortest_path_recommendation(self):
        # Test finding the shortest path between two connected users.
        path = self.analyzer.find_shortest_path('A', 'E')
        self.assertIsInstance(path, list)
        self.assertEqual(path[0], 'A')
        self.assertEqual(path[-1], 'E')
        # Given the graph, the shortest path should have 4 or 5 nodes (depending on tie resolution).
        self.assertLessEqual(len(path), 5)
    
    def test_shortest_path_no_route(self):
        # Add an isolated user to test path not found.
        self.analyzer.add_user('F')
        path = self.analyzer.find_shortest_path('A', 'F')
        self.assertIsNone(path)
    
    def test_dynamic_updates_add_remove_user(self):
        # Test dynamic updates by adding a new user and then removing it.
        self.analyzer.add_user('G')
        self.analyzer.add_connection('G', 'A')
        scores = self.analyzer.calculate_influence_scores()
        self.assertIn('G', scores)
        self.analyzer.remove_user('G')
        updated_scores = self.analyzer.calculate_influence_scores()
        self.assertNotIn('G', updated_scores)
    
    def test_dynamic_updates_add_remove_connection(self):
        # Test dynamic update for connections.
        # Initially, there is a connection from B to D.
        path_initial = self.analyzer.find_shortest_path('A', 'D')
        self.assertIsNotNone(path_initial)
        
        # Remove connection B -> D and check if an alternate path exists.
        self.analyzer.remove_connection('B', 'D')
        path_after_removal = self.analyzer.find_shortest_path('A', 'D')
        self.assertIsNotNone(path_after_removal)
        
        # Restore connection and check the path again.
        self.analyzer.add_connection('B', 'D')
        path_restored = self.analyzer.find_shortest_path('A', 'D')
        self.assertIsNotNone(path_restored)
    
    def test_error_handling_non_existent_user(self):
        # Test that attempting operations with non-existent users raises an error.
        with self.assertRaises(KeyError):
            self.analyzer.add_connection('X', 'Y')
        with self.assertRaises(KeyError):
            self.analyzer.remove_connection('X', 'Y')
        with self.assertRaises(KeyError):
            self.analyzer.find_shortest_path('X', 'A')

if __name__ == '__main__':
    unittest.main()