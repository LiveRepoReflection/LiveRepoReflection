import unittest
from pipeline_time import min_total_time

class PipelineTimeTest(unittest.TestCase):

    def test_no_tasks(self):
        tasks = []
        dependencies = {}
        processing_times = {}
        num_workers = 3
        self.assertEqual(min_total_time(tasks, dependencies, processing_times, num_workers), 0)
        
    def test_no_dependencies_workers_equal_tasks(self):
        tasks = [1, 2, 3]
        dependencies = {1: [], 2: [], 3: []}
        processing_times = {1: 3, 2: 3, 3: 3}
        num_workers = 3
        # All tasks run concurrently, so the total time equals the max processing time.
        self.assertEqual(min_total_time(tasks, dependencies, processing_times, num_workers), 3)
        
    def test_no_dependencies_workers_less_than_tasks(self):
        tasks = [1, 2, 3, 4]
        dependencies = {1: [], 2: [], 3: [], 4: []}
        processing_times = {1: 4, 2: 4, 3: 4, 4: 4}
        num_workers = 2
        # Total work = 16 units with 2 workers, so optimal scheduling gives 8 units.
        # Here, any optimal scheduler would nearly balance the load.
        self.assertEqual(min_total_time(tasks, dependencies, processing_times, num_workers), 8)
        
    def test_chain_dependencies(self):
        # Tasks must be processed sequentially because each depends on the previous.
        tasks = [1, 2, 3]
        dependencies = {1: [], 2: [1], 3: [2]}
        processing_times = {1: 5, 2: 3, 3: 7}
        num_workers = 3  # Although workers are sufficient, dependencies enforce sequential processing.
        self.assertEqual(min_total_time(tasks, dependencies, processing_times, num_workers), 15)
        
    def test_branching_dependencies(self):
        # Task graph:
        # 1, 2 -> both independent initially.
        # 3 depends on 1 and 2.
        # 4 depends on 2.
        # 5 depends on 3 and 4.
        tasks = [1, 2, 3, 4, 5]
        dependencies = {
            1: [],
            2: [],
            3: [1, 2],
            4: [2],
            5: [3, 4]
        }
        processing_times = {
            1: 2,
            2: 3,
            3: 4,
            4: 4,
            5: 5
        }
        num_workers = 2
        # Expected scheduling:
        # Time 0: start tasks 1 and 2.
        # Time 2: task 1 completes (task 2 still running).
        # Time 3: task 2 completes; tasks 3 and 4 become available.
        # Time 3 to 7: tasks 3 and 4 process concurrently.
        # Time 7: task 5 becomes available and runs until time 12.
        self.assertEqual(min_total_time(tasks, dependencies, processing_times, num_workers), 12)
        
    def test_large_number_of_workers(self):
        # When workers are abundant, the total time should be the time taken by the longest dependency chain.
        tasks = [1, 2, 3, 4, 5]
        dependencies = {
            1: [],      # start
            2: [1],
            3: [2],
            4: [3],
            5: [4]
        }
        processing_times = {
            1: 2,
            2: 2,
            3: 2,
            4: 2,
            5: 2
        }
        num_workers = 10
        # The chain forces sequential execution regardless of available workers.
        self.assertEqual(min_total_time(tasks, dependencies, processing_times, num_workers), 10)
        
    def test_independent_tasks_varying_processing(self):
        # Tasks with no dependencies, varying processing times with limited workers.
        tasks = [1, 2, 3, 4, 5]
        dependencies = {task: [] for task in tasks}
        processing_times = {
            1: 1,
            2: 2,
            3: 3,
            4: 4,
            5: 5
        }
        num_workers = 2
        # Total processing time = 15; optimal schedule may yield 9 time units if tasks are balanced right.
        # One optimal scheduling:
        # Worker1: 5 + 3 + 1 = 9; Worker2: 4 + 2 = 6; max = 9.
        self.assertEqual(min_total_time(tasks, dependencies, processing_times, num_workers), 9)
        
    def test_complex_graph(self):
        # A slightly more complex graph involving multiple chains and convergences.
        tasks = [1, 2, 3, 4, 5, 6, 7]
        dependencies = {
            1: [],
            2: [],
            3: [1],
            4: [1],
            5: [2, 3],
            6: [3, 4],
            7: [5, 6]
        }
        processing_times = {
            1: 3,
            2: 2,
            3: 4,
            4: 6,
            5: 5,
            6: 1,
            7: 2
        }
        num_workers = 3
        # A possible optimal schedule:
        # Time 0: Start tasks 1 (3) and 2 (2) [Worker3 idle].
        # Time 2: Task 2 finishes.
        # Time 3: Task 1 finishes; now tasks 3 and 4 become available.
        # Time 3: Start tasks 3 (4) and 4 (6) using Worker from task1 and the idle worker.
        # Time 7: Task 3 finishes; now task 5 depends on tasks 2 and 3 becomes available.
        # Time 7: Assign task 5 (5) to available worker.
        # Time 9: Task 4 still processing, one worker idle.
        # Time 9: Task 6 becomes available (depends on 3 and 4, but 4 still in progress, so wait until 9? Actually task4 ends at 9 if started at 3, 6 time units).
        # Time 9: Now start task 6 (1) along with task 5 in progress.
        # Time 10: Task 6 finishes. Task 7 (depends on 5 and 6) starts.
        # Task 5 finishes at time 12 and task 7 (2) finishes at 14.
        # Expected total time is 14.
        self.assertEqual(min_total_time(tasks, dependencies, processing_times, num_workers), 14)

if __name__ == '__main__':
    unittest.main()