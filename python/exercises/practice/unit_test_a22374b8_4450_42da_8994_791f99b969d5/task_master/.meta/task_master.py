import heapq
import random
from collections import defaultdict, deque
from typing import List, Tuple, Dict, Set, Any

# Default failure probability (can be overridden in function call)
DEFAULT_FAILURE_PROBABILITY = 0.01

def schedule_tasks(tasks: List[Tuple[int, int, List[int], int]], 
                  num_workers: int,
                  failure_probability: float = DEFAULT_FAILURE_PROBABILITY) -> List[Tuple[int, int, str, int]]:
    """
    Schedule tasks for execution on multiple worker nodes with dependency constraints,
    priority-based scheduling, and fault tolerance.
    
    Args:
        tasks: List of tuples (task_id, priority, dependencies, execution_time)
        num_workers: Number of available worker nodes
        failure_probability: Probability of worker failure per second of execution
        
    Returns:
        List of events (timestamp, worker_id, event_type, task_id) sorted by timestamp
    """
    # Create task dictionary for easier access
    task_dict = {task[0]: {"id": task[0], 
                          "priority": task[1], 
                          "deps": set(task[2]), 
                          "exec_time": task[3],
                          "remaining_time": task[3],
                          "completed": False} for task in tasks}

    # Set up dependency tracking
    children = defaultdict(set)
    for task_id, task_info in task_dict.items():
        for dep_id in task_info["deps"]:
            children[dep_id].add(task_id)
    
    # Track ready tasks (tasks with all dependencies satisfied)
    ready_tasks = []  # Priority queue (priority, task_id)
    
    # Find initial ready tasks (those with no dependencies)
    for task_id, task_info in task_dict.items():
        if not task_info["deps"]:
            # Use min-heap for priority (lower priority number = higher priority)
            heapq.heappush(ready_tasks, (task_info["priority"], task_id))
            
    # Track worker assignments and current time
    worker_assignments = {}  # worker_id -> (task_id, end_time)
    current_time = 0
    
    # Events to be returned
    events = []
    
    # Continue until all tasks are completed
    completed_tasks = set()
    
    while len(completed_tasks) < len(tasks) or worker_assignments:
        # Process any completed or failed tasks at the current time
        workers_to_free = []
        
        for worker_id, (task_id, end_time) in worker_assignments.items():
            if current_time >= end_time:
                # Task completed
                task_dict[task_id]["completed"] = True
                completed_tasks.add(task_id)
                events.append((current_time, worker_id, "COMPLETED", task_id))
                workers_to_free.append(worker_id)
                
                # Add child tasks to ready queue if all their dependencies are met
                for child_id in children.get(task_id, []):
                    task_dict[child_id]["deps"].discard(task_id)
                    if not task_dict[child_id]["deps"]:
                        heapq.heappush(ready_tasks, (task_dict[child_id]["priority"], child_id))
        
        # Free completed workers
        for worker_id in workers_to_free:
            del worker_assignments[worker_id]
        
        # Check for worker failures
        workers_failed = []
        for worker_id, (task_id, end_time) in worker_assignments.items():
            if random.random() < failure_probability:
                # Worker failed
                events.append((current_time, worker_id, "FAILED", task_id))
                workers_failed.append(worker_id)
                
                # Reschedule task
                task_dict[task_id]["remaining_time"] = end_time - current_time
                events.append((current_time, worker_id, "RESCHEDULED", task_id))
                heapq.heappush(ready_tasks, (task_dict[task_id]["priority"], task_id))
        
        # Free failed workers
        for worker_id in workers_failed:
            del worker_assignments[worker_id]
        
        # Assign tasks to available workers
        available_workers = [w for w in range(num_workers) if w not in worker_assignments]
        
        while available_workers and ready_tasks:
            priority, task_id = heapq.heappop(ready_tasks)
            
            # Skip if task is already completed (can happen with failed and rescheduled tasks)
            if task_dict[task_id]["completed"]:
                continue
                
            worker_id = available_workers.pop(0)
            execution_time = task_dict[task_id].get("remaining_time", task_dict[task_id]["exec_time"])
            end_time = current_time + execution_time
            
            worker_assignments[worker_id] = (task_id, end_time)
            events.append((current_time, worker_id, "SCHEDULED", task_id))
        
        # If there are no events at the current time, jump to the next event time
        if not worker_assignments and not ready_tasks:
            break
            
        if worker_assignments:
            # Jump to the next expected completion time
            next_time = min(end_time for _, end_time in worker_assignments.values())
            current_time = next_time
        else:
            # No workers are busy, increment time by 1
            current_time += 1
        
    # Sort events by timestamp
    events.sort()
    return events