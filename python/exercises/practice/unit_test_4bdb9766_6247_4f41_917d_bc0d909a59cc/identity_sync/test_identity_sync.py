import unittest
from unittest.mock import patch
import time

# Import the function under test from identity_sync module.
from identity_sync import sync_identity

# Attempt to import RateLimitExceeded from identity_sync, if defined.
try:
    from identity_sync import RateLimitExceeded
except ImportError:
    class RateLimitExceeded(Exception):
        pass

class TestIdentitySync(unittest.TestCase):
    def test_k_zero_returns_only_start_user(self):
        # Graph for testing: no relationships needed.
        graph = {
            "alice@idp1": ["bob@idp2"],
            "bob@idp2": []
        }

        def dummy_get_follows(idp_name, user_id):
            # user_id is in full format already ("alice@idp1")
            return graph.get(user_id, [])
        
        with patch("identity_sync.get_follows", new=dummy_get_follows):
            result = sync_identity("alice@idp1", 0)
            self.assertEqual(result, {"alice@idp1"})

    def test_simple_chain(self):
        # Graph: alice -> bob -> carol
        graph = {
            "alice@idp1": ["bob@idp2"],
            "bob@idp2": ["carol@idp3"],
            "carol@idp3": []
        }

        def dummy_get_follows(idp_name, user_id):
            return graph.get(user_id, [])
        
        with patch("identity_sync.get_follows", new=dummy_get_follows):
            # For k = 1, only alice and bob should be reached.
            result = sync_identity("alice@idp1", 1)
            self.assertEqual(result, {"alice@idp1", "bob@idp2"})
            
            # For k = 2, alice, bob, and carol should be reached.
            result = sync_identity("alice@idp1", 2)
            self.assertEqual(result, {"alice@idp1", "bob@idp2", "carol@idp3"})

    def test_cycle_handling(self):
        # Graph with a cycle: alice -> bob, bob -> alice
        graph = {
            "alice@idp1": ["bob@idp2"],
            "bob@idp2": ["alice@idp1"]
        }

        def dummy_get_follows(idp_name, user_id):
            return graph.get(user_id, [])
        
        with patch("identity_sync.get_follows", new=dummy_get_follows):
            result = sync_identity("alice@idp1", 3)
            # Even with repeated cycles, the set should contain only alice and bob.
            self.assertEqual(result, {"alice@idp1", "bob@idp2"})

    def test_self_loop(self):
        # Graph where a user follows themselves.
        graph = {
            "carol@idp3": ["carol@idp3"]
        }

        def dummy_get_follows(idp_name, user_id):
            return graph.get(user_id, [])
        
        with patch("identity_sync.get_follows", new=dummy_get_follows):
            result = sync_identity("carol@idp3", 2)
            self.assertEqual(result, {"carol@idp3"})

    def test_multiple_neighbors_and_idps(self):
        # More complex graph with multiple neighbors and IdPs.
        graph = {
            "alice@idp1": ["bob@idp2", "carol@idp3"],
            "bob@idp2": ["dave@idp1", "eve@idp2"],
            "carol@idp3": ["frank@idp3"],
            "dave@idp1": [],
            "eve@idp2": ["george@idp4"],
            "frank@idp3": [],
            "george@idp4": []
        }

        def dummy_get_follows(idp_name, user_id):
            return graph.get(user_id, [])
        
        with patch("identity_sync.get_follows", new=dummy_get_follows):
            # For k=1 starting from alice
            result = sync_identity("alice@idp1", 1)
            self.assertEqual(result, {"alice@idp1", "bob@idp2", "carol@idp3"})
            
            # For k=2 starting from alice, should include neighbors of bob and carol too.
            result = sync_identity("alice@idp1", 2)
            self.assertEqual(result, {"alice@idp1", "bob@idp2", "carol@idp3", "dave@idp1", "eve@idp2", "frank@idp3"})
            
            # For k=3, include george as well.
            result = sync_identity("alice@idp1", 3)
            self.assertEqual(result, {"alice@idp1", "bob@idp2", "carol@idp3", "dave@idp1", "eve@idp2", "frank@idp3", "george@idp4"})

    def test_rate_limit_retry(self):
        # Simulate rate-limiting: For a specific user, the first call fails.
        graph = {
            "alice@idp1": ["bob@idp2", "carol@idp3"],
            "bob@idp2": [],
            "carol@idp3": []
        }
        call_counts = {"alice@idp1": 0}

        def dummy_get_follows(idp_name, user_id):
            # Only simulate rate limit for alice@idp1 once.
            if user_id == "alice@idp1":
                if call_counts["alice@idp1"] == 0:
                    call_counts["alice@idp1"] += 1
                    raise RateLimitExceeded("Rate limit exceeded for alice@idp1")
            return graph.get(user_id, [])
        
        with patch("identity_sync.get_follows", new=dummy_get_follows):
            # The solution is expected to handle the RateLimitExceeded exception and retry.
            result = sync_identity("alice@idp1", 1)
            self.assertEqual(result, {"alice@idp1", "bob@idp2", "carol@idp3"})

    def test_discovered_idps(self):
        # Test that the function properly discovers IdPs on the fly.
        graph = {
            "alice@idp1": ["bob@idp2"],
            "bob@idp2": ["carol@idp3"],
            "carol@idp3": ["dave@idp4"],
            "dave@idp4": []
        }

        def dummy_get_follows(idp_name, user_id):
            # Return relationships regardless of the provided idp_name.
            return graph.get(user_id, [])
        
        with patch("identity_sync.get_follows", new=dummy_get_follows):
            result = sync_identity("alice@idp1", 3)
            self.assertEqual(result, {"alice@idp1", "bob@idp2", "carol@idp3", "dave@idp4"})

if __name__ == "__main__":
    unittest.main()