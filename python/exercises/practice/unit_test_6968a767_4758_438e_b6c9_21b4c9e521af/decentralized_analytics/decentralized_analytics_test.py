import unittest
from decentralized_analytics import analyze_network

class TestDecentralizedAnalytics(unittest.TestCase):
    def test_single_shard_reachability_and_influencer(self):
        # Single shard with a simple chain A -> B -> C.
        shards = [{
            "shard_id": 1,
            "users": {"A", "B", "C"},
            "connections": [("A", "B"), ("B", "C")]
        }]
        queries = [
            {
                "type": "reachability",
                "user_a": "A",
                "user_b": "C",
                "max_hops": 2
            },
            {
                "type": "reachability",
                "user_a": "A",
                "user_b": "C",
                "max_hops": 1
            },
            {
                "type": "influencer_score",
                "user": "A",
                "hop_limit": 2
            }
        ]
        expected = [True, False, 2]
        result = analyze_network(shards, queries)
        self.assertEqual(result, expected)
        
    def test_non_existent_user(self):
        # Test when one of the users does not exist.
        shards = [{
            "shard_id": 1,
            "users": {"A", "B", "C"},
            "connections": [("A", "B"), ("B", "C")]
        }]
        queries = [
            {
                "type": "reachability",
                "user_a": "X",
                "user_b": "C",
                "max_hops": 3
            },
            {
                "type": "influencer_score",
                "user": "Y",
                "hop_limit": 2
            }
        ]
        # If a user does not exist, reachability should return False and influencer_score should be 0.
        expected = [False, 0]
        result = analyze_network(shards, queries)
        self.assertEqual(result, expected)
        
    def test_multiple_shards_cross_connection(self):
        # Two shards simulate cross shard connectivity.
        # Shard1 contains A and B with connection A -> B.
        # Shard2 contains B and C with connection B -> C.
        shards = [
            {
                "shard_id": 1,
                "users": {"A", "B"},
                "connections": [("A", "B")]
            },
            {
                "shard_id": 2,
                "users": {"B", "C"},
                "connections": [("B", "C")]
            }
        ]
        queries = [
            {
                "type": "reachability",
                "user_a": "A",
                "user_b": "C",
                "max_hops": 2
            },
            {
                "type": "influencer_score",
                "user": "B",
                "hop_limit": 1
            }
        ]
        expected = [True, 1]
        result = analyze_network(shards, queries)
        self.assertEqual(result, expected)
    
    def test_complex_graph_with_cycle(self):
        # Single shard graph with cycle and branch:
        # A -> B, B -> C, C -> A (cycle), and C -> D.
        shards = [{
            "shard_id": 1,
            "users": {"A", "B", "C", "D"},
            "connections": [("A", "B"), ("B", "C"), ("C", "A"), ("C", "D")]
        }]
        queries = [
            {
                "type": "influencer_score",
                "user": "A",
                "hop_limit": 3
            },
            {
                "type": "reachability",
                "user_a": "D",
                "user_b": "A",
                "max_hops": 3
            }
        ]
        # From A: within 3 hops reachable nodes are B (hop1), C (hop2) and D (via A->B->C->D, hop3) => score=3.
        # D has no outgoing connections so reachability from D to A is False.
        expected = [3, False]
        result = analyze_network(shards, queries)
        self.assertEqual(result, expected)

    def test_large_hop_limits(self):
        # Graph with isolated chain where hop limits exceed chain length.
        shards = [{
            "shard_id": 1,
            "users": {"A", "B", "C", "D"},
            "connections": [("A", "B"), ("B", "C"), ("C", "D")]
        }]
        queries = [
            {
                "type": "reachability",
                "user_a": "A",
                "user_b": "D",
                "max_hops": 10
            },
            {
                "type": "influencer_score",
                "user": "A",
                "hop_limit": 10
            }
        ]
        # A reaches D in 3 hops, and influencer score for A is 3 (B, C, D).
        expected = [True, 3]
        result = analyze_network(shards, queries)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()