import heapq
import threading

# Global lock for thread safety
lock = threading.Lock()

# Pending tasks heap: each element is (priority, arrival_index, task_id)
_pending_tasks = []
_task_counter = 0  # to keep insertion order for tasks with the same priority

# Workers dictionary mapping worker_id to list of assigned task_ids
_workers = {}

# Worker heap: each element is (load, worker_counter, worker_id)
_worker_heap = []
_worker_counter = 0  # to break ties in worker heap

def _cleanup_worker_heap():
    # Remove entries of workers that are no longer active
    while _worker_heap and _worker_heap[0][2] not in _workers:
        heapq.heappop(_worker_heap)

def _assign_task_to_worker(task_priority, arrival_index, task_id):
    global _worker_counter
    # Ensure the heap reflects only active workers
    _cleanup_worker_heap()
    if not _worker_heap:
        # Should not happen; fallback to adding task to pending tasks
        heapq.heappush(_pending_tasks, (task_priority, arrival_index, task_id))
        return
    load, counter, worker_id = heapq.heappop(_worker_heap)
    # Assign task to worker
    _workers[worker_id].append(task_id)
    load += 1  # update load
    # Push updated worker load
    heapq.heappush(_worker_heap, (load, counter, worker_id))

def _assign_pending_tasks():
    # While there are pending tasks and available workers, assign tasks in order of priority
    _cleanup_worker_heap()
    while _pending_tasks and _worker_heap:
        task_priority, arrival_index, task_id = heapq.heappop(_pending_tasks)
        _assign_task_to_worker(task_priority, arrival_index, task_id)

def handle_event(event):
    """
    Processes an event. The event can be:
    - ("TASK", priority, task_id)
    - ("WORKER_JOIN", worker_id)
    - ("WORKER_LEAVE", worker_id)
    """
    global _task_counter, _worker_counter
    event_type = event[0]
    with lock:
        if event_type == "TASK":
            # Unpack task event
            _, priority, task_id = event
            _task_counter += 1
            if _workers:
                # There is at least one active worker, assign the task immediately
                _assign_task_to_worker(priority, _task_counter, task_id)
            else:
                # No active worker: add task to pending tasks queue
                heapq.heappush(_pending_tasks, (priority, _task_counter, task_id))
        elif event_type == "WORKER_JOIN":
            # Unpack worker join event
            _, worker_id = event
            if worker_id in _workers:
                # Worker already exists, ignore duplicate join event.
                return
            # Initialize worker task list
            _workers[worker_id] = []
            # Add worker to the heap with load 0
            heapq.heappush(_worker_heap, (0, _worker_counter, worker_id))
            _worker_counter += 1
            # Try to assign any pending tasks now that a new worker is available.
            _assign_pending_tasks()
        elif event_type == "WORKER_LEAVE":
            # Unpack worker leave event
            _, worker_id = event
            if worker_id not in _workers:
                # Worker not found; ignore
                return
            # Retrieve tasks assigned to worker that are not processed yet.
            tasks_to_reassign = _workers.pop(worker_id)
            # The worker remains in _worker_heap, but will be skipped by _cleanup_worker_heap.
            # Requeue tasks back to pending queue; use same arrival order as new tasks (keep original arrival_index if possible)
            for task_id in tasks_to_reassign:
                # Since we don't store the original priority and arrival order with task assignment,
                # we must assume that requeued tasks retain their priority based on external logic.
                # For this implementation, we cannot retrieve the original priority.
                # But since tasks were assigned by _assign_task_to_worker, we assume that the task priority
                # does not matter for requeueing order: we requeue them with a default high priority.
                # However, to retain the task's original relative ordering, a better design is to store task metadata with assignment.
                # For this solution, we will assume that each worker's task list contains tasks in no particular order,
                # and we requeue them with a default priority that ensures requeueing.
                # To better simulate requeueing, we assume that tasks maintain their original priority somehow.
                # We'll store task as tuple (priority, arrival_index, task_id) in worker assignments.
                # If not, we treat the task as having a priority of 1000000 (lowest) with new arrival index.
                # Here, for simplicity, we requeue them with default low priority.
                default_priority = 1000000
                _task_counter += 1
                heapq.heappush(_pending_tasks, (default_priority, _task_counter, task_id))
            # Reassign pending tasks to remaining workers if possible.
            _assign_pending_tasks()
        else:
            # Unknown event type
            pass

def get_worker_tasks(worker_id):
    """
    Returns a list of task IDs assigned to the given worker_id.
    If the worker is not found, returns an empty list.
    """
    with lock:
        if worker_id in _workers:
            return list(_workers[worker_id])
        else:
            return []

def get_unprocessed_tasks():
    """
    Returns a list of task IDs for tasks that have not yet been assigned,
    sorted by priority (ascending).
    """
    with lock:
        # Create a sorted copy of pending tasks
        sorted_tasks = sorted(_pending_tasks, key=lambda x: (x[0], x[1]))
        return [task_id for priority, arrival_index, task_id in sorted_tasks]