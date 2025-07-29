import unittest
from parallel_process import distribute_data, process_data, recover_from_failure, aggregate_results

class ParallelProcessTest(unittest.TestCase):
    
    def test_distribute_data_small(self):
        # Test with small dataset and few workers
        N, K = 10, 2
        distribution = distribute_data(N, K)
        
        # Check format of returned data
        self.assertIsInstance(distribution, list)
        for segment in distribution:
            self.assertIsInstance(segment, tuple)
            self.assertEqual(len(segment), 3)
        
        # Check that all records are covered exactly once
        covered_indices = set()
        for start, end, worker_id in distribution:
            self.assertGreaterEqual(worker_id, 0)
            self.assertLess(worker_id, K)
            self.assertGreaterEqual(start, 0)
            self.assertLess(end, N)
            self.assertGreaterEqual(end, start)
            for i in range(start, end + 1):
                self.assertNotIn(i, covered_indices, "Index assigned to multiple workers")
                covered_indices.add(i)
        
        self.assertEqual(len(covered_indices), N, "Not all indices were covered")
    
    def test_distribute_data_large(self):
        # Test with larger dataset
        N, K = 1000, 10
        distribution = distribute_data(N, K)
        
        # Check that all workers have reasonable workload
        worker_loads = {}
        for start, end, worker_id in distribution:
            load = end - start + 1
            if worker_id in worker_loads:
                worker_loads[worker_id] += load
            else:
                worker_loads[worker_id] = load
        
        # Check that load is reasonably balanced (no worker has more than twice the average load)
        avg_load = N / K
        for worker_id, load in worker_loads.items():
            self.assertLessEqual(load, 2 * avg_load, 
                                 f"Worker {worker_id} has an excessive workload")
    
    def test_process_data(self):
        # Test data processing function with different segments
        segment1 = (0, 5)
        result1 = process_data(segment1)
        # Expected sum of indices 0+1+2+3+4+5 = 15
        self.assertEqual(result1, 15)
        
        segment2 = (10, 15)
        result2 = process_data(segment2)
        # Expected sum of indices 10+11+12+13+14+15 = 75
        self.assertEqual(result2, 75)
    
    def test_recover_from_failure(self):
        N, K = 20, 4
        initial_distribution = distribute_data(N, K)
        
        # Simulate failure of worker 1
        failed_worker_id = 1
        new_distribution = recover_from_failure(failed_worker_id, N, K)
        
        # Check that the new distribution is valid
        self.assertIsInstance(new_distribution, list)
        for segment in new_distribution:
            self.assertIsInstance(segment, tuple)
            self.assertEqual(len(segment), 3)
        
        # Check that all records are covered
        covered_indices = set()
        for start, end, worker_id in new_distribution:
            self.assertGreaterEqual(worker_id, 0)
            self.assertLess(worker_id, K)
            self.assertNotEqual(worker_id, failed_worker_id) # Failed worker shouldn't be assigned work
            self.assertGreaterEqual(start, 0)
            self.assertLess(end, N)
            self.assertGreaterEqual(end, start)
            for i in range(start, end + 1):
                covered_indices.add(i)
        
        self.assertEqual(len(covered_indices), N, "Not all indices were covered after recovery")
        
        # Check that the workload of the failed worker is properly redistributed
        failed_segments = [seg for seg in initial_distribution if seg[2] == failed_worker_id]
        failed_indices = set()
        for start, end, _ in failed_segments:
            for i in range(start, end + 1):
                failed_indices.add(i)
        
        for idx in failed_indices:
            self.assertIn(idx, covered_indices, 
                          f"Index {idx} from failed worker not reassigned")
    
    def test_aggregate_results(self):
        # Test aggregation with simple results
        worker_results = [10, 20, 30, 40]
        total = aggregate_results(worker_results)
        self.assertEqual(total, 100)
        
        # Test with empty list
        self.assertEqual(aggregate_results([]), 0)
        
        # Test with single result
        self.assertEqual(aggregate_results([42]), 42)
    
    def test_end_to_end_no_failure(self):
        # Test the entire workflow without failures
        N, K = 100, 5
        distribution = distribute_data(N, K)
        
        worker_results = []
        for start, end, _ in distribution:
            result = process_data((start, end))
            worker_results.append(result)
        
        total = aggregate_results(worker_results)
        # Expected sum of indices 0+1+2+...+99 = 4950
        self.assertEqual(total, 4950)
    
    def test_end_to_end_with_failure(self):
        # Test the entire workflow with a failure
        N, K = 100, 5
        initial_distribution = distribute_data(N, K)
        
        # Process some segments
        processed_segments = set()
        worker_results = []
        
        for i, (start, end, worker_id) in enumerate(initial_distribution):
            if worker_id != 2:  # Assume worker 2 completes its work
                result = process_data((start, end))
                worker_results.append(result)
                for idx in range(start, end + 1):
                    processed_segments.add(idx)
        
        # Simulate failure of worker 2
        failed_worker_id = 2
        new_distribution = recover_from_failure(failed_worker_id, N, K)
        
        # Process the redistributed segments
        for start, end, worker_id in new_distribution:
            # Only process segments that weren't already processed
            unprocessed_indices = [idx for idx in range(start, end + 1) 
                                   if idx not in processed_segments]
            if unprocessed_indices:
                min_idx = min(unprocessed_indices)
                max_idx = max(unprocessed_indices)
                result = process_data((min_idx, max_idx))
                # Adjust result to account for only summing unprocessed indices
                adjusted_result = 0
                for idx in unprocessed_indices:
                    adjusted_result += idx
                worker_results.append(adjusted_result)
                for idx in unprocessed_indices:
                    processed_segments.add(idx)
        
        total = aggregate_results(worker_results)
        # Expected sum of indices 0+1+2+...+99 = 4950
        self.assertEqual(total, 4950)
        self.assertEqual(len(processed_segments), N, "Not all segments were processed")

if __name__ == '__main__':
    unittest.main()