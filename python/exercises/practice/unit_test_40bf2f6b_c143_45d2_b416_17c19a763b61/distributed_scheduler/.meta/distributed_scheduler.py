import asyncio
import heapq
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Callable, Optional, Set
import time
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class Task:
    task_id: str
    priority: int
    function: Callable
    cpu_needed: int
    memory_needed: int
    max_cpu_needed: int
    max_memory_needed: int
    status: TaskStatus = TaskStatus.PENDING
    retry_count: int = 0
    max_retries: int = 3
    worker_id: Optional[str] = None
    
    def __lt__(self, other):
        return self.priority > other.priority  # Higher priority first

class WorkerNode:
    def __init__(self, node_id: str, total_cpu: int, total_memory: int):
        self.node_id = node_id
        self.total_cpu = total_cpu
        self.total_memory = total_memory
        self.available_cpu = total_cpu
        self.available_memory = total_memory
        self.tasks: Set[str] = set()
        self.last_heartbeat = time.time()
        self.status = "active"

    def can_accommodate(self, task: Task) -> bool:
        return (self.available_cpu >= task.cpu_needed and 
                self.available_memory >= task.memory_needed)

    def allocate_resources(self, task: Task) -> bool:
        if self.can_accommodate(task):
            self.available_cpu -= task.cpu_needed
            self.available_memory -= task.memory_needed
            self.tasks.add(task.task_id)
            return True
        return False

    def release_resources(self, task: Task):
        if task.task_id in self.tasks:
            self.available_cpu += task.cpu_needed
            self.available_memory += task.memory_needed
            self.tasks.remove(task.task_id)

class ResourceManager:
    def __init__(self):
        self.resource_locks = {}
        self.resource_waiters = defaultdict(list)
        
    async def acquire_resources(self, task: Task, worker: WorkerNode) -> bool:
        resources = [f"cpu_{worker.node_id}", f"memory_{worker.node_id}"]
        
        # Check for potential deadlock
        if self._would_cause_deadlock(task.task_id, resources):
            return False
            
        # Try to acquire all resources
        for resource in resources:
            if resource in self.resource_locks:
                self.resource_waiters[resource].append(task.task_id)
                return False
                
        # Allocate resources
        for resource in resources:
            self.resource_locks[resource] = task.task_id
            
        return True

    def release_resources(self, task: Task, worker: WorkerNode):
        resources = [f"cpu_{worker.node_id}", f"memory_{worker.node_id}"]
        for resource in resources:
            if resource in self.resource_locks and self.resource_locks[resource] == task.task_id:
                del self.resource_locks[resource]
                
                # Wake up waiting tasks
                if resource in self.resource_waiters:
                    self.resource_waiters[resource].pop(0)

    def _would_cause_deadlock(self, task_id: str, requested_resources: List[str]) -> bool:
        # Simple cycle detection in resource allocation graph
        visited = set()
        
        def has_cycle(current_task: str) -> bool:
            if current_task in visited:
                return True
            visited.add(current_task)
            
            for resource in requested_resources:
                if resource in self.resource_locks:
                    owner = self.resource_locks[resource]
                    if owner != current_task and has_cycle(owner):
                        return True
            
            visited.remove(current_task)
            return False
            
        return has_cycle(task_id)

class Scheduler:
    def __init__(self):
        self.tasks: List[Task] = []
        self.workers: Dict[str, WorkerNode] = {}
        self.resource_manager = ResourceManager()
        self.task_map: Dict[str, Task] = {}
        self.heartbeat_timeout = 30  # seconds

    def add_task(self, task: Task):
        heapq.heappush(self.tasks, task)
        self.task_map[task.task_id] = task

    def add_worker(self, worker: WorkerNode):
        self.workers[worker.worker_id] = worker

    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        return self.task_map.get(task_id).status if task_id in self.task_map else None

    async def run(self):
        while True:
            await self._schedule_tasks()
            await self._check_worker_health()
            await asyncio.sleep(1)

    async def _schedule_tasks(self):
        if not self.tasks:
            return

        for worker in self.workers.values():
            if worker.status != "active":
                continue

            while self.tasks:
                task = heapq.heappop(self.tasks)
                
                if task.status == TaskStatus.CANCELLED:
                    continue

                if worker.can_accommodate(task):
                    if await self.resource_manager.acquire_resources(task, worker):
                        await self._execute_task(task, worker)
                    else:
                        heapq.heappush(self.tasks, task)
                else:
                    heapq.heappush(self.tasks, task)
                    break

    async def _execute_task(self, task: Task, worker: WorkerNode):
        task.status = TaskStatus.RUNNING
        task.worker_id = worker.node_id
        worker.allocate_resources(task)

        try:
            await asyncio.get_event_loop().run_in_executor(None, task.function)
            task.status = TaskStatus.COMPLETED
        except Exception as e:
            logger.error(f"Task {task.task_id} failed: {str(e)}")
            task.status = TaskStatus.FAILED
            
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.PENDING
                heapq.heappush(self.tasks, task)
        finally:
            worker.release_resources(task)
            self.resource_manager.release_resources(task, worker)

    async def _check_worker_health(self):
        current_time = time.time()
        for worker_id, worker in self.workers.items():
            if (current_time - worker.last_heartbeat > self.heartbeat_timeout and 
                worker.status == "active"):
                await self._handle_worker_failure(worker_id)

    async def _handle_worker_failure(self, worker_id: str):
        worker = self.workers[worker_id]
        worker.status = "failed"
        
        # Requeue tasks from failed worker
        for task_id in worker.tasks:
            task = self.task_map[task_id]
            task.status = TaskStatus.PENDING
            task.worker_id = None
            heapq.heappush(self.tasks, task)

        # Clear worker's state
        worker.tasks.clear()
        worker.available_cpu = worker.total_cpu
        worker.available_memory = worker.total_memory

    async def cancel_task(self, task_id: str) -> bool:
        if task_id not in self.task_map:
            return False

        task = self.task_map[task_id]
        task.status = TaskStatus.CANCELLED

        if task.worker_id:
            worker = self.workers[task.worker_id]
            worker.release_resources(task)
            self.resource_manager.release_resources(task, worker)

        return True

    def adjust_resources(self, task_id: str, cpu_delta: int, memory_delta: int) -> bool:
        if task_id not in self.task_map:
            return False

        task = self.task_map[task_id]
        if task.status != TaskStatus.RUNNING or not task.worker_id:
            return False

        worker = self.workers[task.worker_id]
        new_cpu = task.cpu_needed + cpu_delta
        new_memory = task.memory_needed + memory_delta

        if (new_cpu <= task.max_cpu_needed and 
            new_memory <= task.max_memory_needed and
            worker.available_cpu + task.cpu_needed >= new_cpu and
            worker.available_memory + task.memory_needed >= new_memory):
            
            worker.available_cpu += task.cpu_needed - new_cpu
            worker.available_memory += task.memory_needed - new_memory
            task.cpu_needed = new_cpu
            task.memory_needed = new_memory
            return True

        return False