import unittest
from influencer_path import find_optimal_influencer_path


class InfluencerPathTest(unittest.TestCase):
    def test_basic_example(self):
        graph = {1: [2, 3], 2: [4], 3: [4, 5]}
        user_attributes = {
            1: {'age': 25, 'influence_score': 0.8},
            2: {'age': 30, 'influence_score': 0.9},
            3: {'age': 27, 'influence_score': 0.75},
            4: {'age': 29, 'influence_score': 0.88},
            5: {'age': 31, 'influence_score': 0.92}
        }
        user_reach = {1: 1000, 2: 2000, 3: 1500, 4: 3000, 5: 2500}
        target_audience_profile = {'age': 28, 'influence_score': 0.85}
        max_attribute_values = {'age': 100, 'influence_score': 1.0}
        seed_user_id = 1
        K = 3
        Lambda = 0.5
        
        result = find_optimal_influencer_path(graph, user_attributes, user_reach, 
                                            target_audience_profile, max_attribute_values, 
                                            seed_user_id, K, Lambda)
        
        # Check that result is a list
        self.assertIsInstance(result, list)
        
        # Check that the path starts with seed_user_id
        self.assertTrue(len(result) == 0 or result[0] == seed_user_id)
        
        # Check that the path length is at most K
        self.assertLessEqual(len(result), K)
        
        # Check that the path is valid in the graph
        if len(result) > 1:
            for i in range(len(result) - 1):
                self.assertIn(result[i+1], graph.get(result[i], []), 
                              f"Invalid edge in path: {result[i]} -> {result[i+1]}")
    
    def test_empty_graph(self):
        graph = {}
        user_attributes = {}
        user_reach = {}
        target_audience_profile = {'age': 28, 'influence_score': 0.85}
        max_attribute_values = {'age': 100, 'influence_score': 1.0}
        seed_user_id = 1
        K = 3
        Lambda = 0.5
        
        result = find_optimal_influencer_path(graph, user_attributes, user_reach, 
                                            target_audience_profile, max_attribute_values, 
                                            seed_user_id, K, Lambda)
        
        # Empty graph should return empty path or just the seed if it exists
        self.assertTrue(len(result) == 0 or (len(result) == 1 and result[0] == seed_user_id))
    
    def test_disconnected_graph(self):
        graph = {1: [], 2: [3], 3: []}
        user_attributes = {
            1: {'age': 25, 'influence_score': 0.8},
            2: {'age': 30, 'influence_score': 0.9},
            3: {'age': 27, 'influence_score': 0.75}
        }
        user_reach = {1: 1000, 2: 2000, 3: 1500}
        target_audience_profile = {'age': 28, 'influence_score': 0.85}
        max_attribute_values = {'age': 100, 'influence_score': 1.0}
        seed_user_id = 1
        K = 3
        Lambda = 0.5
        
        result = find_optimal_influencer_path(graph, user_attributes, user_reach, 
                                            target_audience_profile, max_attribute_values, 
                                            seed_user_id, K, Lambda)
        
        # Should only contain the seed user as there are no outgoing edges
        self.assertEqual(result, [1])
    
    def test_missing_attributes(self):
        graph = {1: [2, 3], 2: [4], 3: [4, 5]}
        user_attributes = {
            1: {'age': 25},  # Missing influence_score
            2: {'influence_score': 0.9},  # Missing age
            3: {'age': 27, 'influence_score': 0.75},
            4: {'age': 29, 'influence_score': 0.88},
            5: {'age': 31, 'influence_score': 0.92}
        }
        user_reach = {1: 1000, 2: 2000, 3: 1500, 4: 3000, 5: 2500}
        target_audience_profile = {'age': 28, 'influence_score': 0.85}
        max_attribute_values = {'age': 100, 'influence_score': 1.0}
        seed_user_id = 1
        K = 3
        Lambda = 0.5
        
        result = find_optimal_influencer_path(graph, user_attributes, user_reach, 
                                            target_audience_profile, max_attribute_values, 
                                            seed_user_id, K, Lambda)
        
        # Check that result is still valid
        self.assertIsInstance(result, list)
        if len(result) > 0:
            self.assertEqual(result[0], seed_user_id)
        
        if len(result) > 1:
            for i in range(len(result) - 1):
                self.assertIn(result[i+1], graph.get(result[i], []))
    
    def test_single_user(self):
        graph = {1: []}
        user_attributes = {1: {'age': 25, 'influence_score': 0.8}}
        user_reach = {1: 1000}
        target_audience_profile = {'age': 28, 'influence_score': 0.85}
        max_attribute_values = {'age': 100, 'influence_score': 1.0}
        seed_user_id = 1
        K = 3
        Lambda = 0.5
        
        result = find_optimal_influencer_path(graph, user_attributes, user_reach, 
                                            target_audience_profile, max_attribute_values, 
                                            seed_user_id, K, Lambda)
        
        # Should only contain the seed user
        self.assertEqual(result, [1])
    
    def test_larger_graph(self):
        # Create a larger graph
        graph = {}
        user_attributes = {}
        user_reach = {}
        
        # Generate a larger test case
        for i in range(1, 101):  # 100 users
            graph[i] = [(i + j) % 100 + 1 for j in range(1, 6)]  # Each user follows 5 others
            user_attributes[i] = {'age': 20 + (i % 30), 'influence_score': 0.5 + (i % 10) / 20}
            user_reach[i] = i * 100
        
        target_audience_profile = {'age': 28, 'influence_score': 0.85}
        max_attribute_values = {'age': 100, 'influence_score': 1.0}
        seed_user_id = 1
        K = 5
        Lambda = 0.5
        
        result = find_optimal_influencer_path(graph, user_attributes, user_reach, 
                                            target_audience_profile, max_attribute_values, 
                                            seed_user_id, K, Lambda)
        
        # Check that result is a valid path
        self.assertIsInstance(result, list)
        self.assertLessEqual(len(result), K)
        
        if len(result) > 0:
            self.assertEqual(result[0], seed_user_id)
        
        if len(result) > 1:
            for i in range(len(result) - 1):
                self.assertIn(result[i+1], graph.get(result[i], []))
    
    def test_varying_k_values(self):
        graph = {1: [2, 3], 2: [4], 3: [4, 5], 4: [6], 5: [6], 6: []}
        user_attributes = {
            1: {'age': 25, 'influence_score': 0.8},
            2: {'age': 30, 'influence_score': 0.9},
            3: {'age': 27, 'influence_score': 0.75},
            4: {'age': 29, 'influence_score': 0.88},
            5: {'age': 31, 'influence_score': 0.92},
            6: {'age': 28, 'influence_score': 0.85}
        }
        user_reach = {1: 1000, 2: 2000, 3: 1500, 4: 3000, 5: 2500, 6: 4000}
        target_audience_profile = {'age': 28, 'influence_score': 0.85}
        max_attribute_values = {'age': 100, 'influence_score': 1.0}
        seed_user_id = 1
        Lambda = 0.5
        
        # Test with different K values
        for K in range(1, 5):
            result = find_optimal_influencer_path(graph, user_attributes, user_reach, 
                                                target_audience_profile, max_attribute_values, 
                                                seed_user_id, K, Lambda)
            
            # Path should not exceed K
            self.assertLessEqual(len(result), K)
            
            if len(result) > 0:
                self.assertEqual(result[0], seed_user_id)
            
            if len(result) > 1:
                for i in range(len(result) - 1):
                    self.assertIn(result[i+1], graph.get(result[i], []))
    
    def test_invalid_seed(self):
        graph = {1: [2, 3], 2: [4], 3: [4, 5]}
        user_attributes = {
            1: {'age': 25, 'influence_score': 0.8},
            2: {'age': 30, 'influence_score': 0.9},
            3: {'age': 27, 'influence_score': 0.75},
            4: {'age': 29, 'influence_score': 0.88},
            5: {'age': 31, 'influence_score': 0.92}
        }
        user_reach = {1: 1000, 2: 2000, 3: 1500, 4: 3000, 5: 2500}
        target_audience_profile = {'age': 28, 'influence_score': 0.85}
        max_attribute_values = {'age': 100, 'influence_score': 1.0}
        seed_user_id = 999  # Invalid seed
        K = 3
        Lambda = 0.5
        
        result = find_optimal_influencer_path(graph, user_attributes, user_reach, 
                                            target_audience_profile, max_attribute_values, 
                                            seed_user_id, K, Lambda)
        
        # Should return empty list for invalid seed
        self.assertEqual(result, [])
    
    def test_complex_attributes(self):
        graph = {1: [2, 3], 2: [4], 3: [4, 5]}
        user_attributes = {
            1: {'age': 25, 'influence_score': 0.8, 'location': 10, 'expertise': 5},
            2: {'age': 30, 'influence_score': 0.9, 'location': 15, 'expertise': 8},
            3: {'age': 27, 'influence_score': 0.75, 'location': 12, 'expertise': 6},
            4: {'age': 29, 'influence_score': 0.88, 'location': 8, 'expertise': 9},
            5: {'age': 31, 'influence_score': 0.92, 'location': 20, 'expertise': 7}
        }
        user_reach = {1: 1000, 2: 2000, 3: 1500, 4: 3000, 5: 2500}
        target_audience_profile = {
            'age': 28, 'influence_score': 0.85, 'location': 10, 'expertise': 7
        }
        max_attribute_values = {
            'age': 100, 'influence_score': 1.0, 'location': 100, 'expertise': 10
        }
        seed_user_id = 1
        K = 3
        Lambda = 0.5
        
        result = find_optimal_influencer_path(graph, user_attributes, user_reach, 
                                            target_audience_profile, max_attribute_values, 
                                            seed_user_id, K, Lambda)
        
        # Check that result is valid
        self.assertIsInstance(result, list)
        self.assertLessEqual(len(result), K)
        
        if len(result) > 0:
            self.assertEqual(result[0], seed_user_id)
        
        if len(result) > 1:
            for i in range(len(result) - 1):
                self.assertIn(result[i+1], graph.get(result[i], []))
    
    def test_cyclic_graph(self):
        # Graph with cycles
        graph = {1: [2], 2: [3], 3: [4], 4: [2, 5], 5: []}
        user_attributes = {
            1: {'age': 25, 'influence_score': 0.8},
            2: {'age': 30, 'influence_score': 0.9},
            3: {'age': 27, 'influence_score': 0.75},
            4: {'age': 29, 'influence_score': 0.88},
            5: {'age': 31, 'influence_score': 0.92}
        }
        user_reach = {1: 1000, 2: 2000, 3: 1500, 4: 3000, 5: 2500}
        target_audience_profile = {'age': 28, 'influence_score': 0.85}
        max_attribute_values = {'age': 100, 'influence_score': 1.0}
        seed_user_id = 1
        K = 6
        Lambda = 0.5
        
        result = find_optimal_influencer_path(graph, user_attributes, user_reach, 
                                            target_audience_profile, max_attribute_values, 
                                            seed_user_id, K, Lambda)
        
        # Check that result is valid and doesn't have duplicates (since we want a path, not a cycle)
        self.assertIsInstance(result, list)
        self.assertLessEqual(len(result), K)
        self.assertEqual(len(result), len(set(result)), "Path should not contain duplicate users")
        
        if len(result) > 0:
            self.assertEqual(result[0], seed_user_id)
        
        if len(result) > 1:
            for i in range(len(result) - 1):
                self.assertIn(result[i+1], graph.get(result[i], []))


if __name__ == "__main__":
    unittest.main()