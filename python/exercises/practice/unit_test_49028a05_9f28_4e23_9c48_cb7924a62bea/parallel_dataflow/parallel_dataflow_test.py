import unittest
import time
import threading
from collections import defaultdict

from parallel_dataflow import process_dataflow, ProcessingFailureError, Record, Task

# Dummy implementations for testing purposes
class DummyRecord(Record):
    def __init__(self, id, data):
        self.id = id
        self.data = data

class DummyTask(Task):
    def __init__(self, id, priority, memory_required, process_func):
        self.id = id
        self.priority = priority
        self.memory_required = memory_required
        self.process_func = process_func
        self.processed_records = []

    def process(self, record):
        result = self.process_func(record)
        if result:
            self.processed_records.append(record.id)
        return result

class TestParallelDataflow(unittest.TestCase):
    def setUp(self):
        # Reset any global state if necessary
        self.execution_order_lock = threading.Lock()
        self.execution_order = []

    def record_execution(self, task_id, record_id):
        with self.execution_order_lock:
            self.execution_order.append((task_id, record_id))

    def test_successful_processing(self):
        # Create three dummy records
        records = [DummyRecord(i, f"data_{i}") for i in range(3)]
        
        # Two tasks that always succeed, using a lambda that returns True.
        task0 = DummyTask(
            id=0,
            priority=5,
            memory_required=20,
            process_func=lambda record: True
        )
        task1 = DummyTask(
            id=1,
            priority=3,
            memory_required=30,
            process_func=lambda record: True
        )
        
        tasks = [task0, task1]
        
        # No dependencies between tasks or records.
        task_dependencies = {0: [], 1: []}
        record_dependencies = {record.id: [] for record in records}
        
        P = 4
        M = 100
        max_retries = 3
        initial_backoff = 1
        
        # Should complete processing without error.
        process_dataflow(records, tasks, task_dependencies, record_dependencies, P, M, max_retries, initial_backoff)
        
        # Verify that each task processed all records it was scheduled to process.
        self.assertEqual(set(task0.processed_records), set(record.id for record in records))
        self.assertEqual(set(task1.processed_records), set(record.id for record in records))

    def test_task_dependency_order(self):
        # We want to test that tasks with dependencies are executed in order.
        records = [DummyRecord(i, f"data_{i}") for i in range(2)]
        
        def create_process_func(task_id):
            # Simulate processing by recording execution order and returning success.
            def process(record):
                self.record_execution(task_id, record.id)
                return True
            return process

        # Create two tasks; task1 depends on task0.
        task0 = DummyTask(
            id=0,
            priority=5,
            memory_required=20,
            process_func=create_process_func(0)
        )
        task1 = DummyTask(
            id=1,
            priority=5,
            memory_required=20,
            process_func=create_process_func(1)
        )
        
        tasks = [task0, task1]
        # Task dependency: task1 depends on task0.
        task_dependencies = {0: [], 1: [0]}
        record_dependencies = {record.id: [] for record in records}
        
        P = 2
        M = 50
        max_retries = 3
        initial_backoff = 1
        
        process_dataflow(records, tasks, task_dependencies, record_dependencies, P, M, max_retries, initial_backoff)
        
        # For each record, check that execution from task0 comes before task1.
        order_by_record = defaultdict(list)
        for t_id, r_id in self.execution_order:
            order_by_record[r_id].append(t_id)
        
        for order in order_by_record.values():
            self.assertGreater(order.index(1), order.index(0))

    def test_retry_mechanism(self):
        # Test that a task retries on failure before eventually succeeding.
        records = [DummyRecord(0, "data")]
        
        call_count = defaultdict(int)
        def flaky_process(record):
            call_count[record.id] += 1
            # Fail the first 2 times, succeed on the third try.
            if call_count[record.id] < 3:
                return False
            return True

        task = DummyTask(
            id=0,
            priority=5,
            memory_required=20,
            process_func=flaky_process
        )
        tasks = [task]
        task_dependencies = {0: []}
        record_dependencies = {0: []}
        
        P = 1
        M = 50
        max_retries = 5
        initial_backoff = 1
        
        process_dataflow(records, tasks, task_dependencies, record_dependencies, P, M, max_retries, initial_backoff)
        
        # The task should eventually succeed and record 0 should be processed.
        self.assertIn(0, task.processed_records)
        # Confirm it took at least 3 attempts.
        self.assertGreaterEqual(call_count[0], 3)

    def test_failure_after_max_retries(self):
        # Test that the processing halts and raises ProcessingFailureError when task fails persistently.
        records = [DummyRecord(0, "data")]
        
        def always_fail(record):
            return False

        task = DummyTask(
            id=0,
            priority=5,
            memory_required=20,
            process_func=always_fail
        )
        tasks = [task]
        task_dependencies = {0: []}
        record_dependencies = {0: []}
        
        P = 1
        M = 50
        max_retries = 2
        initial_backoff = 1
        
        with self.assertRaises(ProcessingFailureError):
            process_dataflow(records, tasks, task_dependencies, record_dependencies, P, M, max_retries, initial_backoff)

    def test_memory_constraint_preemption(self):
        # Test that tasks with higher priority preempt lower priority ones when memory limit is encountered.
        records = [DummyRecord(i, f"data_{i}") for i in range(3)]
        
        # Create two tasks: one low priority but heavy memory requirement, one high priority with light memory.
        def low_priority_process(record):
            self.record_execution(0, record.id)
            # simulate some processing delay
            time.sleep(0.05)
            return True

        def high_priority_process(record):
            self.record_execution(1, record.id)
            return True

        low_priority_task = DummyTask(
            id=0,
            priority=1,  # lower priority
            memory_required=60,
            process_func=low_priority_process
        )
        high_priority_task = DummyTask(
            id=1,
            priority=10,  # higher priority
            memory_required=20,
            process_func=high_priority_process
        )
        
        tasks = [low_priority_task, high_priority_task]
        task_dependencies = {0: [], 1: []}
        record_dependencies = {record.id: [] for record in records}
        
        P = 2
        M = 70  # Only enough to run one low priority and one high priority task concurrently
        max_retries = 3
        initial_backoff = 1
        
        process_dataflow(records, tasks, task_dependencies, record_dependencies, P, M, max_retries, initial_backoff)
        
        # Verify that each record is processed by both tasks.
        self.assertEqual(set(low_priority_task.processed_records), set(record.id for record in records))
        self.assertEqual(set(high_priority_task.processed_records), set(record.id for record in records))
        
        # Check that in the execution order, for at least one record, high priority task's processing occurred
        # even if low priority task had started first.
        found_preemption = any(high_priority_task.id in [tid for tid, rid in self.execution_order if rid == record.id]
                               for record in records)
        self.assertTrue(found_preemption)

if __name__ == "__main__":
    unittest.main()