import unittest
import importlib
import distributed_balancer

class DistributedBalancerTest(unittest.TestCase):
    def setUp(self):
        # Reload the module to reset state between tests
        importlib.reload(distributed_balancer)

    def test_no_workers_pending_tasks(self):
        # Test that tasks are queued when no workers are available.
        distributed_balancer.handle_event(("TASK", 5, "task1"))
        distributed_balancer.handle_event(("TASK", 1, "task2"))
        unprocessed = distributed_balancer.get_unprocessed_tasks()
        # Should be sorted by priority (1 then 5)
        self.assertEqual(unprocessed, ["task2", "task1"])
        # No worker should have tasks assigned
        self.assertEqual(distributed_balancer.get_worker_tasks("worker1"), [])

    def test_worker_join_assigns_new_tasks(self):
        # Join a worker, then submit tasks.
        distributed_balancer.handle_event(("WORKER_JOIN", "worker1"))
        distributed_balancer.handle_event(("TASK", 10, "taskA"))
        distributed_balancer.handle_event(("TASK", 2, "taskB"))
        # Both tasks should be assigned to worker1.
        tasks = distributed_balancer.get_worker_tasks("worker1")
        self.assertCountEqual(tasks, ["taskA", "taskB"])
        # No unprocessed tasks remain.
        self.assertEqual(distributed_balancer.get_unprocessed_tasks(), [])

    def test_pending_tasks_assignment_after_worker_join(self):
        # Submit tasks while no workers, then join a worker.
        distributed_balancer.handle_event(("TASK", 3, "task1"))
        distributed_balancer.handle_event(("TASK", 1, "task2"))
        self.assertEqual(distributed_balancer.get_unprocessed_tasks(), ["task2", "task1"])
        
        # Join a worker; assume system assigns pending tasks when possible.
        distributed_balancer.handle_event(("WORKER_JOIN", "worker1"))
        # Check that pending tasks have been assigned to worker1.
        worker_tasks = distributed_balancer.get_worker_tasks("worker1")
        # Depending on implementation, tasks could be immediately re-assigned.
        # We require that the unprocessed queue is empty and worker1 holds both tasks.
        self.assertCountEqual(worker_tasks, ["task2", "task1"])
        self.assertEqual(distributed_balancer.get_unprocessed_tasks(), [])

    def test_load_balancing_across_workers(self):
        # Join multiple workers.
        distributed_balancer.handle_event(("WORKER_JOIN", "worker1"))
        distributed_balancer.handle_event(("WORKER_JOIN", "worker2"))
        distributed_balancer.handle_event(("WORKER_JOIN", "worker3"))
        # Submit multiple tasks.
        tasks = [
            ("TASK", 5, "t1"),
            ("TASK", 3, "t2"),
            ("TASK", 7, "t3"),
            ("TASK", 1, "t4"),
            ("TASK", 4, "t5"),
            ("TASK", 6, "t6")
        ]
        for event in tasks:
            distributed_balancer.handle_event(event)
            
        # Check load balancing: the difference between counts across workers should be at most 1.
        loads = [len(distributed_balancer.get_worker_tasks(w)) for w in ["worker1", "worker2", "worker3"]]
        max_load = max(loads)
        min_load = min(loads)
        self.assertTrue(max_load - min_load <= 1)
        # Ensure that all tasks have been assigned.
        all_assigned = []
        for w in ["worker1", "worker2", "worker3"]:
            all_assigned.extend(distributed_balancer.get_worker_tasks(w))
        self.assertCountEqual(all_assigned, ["t1", "t2", "t3", "t4", "t5", "t6"])
        self.assertEqual(distributed_balancer.get_unprocessed_tasks(), [])

    def test_worker_leave_requeues_tasks(self):
        # Join two workers.
        distributed_balancer.handle_event(("WORKER_JOIN", "worker1"))
        distributed_balancer.handle_event(("WORKER_JOIN", "worker2"))
        # Assign tasks.
        distributed_balancer.handle_event(("TASK", 8, "alpha"))
        distributed_balancer.handle_event(("TASK", 4, "beta"))
        distributed_balancer.handle_event(("TASK", 2, "gamma"))
        distributed_balancer.handle_event(("TASK", 10, "delta"))
        
        # Confirm tasks are distributed between worker1 and worker2.
        tasks1 = distributed_balancer.get_worker_tasks("worker1")
        tasks2 = distributed_balancer.get_worker_tasks("worker2")
        self.assertEqual(len(tasks1) + len(tasks2), 4)

        # Simulate failure of worker1.
        distributed_balancer.handle_event(("WORKER_LEAVE", "worker1"))
        # The tasks assigned to worker1 should be re-queued and then assigned to an available worker or remain pending.
        # Here, we will check that worker1 has no tasks and that the tasks are in unprocessed or reassigned.
        self.assertEqual(distributed_balancer.get_worker_tasks("worker1"), [])
        
        # Depending on system design for rebalancing, tasks from worker1 might be re-assigned immediately.
        # To test, we check that the overall set of tasks is still complete.
        remaining_tasks = distributed_balancer.get_worker_tasks("worker2") + distributed_balancer.get_unprocessed_tasks()
        self.assertCountEqual(remaining_tasks, ["alpha", "beta", "gamma", "delta"])
        
        # Now, add a new worker and see if pending tasks from worker1 are re-assigned.
        distributed_balancer.handle_event(("WORKER_JOIN", "worker3"))
        # If there were pending tasks, they should now be assigned to worker3 to balance the load.
        tasks_worker3 = distributed_balancer.get_worker_tasks("worker3")
        # After rebalancing, there should be no pending tasks.
        self.assertEqual(distributed_balancer.get_unprocessed_tasks(), [])
        # The overall tasks should still match.
        total_tasks = (distributed_balancer.get_worker_tasks("worker2") +
                       distributed_balancer.get_worker_tasks("worker3"))
        self.assertCountEqual(total_tasks, ["alpha", "beta", "gamma", "delta"])

    def test_priority_order_in_unprocessed(self):
        # When multiple tasks with various priorities are pending, ensure they're sorted by priority.
        distributed_balancer.handle_event(("TASK", 20, "task_low"))
        distributed_balancer.handle_event(("TASK", 5, "task_high"))
        distributed_balancer.handle_event(("TASK", 10, "task_mid"))
        # No workers are added, so tasks remain unprocessed.
        unprocessed = distributed_balancer.get_unprocessed_tasks()
        self.assertEqual(unprocessed, ["task_high", "task_mid", "task_low"])

if __name__ == "__main__":
    unittest.main()