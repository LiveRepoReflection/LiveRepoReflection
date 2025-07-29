import unittest
from key_value_store import DistributedKeyValueStore

class TestDistributedKeyValueStore(unittest.TestCase):
    
    def test_basic_operations(self):
        store = DistributedKeyValueStore(100)
        
        # Basic PUT and GET
        store.put("key1", 123, 3)
        self.assertEqual(store.get("key1"), 123)
        
        # PUT another key
        store.put("key2", 456, 2)
        self.assertEqual(store.get("key2"), 456)
        
        # DELETE and verify
        store.delete("key1")
        self.assertEqual(store.get("key1"), -1)
        
        # PUT a key that was deleted
        store.put("key1", 789, 1)
        self.assertEqual(store.get("key1"), 789)
    
    def test_replication_factor(self):
        store = DistributedKeyValueStore(10)
        
        # Test with various replication factors
        store.put("keyA", 111, 1)
        store.put("keyB", 222, 5)
        store.put("keyC", 333, 10)
        
        self.assertEqual(store.get("keyA"), 111)
        self.assertEqual(store.get("keyB"), 222)
        self.assertEqual(store.get("keyC"), 333)
    
    def test_update_key(self):
        store = DistributedKeyValueStore(100)
        
        # Update a key multiple times
        store.put("updateKey", 100, 3)
        self.assertEqual(store.get("updateKey"), 100)
        
        store.put("updateKey", 200, 2)
        self.assertEqual(store.get("updateKey"), 200)
        
        store.put("updateKey", 300, 1)
        self.assertEqual(store.get("updateKey"), 300)
    
    def test_nonexistent_key(self):
        store = DistributedKeyValueStore(100)
        
        # Try to get a key that doesn't exist
        self.assertEqual(store.get("nonexistent"), -1)
        
        # Delete a key that doesn't exist (should not raise an error)
        store.delete("nonexistent")
        self.assertEqual(store.get("nonexistent"), -1)
    
    def test_large_values(self):
        store = DistributedKeyValueStore(100)
        
        # Test with large values
        store.put("largeValue", 10**9, 3)
        self.assertEqual(store.get("largeValue"), 10**9)
    
    def test_deterministic_node_selection(self):
        store1 = DistributedKeyValueStore(100)
        store2 = DistributedKeyValueStore(100)
        
        # Same key should be stored on the same nodes in different instances
        store1.put("testKey", 123, 3)
        store2.put("testKey", 123, 3)
        
        # We can't directly check node selection in this test, but we can
        # ensure consistent behavior across instances
        self.assertEqual(store1.get("testKey"), store2.get("testKey"))
    
    def test_many_keys(self):
        store = DistributedKeyValueStore(100)
        
        # Add many keys
        for i in range(1000):
            key = f"key{i}"
            value = i + 1000
            store.put(key, value, 2)
        
        # Verify keys
        for i in range(1000):
            key = f"key{i}"
            value = i + 1000
            self.assertEqual(store.get(key), value)
        
        # Delete some keys
        for i in range(0, 1000, 2):
            key = f"key{i}"
            store.delete(key)
        
        # Verify deleted and non-deleted keys
        for i in range(1000):
            key = f"key{i}"
            if i % 2 == 0:
                self.assertEqual(store.get(key), -1)
            else:
                self.assertEqual(store.get(key), i + 1000)
    
    def test_edge_cases(self):
        store = DistributedKeyValueStore(100)
        
        # Minimum and maximum replication factors
        store.put("minRep", 100, 1)
        self.assertEqual(store.get("minRep"), 100)
        
        store.put("maxRep", 200, 100)
        self.assertEqual(store.get("maxRep"), 200)
        
        # Special characters in keys (alphanumeric only per requirements)
        store.put("key123", 300, 3)
        self.assertEqual(store.get("key123"), 300)
    
    def test_version_control(self):
        store = DistributedKeyValueStore(100)
        
        # Test version control with updates across different replication factors
        store.put("versionKey", 100, 5)
        self.assertEqual(store.get("versionKey"), 100)
        
        store.put("versionKey", 200, 3)
        self.assertEqual(store.get("versionKey"), 200)
        
        store.put("versionKey", 300, 7)
        self.assertEqual(store.get("versionKey"), 300)
    
    def test_large_system(self):
        # Test with maximum node count
        large_store = DistributedKeyValueStore(1000)
        
        # Add keys with large replication factor
        large_store.put("largeKey1", 10000, 500)
        self.assertEqual(large_store.get("largeKey1"), 10000)
        
        large_store.put("largeKey2", 20000, 750)
        self.assertEqual(large_store.get("largeKey2"), 20000)
        
        large_store.put("largeKey3", 30000, 1000)
        self.assertEqual(large_store.get("largeKey3"), 30000)

    def test_simulation(self):
        store = DistributedKeyValueStore(100)
        
        # Simulate the example in the problem statement
        store.put("key1", 123, 3)
        self.assertEqual(store.get("key1"), 123)
        
        store.put("key2", 456, 2)
        self.assertEqual(store.get("key2"), 456)
        
        store.delete("key1")
        self.assertEqual(store.get("key1"), -1)
        
        store.put("key1", 789, 1)
        self.assertEqual(store.get("key1"), 789)

if __name__ == "__main__":
    unittest.main()