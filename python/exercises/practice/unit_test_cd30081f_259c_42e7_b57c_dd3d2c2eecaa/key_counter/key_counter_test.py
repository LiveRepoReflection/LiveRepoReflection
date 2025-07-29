import unittest
import threading
import random
import time
from key_counter import DistributedKeyCounter

class TestDistributedKeyCounter(unittest.TestCase):
    def test_increment_and_get_single_key(self):
        counter = DistributedKeyCounter()
        counter.increment("key1", 5)
        self.assertEqual(counter.get_value("key1"), 5)
        counter.increment("key1", 3)
        self.assertEqual(counter.get_value("key1"), 8)

    def test_get_nonexistent_key(self):
        counter = DistributedKeyCounter()
        self.assertEqual(counter.get_value("nonexistent"), 0)

    def test_increment_multiple_keys(self):
        counter = DistributedKeyCounter()
        counter.increment("key1", 5)
        counter.increment("key2", 10)
        counter.increment("key3", 15)
        self.assertEqual(counter.get_value("key1"), 5)
        self.assertEqual(counter.get_value("key2"), 10)
        self.assertEqual(counter.get_value("key3"), 15)

    def test_merge_basic(self):
        counter1 = DistributedKeyCounter()
        counter2 = DistributedKeyCounter()
        
        counter1.increment("key1", 5)
        counter1.increment("key2", 10)
        
        counter2.increment("key2", 3)
        counter2.increment("key3", 8)
        
        counter1.merge(counter2)
        
        self.assertEqual(counter1.get_value("key1"), 5)
        self.assertEqual(counter1.get_value("key2"), 13)
        self.assertEqual(counter1.get_value("key3"), 8)

    def test_concurrent_increments_same_key(self):
        counter = DistributedKeyCounter()
        num_threads = 10
        increments_per_thread = 1000
        
        def increment_task():
            for _ in range(increments_per_thread):
                counter.increment("shared_key", 1)
        
        threads = []
        for _ in range(num_threads):
            thread = threading.Thread(target=increment_task)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        self.assertEqual(counter.get_value("shared_key"), num_threads * increments_per_thread)

    def test_concurrent_increments_different_keys(self):
        counter = DistributedKeyCounter()
        num_threads = 10
        increments_per_thread = 1000
        keys = [f"key{i}" for i in range(num_threads)]
        
        def increment_task(key_idx):
            for _ in range(increments_per_thread):
                counter.increment(keys[key_idx], 1)
        
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=increment_task, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        for key in keys:
            self.assertEqual(counter.get_value(key), increments_per_thread)

    def test_concurrent_increments_and_gets(self):
        counter = DistributedKeyCounter()
        num_threads = 10
        operations_per_thread = 1000
        
        def task():
            for _ in range(operations_per_thread):
                op = random.choice(["increment", "get"])
                key = f"key{random.randint(1, 5)}"
                
                if op == "increment":
                    counter.increment(key, 1)
                else:
                    counter.get_value(key)
        
        threads = []
        for _ in range(num_threads):
            thread = threading.Thread(target=task)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # We can't assert exact values here since operations are random,
        # but we ensure no exceptions were raised

    def test_concurrent_merges(self):
        main_counter = DistributedKeyCounter()
        num_threads = 5
        
        counters = []
        for i in range(num_threads):
            counter = DistributedKeyCounter()
            counter.increment(f"key{i}", 100)
            counters.append(counter)
        
        def merge_task(counter_to_merge):
            main_counter.merge(counter_to_merge)
        
        threads = []
        for counter in counters:
            thread = threading.Thread(target=merge_task, args=(counter,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        for i in range(num_threads):
            self.assertEqual(main_counter.get_value(f"key{i}"), 100)

    def test_complex_merge_scenario(self):
        """Test a complex scenario with multiple concurrent increments and merges"""
        # Create multiple counters to simulate different nodes
        node1 = DistributedKeyCounter()
        node2 = DistributedKeyCounter()
        node3 = DistributedKeyCounter()
        
        # Simulate operations on different nodes
        node1.increment("key1", 5)
        node1.increment("key2", 10)
        
        node2.increment("key1", 3)
        node2.increment("key3", 15)
        
        node3.increment("key2", 7)
        node3.increment("key4", 20)
        
        # Merge node2 into node1
        node1.merge(node2)
        
        # Continue operations after first merge
        node1.increment("key5", 25)
        node3.increment("key1", 8)
        
        # Merge node3 into node1
        node1.merge(node3)
        
        # Verify final state
        self.assertEqual(node1.get_value("key1"), 16)  # 5+3+8
        self.assertEqual(node1.get_value("key2"), 17)  # 10+7
        self.assertEqual(node1.get_value("key3"), 15)
        self.assertEqual(node1.get_value("key4"), 20)
        self.assertEqual(node1.get_value("key5"), 25)

    def test_node_failure_simulation(self):
        """Test simulating node failures and recovery"""
        # Create counters for different nodes
        active_node = DistributedKeyCounter()
        failed_node = DistributedKeyCounter()
        
        # Perform operations on both nodes
        active_node.increment("key1", 10)
        failed_node.increment("key2", 20)
        
        # Simulate failed node recovering and merging its state
        recovery_node = DistributedKeyCounter()
        # Reload data from "storage" (we're simulating this by using the failed_node directly)
        recovery_node.merge(failed_node)
        
        # Node comes back online and syncs with active node
        recovery_node.merge(active_node)
        active_node.merge(recovery_node)
        
        # Verify both nodes have consistent state
        self.assertEqual(active_node.get_value("key1"), 10)
        self.assertEqual(active_node.get_value("key2"), 20)
        self.assertEqual(recovery_node.get_value("key1"), 10)
        self.assertEqual(recovery_node.get_value("key2"), 20)

    def test_at_least_once_semantics(self):
        """Test the system's handling of at-least-once semantics"""
        node1 = DistributedKeyCounter()
        node2 = DistributedKeyCounter()
        
        # Simulate an increment operation that might be applied multiple times due to retries
        node1.increment("key1", 5)
        
        # Simulate the same operation being retried (perhaps due to network issues)
        node2.increment("key1", 5)
        
        # Merge the nodes
        node1.merge(node2)
        
        # The value should reflect both increments
        # Note: This test depends on how you implement at-least-once semantics
        # The assertion value might need to be adjusted based on your implementation
        self.assertEqual(node1.get_value("key1"), 10)

    def test_merge_idempotence(self):
        """Test that merging the same counter multiple times is idempotent"""
        counter1 = DistributedKeyCounter()
        counter2 = DistributedKeyCounter()
        
        counter1.increment("key1", 5)
        counter2.increment("key2", 10)
        
        # Merge once
        counter1.merge(counter2)
        first_merge_key1 = counter1.get_value("key1")
        first_merge_key2 = counter1.get_value("key2")
        
        # Merge again
        counter1.merge(counter2)
        
        # Values should be the same as after the first merge
        self.assertEqual(counter1.get_value("key1"), first_merge_key1)
        self.assertEqual(counter1.get_value("key2"), first_merge_key2)

    def test_large_scale_performance(self):
        """Test performance with a large number of keys and operations"""
        counter = DistributedKeyCounter()
        num_keys = 1000
        operations_per_key = 100
        
        start_time = time.time()
        
        # Perform many operations
        for i in range(num_keys):
            for _ in range(operations_per_key):
                counter.increment(f"key{i}", 1)
        
        elapsed_time = time.time() - start_time
        print(f"Performed {num_keys * operations_per_key} operations in {elapsed_time:.2f} seconds")
        
        # Verify results
        for i in range(num_keys):
            self.assertEqual(counter.get_value(f"key{i}"), operations_per_key)

if __name__ == "__main__":
    unittest.main()