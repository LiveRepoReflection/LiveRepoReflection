import threading
import time
from collections import defaultdict, deque

class TaskScheduler:
    def __init__(self, scheduling_algo="fcfs"):
        self.lock = threading.Lock()
        self.scheduling_algo = scheduling_algo  # "fcfs", "priority", "sjf"
        self.tasks = {}  # task_id -> task_info dict with additional metadata
        self.task_dependencies = defaultdict(list)  # task_id -> list of dependent task_ids
        self.dependency_count = {}  # task_id -> number of unresolved dependencies
        self.submission_order = {}  # task_id -> submission counter
        self._submission_counter = 0

        self.workers = {}  # worker_id -> status dict
        self.assignments = {}  # task_id -> worker_id
        self.task_status = {}  # task_id -> "pending", "running", "completed"
        self.task_start_time = {}  # task_id -> start time

    def reset(self):
        with self.lock:
            self.tasks.clear()
            self.task_dependencies.clear()
            self.dependency_count.clear()
            self.submission_order.clear()
            self._submission_counter = 0
            self.assignments.clear()
            self.task_status.clear()
            self.task_start_time.clear()
            # Workers are left intact

    def submit_task(self, task):
        # Validate required fields
        required_fields = ["task_id", "command", "resources", "dependencies", "priority", "max_time"]
        for field in required_fields:
            if field not in task:
                raise ValueError("Invalid task submission: Missing field '{}'".format(field))
        task_id = task["task_id"]
        with self.lock:
            if task_id in self.tasks:
                raise ValueError("Task with id '{}' already exists".format(task_id))
            self.tasks[task_id] = task.copy()
            self.task_status[task_id] = "pending"
            self.submission_order[task_id] = self._submission_counter
            self._submission_counter += 1
            # Initialize dependency count for the task
            dependencies = task.get("dependencies", [])
            self.dependency_count[task_id] = len(dependencies)
            # For each dependency, add this task as a dependent
            for dep in dependencies:
                self.task_dependencies[dep].append(task_id)
        return task_id

    def get_all_tasks(self):
        with self.lock:
            return list(self.tasks.keys())

    def set_scheduling_algo(self, algo):
        if algo not in ["fcfs", "priority", "sjf"]:
            raise ValueError("Invalid scheduling algorithm: {}".format(algo))
        with self.lock:
            self.scheduling_algo = algo

    def register_worker(self, worker_id, status):
        with self.lock:
            self.workers[worker_id] = status.copy()

    def get_worker_status(self, worker_id):
        with self.lock:
            if worker_id in self.workers:
                return self.workers[worker_id].copy()
            else:
                return None

    def schedule_tasks(self):
        with self.lock:
            # Create a copy of dependency count since we'll modify it during topological sort
            local_dep_count = self.dependency_count.copy()
            # Build initial queue: tasks with no unmet dependencies
            queue = []
            for task_id, count in local_dep_count.items():
                if count == 0:
                    queue.append(task_id)

            # Apply scheduling algorithm ordering on the initial queue
            queue = self._sort_tasks(queue)
            scheduled_order = []
            visited = set()

            while queue:
                current = queue.pop(0)  # pop first element as per sorted order
                scheduled_order.append(current)
                visited.add(current)
                # For each task depending on current, decrement dependency count
                for dependent in self.task_dependencies.get(current, []):
                    if dependent in local_dep_count:
                        local_dep_count[dependent] -= 1
                        if local_dep_count[dependent] == 0:
                            queue.append(dependent)
                # Re-sort the queue at each iteration according to scheduling algorithm
                queue = self._sort_tasks(queue)

            if len(scheduled_order) != len(self.tasks):
                raise ValueError("Cycle detected or unresolved dependencies exist among tasks")
            # After ordering, assign tasks to available workers using round-robin
            worker_ids = list(self.workers.keys())
            if worker_ids:
                assignment = {}
                idx = 0
                for task_id in scheduled_order:
                    assignment[task_id] = worker_ids[idx % len(worker_ids)]
                    idx += 1
                self.assignments = assignment
            else:
                self.assignments = {}
            return scheduled_order

    def _sort_tasks(self, tasks_list):
        # Sort tasks based on the current scheduling algorithm
        if self.scheduling_algo == "fcfs":
            # Use submission order (lower submission counter first)
            return sorted(tasks_list, key=lambda tid: self.submission_order.get(tid, 0))
        elif self.scheduling_algo == "priority":
            # Higher priority first, tie break with submission order
            return sorted(tasks_list, key=lambda tid: (-self.tasks[tid]["priority"], self.submission_order.get(tid, 0)))
        elif self.scheduling_algo == "sjf":
            # Shortest job first based on max_time, tie break with submission order
            return sorted(tasks_list, key=lambda tid: (self.tasks[tid]["max_time"], self.submission_order.get(tid, 0)))
        else:
            return tasks_list

    def get_task_assignment(self, task_id):
        with self.lock:
            return self.assignments.get(task_id, None)

    def simulate_worker_failure(self, worker_id):
        with self.lock:
            if worker_id not in self.workers:
                return
            # Remove the failed worker
            del self.workers[worker_id]
            # Reassign tasks that were assigned to the failed worker
            available_workers = list(self.workers.keys())
            for task_id, assigned_worker in self.assignments.items():
                if assigned_worker == worker_id:
                    if available_workers:
                        # Reassign using round-robin: pick the first available worker
                        self.assignments[task_id] = available_workers[0]
                    else:
                        self.assignments[task_id] = None

    def start_task(self, task_id):
        with self.lock:
            if task_id not in self.tasks:
                raise ValueError("Task not found: {}".format(task_id))
            # Mark the task as running and set start time
            self.task_status[task_id] = "running"
            self.task_start_time[task_id] = time.time()
            return True

    def monitor_task(self, task_id):
        with self.lock:
            if task_id not in self.tasks:
                raise ValueError("Task not found: {}".format(task_id))
            # Simulate progress monitoring: if running, compute progress based on elapsed time
            status = self.task_status.get(task_id, "pending")
            progress = 0
            if status == "running":
                start = self.task_start_time.get(task_id, time.time())
                elapsed = time.time() - start
                max_time = self.tasks[task_id]["max_time"]
                progress = min(100, int((elapsed / max_time) * 100))
            elif status == "completed":
                progress = 100
            return {"task_id": task_id, "status": status, "progress": progress}

# For backward compatibility with unit tests that import task_cluster.TaskScheduler as task_cluster
TaskScheduler = TaskScheduler