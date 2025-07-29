import unittest
import threading
import time
import random
from concurrent.futures import ThreadPoolExecutor
from consistent_kv import (
    ConsistentKVStore,
    Node
)

class TestConsistentKVStore(unittest.TestCase):
    
    def setUp(self):
        # Create a basic cluster with 5 nodes and replication factor 3
        self.node_ids = [1, 2, 3, 4, 5]
        self.replication_factor = 3
        self.kvstore = ConsistentKVStore(self.node_ids, self.replication_factor)
    
    def test_basic_operations(self):
        """Test basic put, get, and delete operations"""
        # Put and get a value
        self.kvstore.put("key1", "value1")
        self.assertEqual(self.kvstore.get("key1"), "value1")
        
        # Update a value
        self.kvstore.put("key1", "updated_value1")
        self.assertEqual(self.kvstore.get("key1"), "updated_value1")
        
        # Delete a value
        self.kvstore.delete("key1")
        self.assertIsNone(self.kvstore.get("key1"))
        
        # Get a non-existent key
        self.assertIsNone(self.kvstore.get("non_existent_key"))
    
    def test_multiple_keys(self):
        """Test operation with multiple keys"""
        # Put multiple keys
        keys_values = {
            "key1": "value1",
            "key2": "value2",
            "key3": "value3",
            "key4": "value4",
            "key5": "value5"
        }
        
        for key, value in keys_values.items():
            self.kvstore.put(key, value)
        
        # Get all keys
        for key, expected_value in keys_values.items():
            self.assertEqual(self.kvstore.get(key), expected_value)
        
        # Delete some keys
        self.kvstore.delete("key1")
        self.kvstore.delete("key3")
        self.kvstore.delete("key5")
        
        # Verify deletions
        self.assertIsNone(self.kvstore.get("key1"))
        self.assertEqual(self.kvstore.get("key2"), "value2")
        self.assertIsNone(self.kvstore.get("key3"))
        self.assertEqual(self.kvstore.get("key4"), "value4")
        self.assertIsNone(self.kvstore.get("key5"))
    
    def test_node_failure(self):
        """Test resilience to node failures"""
        # Put some data
        self.kvstore.put("key1", "value1")
        self.kvstore.put("key2", "value2")
        
        # Simulate a node failure
        failed_node = self.node_ids[2]  # Node ID 3
        self.kvstore.node_failure(failed_node)
        
        # Verify data is still accessible
        self.assertEqual(self.kvstore.get("key1"), "value1")
        self.assertEqual(self.kvstore.get("key2"), "value2")
        
        # Put new data with a node down
        self.kvstore.put("key3", "value3")
        self.assertEqual(self.kvstore.get("key3"), "value3")
        
        # Bring the node back online
        self.kvstore.node_recovery(failed_node)
        
        # Verify all data is still accessible
        self.assertEqual(self.kvstore.get("key1"), "value1")
        self.assertEqual(self.kvstore.get("key2"), "value2")
        self.assertEqual(self.kvstore.get("key3"), "value3")
    
    def test_multiple_node_failures(self):
        """Test resilience to multiple node failures"""
        # Put some data
        self.kvstore.put("key1", "value1")
        
        # Simulate multiple node failures (but less than replication factor)
        failed_nodes = self.node_ids[:2]  # Node IDs 1 and 2
        for node_id in failed_nodes:
            self.kvstore.node_failure(node_id)
        
        # Verify data is still accessible
        self.assertEqual(self.kvstore.get("key1"), "value1")
        
        # Recover the nodes
        for node_id in failed_nodes:
            self.kvstore.node_recovery(node_id)
        
        # Verify data is still accessible
        self.assertEqual(self.kvstore.get("key1"), "value1")
    
    def test_read_repair(self):
        """Test read repair mechanism for eventual consistency"""
        # Put a value
        self.kvstore.put("key1", "value1")
        
        # Directly modify one of the replicas to create an inconsistency
        # This is a special test method that should be implemented in the KV store class
        self.kvstore.create_inconsistency("key1", "incorrect_value", 1)
        
        # Reading should trigger read repair
        value = self.kvstore.get("key1")
        
        # We should get the correct value
        self.assertEqual(value, "value1")
        
        # After some time, all replicas should be consistent
        time.sleep(0.1)  # Allow time for read repair to complete
        
        # Verify all replicas have the correct value
        inconsistency = self.kvstore.check_inconsistency("key1")
        self.assertFalse(inconsistency, "Read repair did not fix the inconsistency")
    
    def test_concurrent_operations(self):
        """Test handling of concurrent operations"""
        num_threads = 10
        operations_per_thread = 100
        
        def worker(thread_id):
            for i in range(operations_per_thread):
                key = f"thread{thread_id}_key{i}"
                value = f"thread{thread_id}_value{i}"
                self.kvstore.put(key, value)
                
                # Verify the put was successful
                self.assertEqual(self.kvstore.get(key), value)
                
                # 25% chance to delete the key
                if random.random() < 0.25:
                    self.kvstore.delete(key)
                    self.assertIsNone(self.kvstore.get(key))
        
        # Create and start threads
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(worker, i) for i in range(num_threads)]
            
            # Wait for all threads to complete
            for future in futures:
                future.result()
    
    def test_different_cluster_sizes(self):
        """Test with different cluster sizes"""
        # Test with minimal cluster (replication factor = number of nodes)
        min_kvstore = ConsistentKVStore([1, 2, 3], 3)
        min_kvstore.put("key1", "value1")
        self.assertEqual(min_kvstore.get("key1"), "value1")
        
        # Test with larger cluster
        large_node_ids = list(range(1, 11))  # 10 nodes
        large_kvstore = ConsistentKVStore(large_node_ids, 5)
        large_kvstore.put("key1", "value1")
        self.assertEqual(large_kvstore.get("key1"), "value1")
        
        # Simulate multiple failures in large cluster
        for node_id in large_node_ids[:4]:  # Fail 4 nodes
            large_kvstore.node_failure(node_id)
        
        # Should still be able to get the value (5 replicas, 4 nodes failed)
        self.assertEqual(large_kvstore.get("key1"), "value1")
    
    def test_distribution(self):
        """Test that keys are distributed evenly"""
        # Create a larger key space
        num_keys = 1000
        for i in range(num_keys):
            key = f"key{i}"
            value = f"value{i}"
            self.kvstore.put(key, value)
        
        # Check the distribution of keys across nodes
        node_key_counts = self.kvstore.get_key_distribution()
        
        # Each node should have approximately the same number of keys
        # Calculate the standard deviation to measure evenness
        avg_keys_per_node = num_keys * self.replication_factor / len(self.node_ids)
        sum_squared_diff = sum((count - avg_keys_per_node) ** 2 for count in node_key_counts.values())
        std_dev = (sum_squared_diff / len(self.node_ids)) ** 0.5
        
        # Standard deviation should be reasonable for even distribution
        # For a good hash function, std_dev should be small relative to the average
        self.assertLess(std_dev / avg_keys_per_node, 0.5, 
                        "Keys are not distributed evenly across nodes")
    
    def test_node_addition(self):
        """Test adding a new node to the cluster"""
        # Put some initial data
        for i in range(10):
            self.kvstore.put(f"key{i}", f"value{i}")
        
        # Add a new node
        new_node_id = 6
        self.kvstore.add_node(new_node_id)
        
        # Verify all data is still accessible
        for i in range(10):
            self.assertEqual(self.kvstore.get(f"key{i}"), f"value{i}")
        
        # Add more data
        for i in range(10, 20):
            self.kvstore.put(f"key{i}", f"value{i}")
            self.assertEqual(self.kvstore.get(f"key{i}"), f"value{i}")


if __name__ == "__main__":
    unittest.main()