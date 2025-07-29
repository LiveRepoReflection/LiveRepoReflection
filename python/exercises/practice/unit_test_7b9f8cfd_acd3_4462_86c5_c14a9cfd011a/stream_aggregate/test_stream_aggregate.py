import unittest
import time
import random
from stream_aggregate import EventAggregator

class TestStreamAggregate(unittest.TestCase):
    def setUp(self):
        self.aggregator = EventAggregator()
        self.event_types = ['post', 'like', 'comment', 'share']
        self.regions = ['US', 'EU', 'Asia', 'Africa', 'Oceania']
        
    def test_single_event(self):
        self.aggregator.process_event('post', 'US', 1000)
        count = self.aggregator.query_event_count('post', 'US', 999, 1001)
        self.assertEqual(count, 1)
        
    def test_multiple_events_same_type_region(self):
        for i in range(100):
            self.aggregator.process_event('like', 'EU', 1000 + i)
        count = self.aggregator.query_event_count('like', 'EU', 1000, 1099)
        self.assertEqual(count, 100)
        
    def test_time_window_boundaries(self):
        self.aggregator.process_event('comment', 'Asia', 2000)
        self.assertEqual(self.aggregator.query_event_count('comment', 'Asia', 2000, 2000), 1)
        self.assertEqual(self.aggregator.query_event_count('comment', 'Asia', 1999, 2001), 1)
        self.assertEqual(self.aggregator.query_event_count('comment', 'Asia', 2001, 2002), 0)
        
    def test_out_of_order_timestamps(self):
        self.aggregator.process_event('share', 'Africa', 3000)
        self.aggregator.process_event('share', 'Africa', 2999)
        count = self.aggregator.query_event_count('share', 'Africa', 2999, 3000)
        self.assertEqual(count, 2)
        
    def test_empty_query(self):
        count = self.aggregator.query_event_count('post', 'Oceania', 4000, 5000)
        self.assertEqual(count, 0)
        
    def test_high_volume_performance(self):
        start_time = time.time()
        for i in range(10000):
            event_type = random.choice(self.event_types)
            region = random.choice(self.regions)
            timestamp = random.randint(5000, 6000)
            self.aggregator.process_event(event_type, region, timestamp)
            
        query_time = time.time()
        count = self.aggregator.query_event_count('like', 'US', 5500, 5700)
        end_time = time.time()
        
        self.assertLess(end_time - query_time, 0.1, "Query should be fast even with high volume")
        
    def test_edge_cases(self):
        # Test empty event type
        self.aggregator.process_event('', 'US', 7000)
        count = self.aggregator.query_event_count('', 'US', 6999, 7001)
        self.assertEqual(count, 1)
        
        # Test empty region
        self.aggregator.process_event('post', '', 8000)
        count = self.aggregator.query_event_count('post', '', 7999, 8001)
        self.assertEqual(count, 1)
        
        # Test negative timestamp
        self.aggregator.process_event('like', 'EU', -1000)
        count = self.aggregator.query_event_count('like', 'EU', -1001, -999)
        self.assertEqual(count, 1)
        
    def test_concurrent_operations(self):
        from threading import Thread
        
        def process_events():
            for i in range(1000):
                self.aggregator.process_event('comment', 'Asia', 9000 + i)
                
        def query_events():
            for i in range(100):
                count = self.aggregator.query_event_count('comment', 'Asia', 9000, 9999)
                self.assertGreaterEqual(count, 0)
                
        threads = [
            Thread(target=process_events),
            Thread(target=query_events),
            Thread(target=process_events)
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
            
        final_count = self.aggregator.query_event_count('comment', 'Asia', 9000, 9999)
        self.assertEqual(final_count, 2000)
        
    def test_persistence_simulation(self):
        # Simulate system restart by creating new instance
        for i in range(100):
            self.aggregator.process_event('post', 'US', 10000 + i)
            
        new_aggregator = EventAggregator()
        # In a real system, we would load persisted data here
        count = new_aggregator.query_event_count('post', 'US', 10000, 10099)
        self.assertEqual(count, 0)  # Expect 0 because we didn't implement actual persistence
        
if __name__ == '__main__':
    unittest.main()