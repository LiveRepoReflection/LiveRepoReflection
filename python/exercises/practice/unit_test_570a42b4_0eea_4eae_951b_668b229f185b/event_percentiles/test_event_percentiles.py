import unittest
import time
import random
from event_percentiles.event_percentiles import EventPercentiles

class TestEventPercentiles(unittest.TestCase):
    def setUp(self):
        self.window_sizes = [60, 300, 3600]  # 1min, 5min, 1hr
        self.percentiles = [0.5, 0.9, 0.95]
        self.accuracy = 0.01
        self.max_event_age = 3600  # 1hr
        self.ep = EventPercentiles(self.window_sizes, self.percentiles, self.accuracy, self.max_event_age)

    def test_basic_functionality(self):
        current_time = int(time.time())
        for i in range(1000):
            ts = current_time - random.randint(0, 59)
            self.ep.process_event(ts, i, random.uniform(0, 100))
        
        results = self.ep.get_percentiles(current_time)
        self.assertEqual(set(results.keys()), set(self.window_sizes))
        for window in self.window_sizes:
            self.assertEqual(set(results[window].keys()), set(self.percentiles))

    def test_out_of_order_events(self):
        current_time = int(time.time())
        timestamps = [current_time - i for i in range(100)]
        random.shuffle(timestamps)
        
        for i, ts in enumerate(timestamps):
            self.ep.process_event(ts, i, random.uniform(0, 100))
        
        results = self.ep.get_percentiles(current_time)
        for window in self.window_sizes:
            self.assertTrue(all(0 <= v <= 100 for v in results[window].values()))

    def test_old_events_discarded(self):
        current_time = int(time.time())
        very_old_time = current_time - self.max_event_age - 1
        self.ep.process_event(very_old_time, 1, 50.0)
        
        results = self.ep.get_percentiles(current_time)
        for window in self.window_sizes:
            for p in self.percentiles:
                self.assertNotEqual(results[window][p], 50.0)

    def test_thread_safety(self):
        import threading
        current_time = int(time.time())
        threads = []
        
        def worker():
            for i in range(100):
                ts = current_time - random.randint(0, 59)
                self.ep.process_event(ts, i, random.uniform(0, 100))
        
        for _ in range(10):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        results = self.ep.get_percentiles(current_time)
        self.assertEqual(set(results.keys()), set(self.window_sizes))

    def test_empty_windows(self):
        current_time = int(time.time())
        results = self.ep.get_percentiles(current_time)
        for window in self.window_sizes:
            for p in self.percentiles:
                self.assertTrue(results[window][p] is None or results[window][p] == 0)

    def test_accuracy_parameter(self):
        high_acc_ep = EventPercentiles([60], [0.5], 0.001, 3600)
        low_acc_ep = EventPercentiles([60], [0.5], 0.1, 3600)
        
        current_time = int(time.time())
        for i in range(10000):
            ts = current_time - random.randint(0, 59)
            val = random.uniform(0, 100)
            high_acc_ep.process_event(ts, i, val)
            low_acc_ep.process_event(ts, i, val)
        
        high_result = high_acc_ep.get_percentiles(current_time)[60][0.5]
        low_result = low_acc_ep.get_percentiles(current_time)[60][0.5]
        self.assertNotEqual(high_result, low_result)

if __name__ == '__main__':
    unittest.main()