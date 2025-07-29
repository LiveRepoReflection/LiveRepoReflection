import unittest
from unittest.mock import Mock, patch
import asyncio
from typing import List, Dict

class TestDistributedScheduler(unittest.TestCase):
    def setUp(self):
        # Mock function for task execution
        self.mock_function = Mock()
        self.mock_function.return_value = True

    def test_task_creation(self):
        """Test if tasks are created with correct attributes"""
        task_id = "task1"
        priority = 5
        cpu_needed = 2
        memory_needed = 1024
        max_cpu_needed = 4
        max_memory_needed = 2048

        with patch('distributed_scheduler.Task') as mock_task:
            mock_task.return_value.task_id = task_id
            mock_task.return_value.priority = priority
            mock_task.return_value.cpu_needed = cpu_needed
            mock_task.return_value.memory_needed = memory_needed
            mock_task.return_value.max_cpu_needed = max_cpu_needed
            mock_task.return_value.max_memory_needed = max_memory_needed

            task = mock_task(
                task_id=task_id,
                priority=priority,
                function=self.mock_function,
                cpu_needed=cpu_needed,
                memory_needed=memory_needed,
                max_cpu_needed=max_cpu_needed,
                max_memory_needed=max_memory_needed
            )

            self.assertEqual(task.task_id, task_id)
            self.assertEqual(task.priority, priority)
            self.assertEqual(task.cpu_needed, cpu_needed)
            self.assertEqual(task.memory_needed, memory_needed)
            self.assertEqual(task.max_cpu_needed, max_cpu_needed)
            self.assertEqual(task.max_memory_needed, max_memory_needed)

    def test_worker_node_creation(self):
        """Test if worker nodes are created with correct attributes"""
        with patch('distributed_scheduler.WorkerNode') as mock_worker:
            node_id = "worker1"
            total_cpu = 8
            total_memory = 16384

            mock_worker.return_value.node_id = node_id
            mock_worker.return_value.total_cpu = total_cpu
            mock_worker.return_value.total_memory = total_memory

            worker = mock_worker(
                node_id=node_id,
                total_cpu=total_cpu,
                total_memory=total_memory
            )

            self.assertEqual(worker.node_id, node_id)
            self.assertEqual(worker.total_cpu, total_cpu)
            self.assertEqual(worker.total_memory, total_memory)

    @patch('distributed_scheduler.Scheduler')
    def test_task_scheduling(self, mock_scheduler):
        """Test if tasks are scheduled correctly"""
        # Create mock tasks
        mock_tasks = [
            Mock(task_id=f"task{i}", priority=i, cpu_needed=1, memory_needed=1024)
            for i in range(3)
        ]

        # Create mock worker nodes
        mock_workers = [
            Mock(node_id=f"worker{i}", total_cpu=4, total_memory=8192, available_cpu=4, available_memory=8192)
            for i in range(2)
        ]

        scheduler = mock_scheduler()
        scheduler.schedule_tasks.return_value = True

        # Test scheduling
        result = scheduler.schedule_tasks(mock_tasks, mock_workers)
        self.assertTrue(result)
        scheduler.schedule_tasks.assert_called_once()

    @patch('distributed_scheduler.Scheduler')
    def test_task_prioritization(self, mock_scheduler):
        """Test if tasks are scheduled according to priority"""
        # Create mock tasks with different priorities
        mock_tasks = [
            Mock(task_id="task1", priority=1),
            Mock(task_id="task2", priority=3),
            Mock(task_id="task3", priority=2)
        ]

        scheduler = mock_scheduler()
        scheduler.get_next_task.return_value = mock_tasks[1]  # Should return highest priority task

        next_task = scheduler.get_next_task()
        self.assertEqual(next_task.task_id, "task2")
        self.assertEqual(next_task.priority, 3)

    @patch('distributed_scheduler.Scheduler')
    def test_resource_allocation(self, mock_scheduler):
        """Test if resources are allocated correctly"""
        scheduler = mock_scheduler()
        
        # Mock worker with limited resources
        mock_worker = Mock(
            total_cpu=4,
            total_memory=8192,
            available_cpu=4,
            available_memory=8192
        )

        # Mock task requiring resources
        mock_task = Mock(
            cpu_needed=2,
            memory_needed=4096
        )

        scheduler.allocate_resources.return_value = True
        result = scheduler.allocate_resources(mock_worker, mock_task)
        
        self.assertTrue(result)
        scheduler.allocate_resources.assert_called_once()

    @patch('distributed_scheduler.Scheduler')
    def test_fault_tolerance(self, mock_scheduler):
        """Test handling of worker node failures"""
        scheduler = mock_scheduler()
        
        # Mock failed task
        mock_task = Mock(task_id="failed_task", retry_count=0)
        
        scheduler.handle_node_failure.return_value = True
        result = scheduler.handle_node_failure("failed_worker_id", [mock_task])
        
        self.assertTrue(result)
        scheduler.handle_node_failure.assert_called_once()

    @patch('distributed_scheduler.Scheduler')
    def test_task_cancellation(self, mock_scheduler):
        """Test task cancellation handling"""
        scheduler = mock_scheduler()
        
        mock_task = Mock(task_id="task_to_cancel", status="running")
        
        scheduler.cancel_task.return_value = True
        result = scheduler.cancel_task(mock_task.task_id)
        
        self.assertTrue(result)
        scheduler.cancel_task.assert_called_once()

    @patch('distributed_scheduler.Scheduler')
    def test_deadlock_prevention(self, mock_scheduler):
        """Test deadlock prevention mechanism"""
        scheduler = mock_scheduler()
        
        # Create mock tasks with circular resource dependencies
        mock_tasks = [
            Mock(task_id="task1", required_resources=["resource1", "resource2"]),
            Mock(task_id="task2", required_resources=["resource2", "resource1"])
        ]
        
        scheduler.check_deadlock.return_value = False
        result = scheduler.check_deadlock(mock_tasks)
        
        self.assertFalse(result)
        scheduler.check_deadlock.assert_called_once()

    @patch('distributed_scheduler.Scheduler')
    def test_dynamic_resource_allocation(self, mock_scheduler):
        """Test dynamic resource allocation"""
        scheduler = mock_scheduler()
        
        mock_task = Mock(
            task_id="dynamic_task",
            cpu_needed=2,
            memory_needed=4096,
            max_cpu_needed=4,
            max_memory_needed=8192
        )
        
        scheduler.adjust_resources.return_value = True
        result = scheduler.adjust_resources(mock_task, cpu_delta=1, memory_delta=2048)
        
        self.assertTrue(result)
        scheduler.adjust_resources.assert_called_once()

    def test_task_status_tracking(self):
        """Test task status tracking"""
        with patch('distributed_scheduler.Scheduler') as mock_scheduler:
            scheduler = mock_scheduler()
            
            mock_task = Mock(task_id="tracked_task")
            scheduler.get_task_status.return_value = "running"
            
            status = scheduler.get_task_status(mock_task.task_id)
            self.assertEqual(status, "running")
            scheduler.get_task_status.assert_called_once()

if __name__ == '__main__':
    unittest.main()