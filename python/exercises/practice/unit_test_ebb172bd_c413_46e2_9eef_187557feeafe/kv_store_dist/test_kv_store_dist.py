import unittest
import time
import threading
import random
import string
from hashlib import md5
import sys
import os

# Ensure the directory containing kv_store_dist is in the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import your implementation
from kv_store_dist.kv_store_dist import DistributedKVStore

def random_string(length):
    """Generate a random string of fixed length."""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))

class TestDistributedKVStore(unittest.TestCase):
    def setUp(self):
        # Initialize with 5 servers, 3 virtual nodes per server, and replication factor 2
        self.store = DistributedKVStore(5, 3, 2)
        
    def test_basic_put_get(self):
        """Test basic put and get operations."""
        self.store.put("key1", "value1")
        self.assertEqual(self.store.get("key1"), "value1")
        
        self.store.put("key2", "value2")
        self.assertEqual(self.store.get("key2"), "value2")
        
        # Test non-existent key
        self.assertIsNone(self.store.get("non_existent_key"))
        
    def test_delete(self):
        """Test delete operation."""
        self.store.put("key1", "value1")
        self.assertEqual(self.store.get("key1"), "value1")
        
        self.store.delete("key1")
        self.assertIsNone(self.store.get("key1"))
        
        # Delete non-existent key should not raise error
        self.store.delete("non_existent_key")
        
    def test_server_join_leave(self):
        """Test server join and leave operations."""
        # Put some initial data
        for i in range(10):
            self.store.put(f"key{i}", f"value{i}")
        
        # Add a new server
        self.store.join("server6")
        
        # Check if data is still accessible
        for i in range(10):
            self.assertEqual(self.store.get(f"key{i}"), f"value{i}")
        
        # Remove a server
        self.store.leave("server1")
        
        # Check if data is still accessible
        for i in range(10):
            self.assertEqual(self.store.get(f"key{i}"), f"value{i}")
        
    def test_data_consistency(self):
        """Test data consistency with updates."""
        self.store.put("key1", "value1")
        self.assertEqual(self.store.get("key1"), "value1")
        
        # Update the value
        time.sleep(0.01)  # Ensure timestamp difference
        self.store.put("key1", "updated_value1")
        self.assertEqual(self.store.get("key1"), "updated_value1")
        
    def test_replication(self):
        """Test that data is properly replicated."""
        # This test is indirect since we don't have direct access to server internals
        # Put data and then remove servers to test replication
        for i in range(20):
            self.store.put(f"rep_key{i}", f"rep_value{i}")
        
        # Remove multiple servers (but fewer than replication factor)
        self.store.leave("server1")
        
        # Check if all data is still accessible
        for i in range(20):
            self.assertEqual(self.store.get(f"rep_key{i}"), f"rep_value{i}")
            
    def test_concurrent_operations(self):
        """Test concurrent operations."""
        num_threads = 10
        operations_per_thread = 50
        
        def worker(worker_id):
            for i in range(operations_per_thread):
                key = f"conc_key_{worker_id}_{i}"
                value = f"conc_value_{worker_id}_{i}"
                self.store.put(key, value)
                
                # Read back to verify
                read_value = self.store.get(key)
                self.assertEqual(read_value, value)
                
                # Occasionally update values
                if i % 5 == 0:
                    updated_value = f"updated_{value}"
                    self.store.put(key, updated_value)
                    read_value = self.store.get(key)
                    self.assertEqual(read_value, updated_value)
                
                # Occasionally delete values
                if i % 10 == 0:
                    self.store.delete(key)
                    self.assertIsNone(self.store.get(key))
        
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
            
        for thread in threads:
            thread.join()
            
    def test_concurrent_server_changes(self):
        """Test server join/leave while operations are ongoing."""
        # Put some initial data
        for i in range(30):
            self.store.put(f"sc_key{i}", f"sc_value{i}")
            
        def operations_worker():
            for i in range(50):
                key = f"sc_op_key{i}"
                value = f"sc_op_value{i}"
                self.store.put(key, value)
                
                # Read some existing keys
                existing_key = f"sc_key{i % 30}"
                self.assertIsNotNone(self.store.get(existing_key))
                
                # Read the key we just wrote
                self.assertEqual(self.store.get(key), value)
                
        def server_changes_worker():
            # Add servers
            self.store.join("new_server1")
            time.sleep(0.05)
            self.store.join("new_server2")
            time.sleep(0.05)
            
            # Remove servers
            self.store.leave("server3")
            time.sleep(0.05)
            self.store.leave("new_server1")
            
        op_thread = threading.Thread(target=operations_worker)
        sc_thread = threading.Thread(target=server_changes_worker)
        
        op_thread.start()
        sc_thread.start()
        
        op_thread.join()
        sc_thread.join()
        
        # Verify that all data is still accessible
        for i in range(50):
            key = f"sc_op_key{i}"
            self.assertEqual(self.store.get(key), f"sc_op_value{i}")
            
    def test_stress_test(self):
        """Stress test with many operations."""
        num_operations = 1000
        keys = [f"stress_key_{i}" for i in range(100)]
        
        for _ in range(num_operations):
            operation = random.choice(["put", "get", "delete"])
            key = random.choice(keys)
            
            if operation == "put":
                value = random_string(10)
                self.store.put(key, value)
            elif operation == "get":
                self.store.get(key)  # Result might be None which is fine
            else:  # delete
                self.store.delete(key)
                
        # Final verification - no errors means test passed
        
    def test_large_cluster(self):
        """Test with a larger number of servers."""
        large_store = DistributedKVStore(20, 5, 3)
        
        # Put some data
        for i in range(100):
            large_store.put(f"large_key{i}", f"large_value{i}")
            
        # Check retrieval
        for i in range(100):
            self.assertEqual(large_store.get(f"large_key{i}"), f"large_value{i}")
            
        # Remove several servers
        large_store.leave("server5")
        large_store.leave("server10")
        large_store.leave("server15")
        
        # Check data is still available
        for i in range(100):
            self.assertEqual(large_store.get(f"large_key{i}"), f"large_value{i}")
            
    def test_inconsistent_data_resolution(self):
        """Test the resolution of inconsistent data."""
        # We need to directly manipulate server data for this test
        # This is a bit of a hack but necessary to test inconsistency resolution
        
        test_key = "inconsistent_key"
        test_value1 = "value1"
        test_value2 = "value2"
        
        # First store a value normally
        self.store.put(test_key, test_value1)
        
        # Find which servers have this key
        key_hash = int(md5(test_key.encode()).hexdigest(), 16) % (2**32)
        
        # Directly modify one replica to have a different value with a newer timestamp
        # Note: This assumes certain implementation details that might need to be adjusted
        flag_modified = False
        for server_id in self.store._servers:
            server = self.store._servers[server_id]
            if test_key in server._data:
                # Create a newer timestamp and different value
                current_time, _ = server._data[test_key]
                server._data[test_key] = (current_time + 1, test_value2)
                flag_modified = True
                break
        
        self.assertTrue(flag_modified, "Failed to modify server data for test")
        
        # Now get the key - it should return the newer value
        result = self.store.get(test_key)
        self.assertEqual(result, test_value2)
        
    def test_edge_cases(self):
        """Test various edge cases."""
        # Empty key
        self.store.put("", "empty_key_value")
        self.assertEqual(self.store.get(""), "empty_key_value")
        
        # Very long key
        long_key = "a" * 256  # Max key size per constraints
        self.store.put(long_key, "long_key_value")
        self.assertEqual(self.store.get(long_key), "long_key_value")
        
        # Large value
        large_value = "x" * (1024 * 1024)  # 1MB
        self.store.put("large_value_key", large_value)
        self.assertEqual(self.store.get("large_value_key"), large_value)
        
        # None value
        self.store.put("none_key", None)
        self.assertIsNone(self.store.get("none_key"))
        
        # Test with very few servers
        min_store = DistributedKVStore(1, 1, 1)
        min_store.put("min_key", "min_value")
        self.assertEqual(min_store.get("min_key"), "min_value")
        
        # Test with maximum parameters
        max_store = DistributedKVStore(100, 10, 100)
        max_store.put("max_key", "max_value")
        self.assertEqual(max_store.get("max_key"), "max_value")
        

if __name__ == '__main__':
    unittest.main()