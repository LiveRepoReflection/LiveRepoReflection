import unittest
import time

from kv_store import DistributedKVStore

class TestDistributedKVStore(unittest.TestCase):
    def setUp(self):
        # Create a store with 4 nodes and a replication factor of 3.
        self.store = DistributedKVStore(num_nodes=4, replication_factor=3)

    def test_put_get(self):
        # Test basic put and get operations.
        self.store.put("key1", "value1")
        result = self.store.get("key1")
        self.assertEqual(result, "value1", "get should return the value that was put.")

    def test_delete(self):
        # Test deletion of a key.
        self.store.put("key_delete", "to_be_deleted")
        self.assertEqual(self.store.get("key_delete"), "to_be_deleted")
        self.store.delete("key_delete")
        self.assertIsNone(self.store.get("key_delete"), "After deletion, get should return None.")

    def test_conflict_resolution(self):
        # Test that a later write overwrites an earlier one (Last-Write-Wins).
        self.store.put("conflict_key", "first_value")
        # Slight pause to simulate later timestamp.
        time.sleep(0.01)
        self.store.put("conflict_key", "second_value")
        result = self.store.get("conflict_key")
        self.assertEqual(result, "second_value", "The last write should win in conflict resolution.")

    def test_node_failure_and_recovery(self):
        # Mark one node down and ensure operations still succeed.
        target_node = 1
        self.store.mark_node_down(target_node)
        self.store.put("failure_key", "updating_during_failure")
        # Even if one node is down, get should fetch from healthy replicas.
        result = self.store.get("failure_key")
        self.assertEqual(result, "updating_during_failure", 
                         "get should retrieve the value even if one replica is down.")
        
        # Bring the node back up.
        self.store.mark_node_up(target_node)
        # Trigger reconciliation for the recovered node.
        self.store.reconcile_node(target_node)
        # Inspect internal node data to confirm key replication.
        node_data = self.store.get_node_data(target_node)
        self.assertIn("failure_key", node_data,
                      "After recovery and reconciliation, the recovered node should have the key.")
        self.assertEqual(node_data["failure_key"][0], "updating_during_failure",
                         "The value in the recovered node should match the updated value.")

    def test_consistent_replication_factor(self):
        # Insert multiple keys and verify that each key is stored exactly replication_factor times.
        keys = [f"key{i}" for i in range(10)]
        for key in keys:
            self.store.put(key, f"value_{key}")
        
        # Allow some time for asynchronous replication to complete.
        time.sleep(0.05)
        replica_counts = {}
        for node_id in range(self.store.num_nodes):
            node_data = self.store.get_node_data(node_id)
            for key in node_data:
                replica_counts[key] = replica_counts.get(key, 0) + 1

        for key in keys:
            self.assertEqual(replica_counts.get(key, 0), self.store.replication_factor,
                             f"Key '{key}' should be replicated exactly {self.store.replication_factor} times.")

    def test_asynchronous_replication_nonblocking(self):
        # Test that the put operation is non-blocking and returns quickly.
        start_time = time.time()
        self.store.put("async_key", "async_value")
        duration = time.time() - start_time
        # We expect the put to complete very quickly (e.g., less than 0.01 seconds).
        self.assertLess(duration, 0.01, "put should return immediately without waiting for replication.")

    def test_reconciliation_after_recovery(self):
        # Test that a node that recovers after downtime receives missed updates.
        target_node = 2
        self.store.mark_node_down(target_node)
        self.store.put("recon_key1", "value1")
        self.store.put("recon_key2", "value2")
        # Allow asynchronous operations to occur on available nodes.
        time.sleep(0.05)
        self.store.mark_node_up(target_node)
        self.store.reconcile_node(target_node)
        
        node_data = self.store.get_node_data(target_node)
        self.assertIn("recon_key1", node_data,
                      "Recovered node should have 'recon_key1' after reconciliation.")
        self.assertIn("recon_key2", node_data,
                      "Recovered node should have 'recon_key2' after reconciliation.")
        self.assertEqual(node_data["recon_key1"][0], "value1")
        self.assertEqual(node_data["recon_key2"][0], "value2")

if __name__ == "__main__":
    unittest.main()