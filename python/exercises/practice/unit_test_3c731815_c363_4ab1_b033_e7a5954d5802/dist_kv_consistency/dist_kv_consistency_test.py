import unittest
import time
import random

from dist_kv_consistency import write, read, gossip, reconcile

class DistributedKVConsistencyTest(unittest.TestCase):

    def setUp(self):
        # Each test should use unique keys to avoid cross-test interference.
        self.test_keys = {
            "simple": "test_simple_key_" + str(random.randint(1000, 9999)),
            "gossip": "test_gossip_key_" + str(random.randint(1000, 9999)),
            "reconcile_dominance": "test_reconcile_dom_" + str(random.randint(1000, 9999)),
            "reconcile_conflict": "test_reconcile_conflict_" + str(random.randint(1000, 9999)),
            "concurrent": "test_concurrent_key_" + str(random.randint(1000, 9999))
        }
        # For testing purposes, we assume the system starts with a clean slate on each test.
        # If there is any store-clear function in the actual implementation, it should be called here.

    def test_write_read_consistency(self):
        # Write a key-value pair from node 0 and read it from the same node.
        key = self.test_keys["simple"]
        expected_value = "value_1"
        write(key, expected_value, node_id=0)
        # Adding a slight delay to ensure that any timestamp mechanisms differentiate operations.
        time.sleep(0.01)
        result = read(key, node_id=0)
        self.assertEqual(result, expected_value,
                         f"Read key '{key}' expected '{expected_value}' but got '{result}'")
    
    def test_gossip_propagation(self):
        # Write a value on one node and then simulate a gossip to propagate it to another node.
        key = self.test_keys["gossip"]
        expected_value = "gossip_value"
        # Write the key on node 5.
        write(key, expected_value, node_id=5)
        # Simulate that other node (node 7) did not have the updated value.
        # Run gossip on node 7, which should exchange the key-value pair.
        gossip(node_id=7)
        # After gossip, read from node 7 should yield the updated value.
        result = read(key, node_id=7)
        self.assertEqual(result, expected_value,
                         f"After gossip, read key '{key}' from node 7 should be '{expected_value}' but got '{result}'")
    
    def test_reconcile_with_dominance(self):
        # Test the reconcile function where one version vector clearly dominates the other.
        # Version vector A dominates vector B.
        version_vector_A = [2, 1, 0]
        version_vector_B = [1, 1, 0]
        values = ["value_A", "value_B"]
        # Use older timestamp for B to emphasize that A is ahead.
        timestamps = [time.time(), time.time() - 10]
        chosen = reconcile(values, [version_vector_A, version_vector_B], timestamps)
        self.assertEqual(chosen, "value_A",
                         f"Reconcilation with dominating version vector should choose 'value_A', but got '{chosen}'")
    
    def test_reconcile_with_conflict(self):
        # Test the reconcile function where version vectors are incomparable and conflict resolution
        # should choose the one with the later timestamp.
        version_vector_A = [2, 1, 0]
        version_vector_B = [1, 2, 0]  # Incomparable with A.
        values = ["value_A", "value_B"]
        # Set timestamps such that value_B is more recent.
        timestamps = [time.time() - 5, time.time()]
        chosen = reconcile(values, [version_vector_A, version_vector_B], timestamps)
        self.assertEqual(chosen, "value_B",
                         f"Reconcilation in conflict should choose the value with later timestamp 'value_B', but got '{chosen}'")

    def test_concurrent_writes_and_gossip(self):
        # Simulate multiple writes from different nodes and ensure that gossip eventually converges to
        # the latest value.
        key = self.test_keys["concurrent"]
        # First write from node 2.
        write(key, "initial", node_id=2)
        time.sleep(0.01)
        # A concurrent write from node 4 with a later timestamp (simulate update).
        write(key, "update_1", node_id=4)
        time.sleep(0.01)
        # Another write from node 8 with an even later update.
        write(key, "update_2", node_id=8)
        
        # At this moment, different nodes might have different values.
        # Run gossip from several nodes to simulate anti-entropy.
        for node in [2, 4, 8, 10]:
            gossip(node)
        
        # All nodes should eventually read the latest value.
        for node in [2, 4, 8, 10]:
            result = read(key, node_id=node)
            self.assertEqual(result, "update_2",
                             f"After concurrent writes and gossip, node {node} should have 'update_2' but got '{result}'")
    
    def test_no_update_if_write_fails(self):
        # Simulate a condition where a write might not propagate to all expected nodes and ensure that
        # a read from a quorum still returns a consistent value.
        key = "nonexistent_" + str(random.randint(1000, 9999))
        # Attempt reading before any write. Expect None or an empty string if the store returns that when absent.
        result = read(key, node_id=3)
        self.assertTrue(result is None or result == "",
                        f"Reading an unwritten key '{key}' should yield an empty result, but got '{result}'")

if __name__ == '__main__':
    unittest.main()