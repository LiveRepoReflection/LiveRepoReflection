import unittest
import threading
import time
import random
from event_aggregate import EventAggregator

class EventAggregatorTest(unittest.TestCase):
    def test_basic_aggregation(self):
        aggregator = EventAggregator(max_memory_mb=100)
        
        # Add some events for a single user
        events = [
            (1000, "user1", 5.0),
            (2000, "user1", 10.0),
            (3000, "user1", 15.0),
            (4000, "user1", 20.0),
        ]
        
        for event in events:
            aggregator.ingest_event(*event)
            
        # Test aggregation for the entire time range
        self.assertEqual(aggregator.aggregate_values("user1", 1000, 4000), 50.0)
        
        # Test aggregation for a subset of the time range
        self.assertEqual(aggregator.aggregate_values("user1", 2000, 3000), 25.0)
        
        # Test aggregation for a time range with no events
        self.assertEqual(aggregator.aggregate_values("user1", 5000, 6000), 0.0)
        
        # Test aggregation for a non-existent user
        self.assertEqual(aggregator.aggregate_values("user2", 1000, 4000), 0.0)

    def test_multiple_users(self):
        aggregator = EventAggregator(max_memory_mb=100)
        
        # Add events for multiple users
        events = [
            (1000, "user1", 5.0),
            (1500, "user2", 7.5),
            (2000, "user1", 10.0),
            (2500, "user2", 12.5),
            (3000, "user1", 15.0),
            (3500, "user2", 17.5),
            (4000, "user1", 20.0),
            (4500, "user2", 22.5),
        ]
        
        for event in events:
            aggregator.ingest_event(*event)
            
        # Test aggregation for each user
        self.assertEqual(aggregator.aggregate_values("user1", 1000, 4000), 50.0)
        self.assertEqual(aggregator.aggregate_values("user2", 1000, 4500), 60.0)
        
        # Test aggregation for specific time ranges
        self.assertEqual(aggregator.aggregate_values("user1", 2000, 3000), 25.0)
        self.assertEqual(aggregator.aggregate_values("user2", 2500, 3500), 30.0)

    def test_overlapping_timestamps(self):
        aggregator = EventAggregator(max_memory_mb=100)
        
        # Add events with the same timestamp
        events = [
            (1000, "user1", 5.0),
            (1000, "user1", 10.0),
            (1000, "user2", 15.0),
            (1000, "user2", 20.0),
        ]
        
        for event in events:
            aggregator.ingest_event(*event)
            
        # Test aggregation
        self.assertEqual(aggregator.aggregate_values("user1", 1000, 1000), 15.0)
        self.assertEqual(aggregator.aggregate_values("user2", 1000, 1000), 35.0)

    def test_out_of_order_events(self):
        aggregator = EventAggregator(max_memory_mb=100)
        
        # Add events in non-chronological order
        events = [
            (4000, "user1", 20.0),
            (1000, "user1", 5.0),
            (3000, "user1", 15.0),
            (2000, "user1", 10.0),
        ]
        
        for event in events:
            aggregator.ingest_event(*event)
            
        # Test aggregation (result should be the same as if events were ingested in order)
        self.assertEqual(aggregator.aggregate_values("user1", 1000, 4000), 50.0)

    def test_memory_management(self):
        # Create an aggregator with a very small memory limit
        aggregator = EventAggregator(max_memory_mb=0.001)  # About 1KB
        
        # Add enough events to exceed the memory limit
        for i in range(1000):
            aggregator.ingest_event(i, f"user{i%10}", 1.0)
            
        # The aggregator should have discarded some old data but still function
        # We can't test exact values here since the behavior depends on the implementation
        # But we can ensure the system doesn't crash and returns something
        result = aggregator.aggregate_values("user0", 0, 1000)
        self.assertIsNotNone(result)

    def test_edge_cases(self):
        aggregator = EventAggregator(max_memory_mb=100)
        
        # Test with extreme timestamp values
        aggregator.ingest_event(0, "user1", 10.0)
        aggregator.ingest_event(9999999999999, "user1", 20.0)
        
        self.assertEqual(aggregator.aggregate_values("user1", 0, 0), 10.0)
        self.assertEqual(aggregator.aggregate_values("user1", 9999999999999, 9999999999999), 20.0)
        
        # Test with negative values
        aggregator.ingest_event(5000, "user1", -10.0)
        self.assertEqual(aggregator.aggregate_values("user1", 5000, 5000), -10.0)
        
        # Test with zero values
        aggregator.ingest_event(6000, "user1", 0.0)
        self.assertEqual(aggregator.aggregate_values("user1", 6000, 6000), 0.0)
        
        # Test with floating point timestamps (should handle according to implementation)
        try:
            aggregator.ingest_event(7000.5, "user1", 15.0)
            # If implementation accepts floats, test the aggregation
            self.assertEqual(aggregator.aggregate_values("user1", 7000, 7001), 15.0)
        except Exception:
            pass  # If implementation rejects floats, that's fine too

    def test_concurrency(self):
        aggregator = EventAggregator(max_memory_mb=100)
        num_threads = 10
        events_per_thread = 1000
        
        def ingest_events(thread_id):
            for i in range(events_per_thread):
                timestamp = i * 10 + thread_id
                user_id = f"user{thread_id}"
                value = 1.0
                aggregator.ingest_event(timestamp, user_id, value)
        
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=ingest_events, args=(i,))
            threads.append(thread)
            thread.start()
            
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
            
        # Verify results
        for i in range(num_threads):
            user_id = f"user{i}"
            # Each thread added events_per_thread events with value 1.0
            self.assertEqual(aggregator.aggregate_values(user_id, 0, events_per_thread * 10), events_per_thread)

    def test_mixed_operations(self):
        aggregator = EventAggregator(max_memory_mb=100)
        stop_flag = threading.Event()
        results = []
        
        def ingest_events():
            i = 0
            while not stop_flag.is_set():
                timestamp = int(time.time() * 1000) + i
                user_id = f"user{i % 5}"
                value = random.uniform(1.0, 10.0)
                aggregator.ingest_event(timestamp, user_id, value)
                i += 1
                time.sleep(0.001)
        
        def query_aggregation():
            while not stop_flag.is_set():
                user_id = f"user{random.randint(0, 4)}"
                now = int(time.time() * 1000)
                start_time = now - 10000  # 10 seconds ago
                result = aggregator.aggregate_values(user_id, start_time, now)
                results.append(result)
                time.sleep(0.005)
        
        threads = []
        # Start 3 ingestion threads
        for _ in range(3):
            thread = threading.Thread(target=ingest_events)
            thread.daemon = True
            threads.append(thread)
            thread.start()
            
        # Start 2 aggregation threads
        for _ in range(2):
            thread = threading.Thread(target=query_aggregation)
            thread.daemon = True
            threads.append(thread)
            thread.start()
            
        # Let the threads run for a short time
        time.sleep(1)
        stop_flag.set()
        
        # No assertions here, we just ensure the system doesn't crash under concurrent access
        self.assertTrue(len(results) > 0)

    def test_boundary_conditions(self):
        aggregator = EventAggregator(max_memory_mb=100)
        
        # Test with empty user_id
        aggregator.ingest_event(1000, "", 10.0)
        self.assertEqual(aggregator.aggregate_values("", 1000, 1000), 10.0)
        
        # Test with very large values
        aggregator.ingest_event(2000, "user1", 1e20)
        self.assertEqual(aggregator.aggregate_values("user1", 2000, 2000), 1e20)
        
        # Test with very small values
        aggregator.ingest_event(3000, "user1", 1e-20)
        self.assertEqual(aggregator.aggregate_values("user1", 3000, 3000), 1e-20)
        
        # Test with start_time > end_time (should handle according to implementation)
        try:
            result = aggregator.aggregate_values("user1", 5000, 4000)
            # Could be 0.0, None, or raise an exception depending on implementation
            self.assertIn(result, [0.0, None])
        except ValueError:
            pass  # Raising an exception is also a valid approach

    def test_performance(self):
        # This is a simple performance test to ensure the implementation is reasonably efficient
        aggregator = EventAggregator(max_memory_mb=100)
        
        # Generate a large number of events
        num_events = 100000
        user_ids = [f"user{i%100}" for i in range(num_events)]
        timestamps = list(range(1000, 1000 + num_events))
        values = [1.0] * num_events
        
        start_time = time.time()
        for i in range(num_events):
            aggregator.ingest_event(timestamps[i], user_ids[i], values[i])
        ingestion_time = time.time() - start_time
        
        # Perform some aggregations
        start_time = time.time()
        for i in range(100):
            user_id = f"user{i}"
            aggregator.aggregate_values(user_id, 1000, 1000 + num_events)
        aggregation_time = time.time() - start_time
        
        # We can't make specific assertions about timing, but we can print out performance info
        print(f"Ingested {num_events} events in {ingestion_time:.2f} seconds")
        print(f"Performed 100 aggregations in {aggregation_time:.2f} seconds")
        
        # Just ensure the test completes without errors
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()