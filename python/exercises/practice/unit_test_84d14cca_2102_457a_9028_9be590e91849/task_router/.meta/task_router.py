import heapq
from collections import defaultdict
from typing import List, Dict, Any


def route_tasks(tasks: List[Dict[str, Any]], workers: List[Dict[str, Any]]) -> Dict[int, List[int]]:
    """
    Route tasks to worker nodes to minimize makespan and maximize resource utilization.
    
    Args:
        tasks: A list of dictionaries representing tasks with their properties.
        workers: A list of dictionaries representing worker nodes with their properties.
        
    Returns:
        A dictionary where keys are worker_ids and values are lists of task_ids assigned to that worker.
        Includes an 'unassigned' key for tasks that couldn't be assigned.
    """
    # Sort tasks by priority (highest first) and then by cpu_needed (largest first)
    sorted_tasks = sorted(tasks, key=lambda x: (-x['priority'], -x['cpu_needed']))
    
    # Initialize worker state tracking
    worker_state = {}
    for worker in workers:
        worker_id = worker['worker_id']
        worker_state[worker_id] = {
            'cpu_remaining': worker['cpu_available'],
            'memory_remaining': worker['memory_available'],
            'io_remaining': worker['disk_io_capacity'],
            'task_types': worker['task_types_supported'],
            'assigned_tasks': [],
            'load': 0  # Represents the current makespan contribution (sum of cpu_needed)
        }
    
    # Result dictionary
    result = defaultdict(list)
    
    # Process tasks
    for task in sorted_tasks:
        task_id = task['task_id']
        task_type = task['task_type']
        cpu_needed = task['cpu_needed']
        memory_needed = task['memory_needed']
        io_needed = task['disk_io_needed']
        
        # Find eligible workers for this task
        eligible_workers = []
        for worker_id, state in worker_state.items():
            if (task_type in state['task_types'] and
                cpu_needed <= state['cpu_remaining'] and
                memory_needed <= state['memory_remaining'] and
                io_needed <= state['io_remaining']):
                # Calculate the makespan if we assign this task to this worker
                new_load = state['load'] + cpu_needed
                # We use a tuple with (new_load, worker_id) for the heap
                # This automatically handles the tie-breaking by worker_id
                heapq.heappush(eligible_workers, (new_load, worker_id))
        
        # Assign task to the worker that minimizes the makespan
        if eligible_workers:
            _, best_worker_id = heapq.heappop(eligible_workers)
            
            # Update worker state
            worker_state[best_worker_id]['cpu_remaining'] -= cpu_needed
            worker_state[best_worker_id]['memory_remaining'] -= memory_needed
            worker_state[best_worker_id]['io_remaining'] -= io_needed
            worker_state[best_worker_id]['assigned_tasks'].append(task_id)
            worker_state[best_worker_id]['load'] += cpu_needed
            
            # Update result
            result[best_worker_id].append(task_id)
        else:
            # Task cannot be assigned
            result['unassigned'].append(task_id)
    
    # Check if we can improve resource utilization by redistributing tasks
    optimize_resource_utilization(result, worker_state, tasks)
    
    return result


def optimize_resource_utilization(result: Dict[int, List[int]], worker_state: Dict[int, Dict[str, Any]], tasks: List[Dict[str, Any]]) -> None:
    """
    Try to improve resource utilization by moving tasks between workers.
    
    This function attempts to move tasks from heavily loaded workers to less loaded ones
    while maintaining or improving the overall makespan.
    
    Args:
        result: The current assignment of tasks to workers.
        worker_state: The current state of each worker.
        tasks: The original list of task dictionaries.
    """
    # Get task lookup dictionary for quick access
    task_lookup = {task['task_id']: task for task in tasks}
    
    # Calculate current makespan
    current_makespan = max([state['load'] for state in worker_state.values()]) if worker_state else 0
    
    # Identify the most loaded and least loaded workers
    workers_by_load = sorted([(state['load'], worker_id) for worker_id, state in worker_state.items()])
    
    if not workers_by_load:
        return
    
    # Try to move tasks from most loaded to least loaded workers
    for _ in range(3):  # Limit the number of optimization passes
        improved = False
        
        # Iterate through workers from most loaded to least loaded
        for i in range(len(workers_by_load) - 1, 0, -1):
            source_load, source_worker_id = workers_by_load[i]
            
            # Skip if worker is not heavily loaded
            if source_load < current_makespan * 0.8:
                continue
                
            source_tasks = result[source_worker_id].copy()
            
            # Try to move each task to a less loaded worker
            for task_id in source_tasks:
                task = task_lookup[task_id]
                
                # Calculate the load reduction if we move this task
                task_load = task['cpu_needed']
                
                # Consider less loaded workers
                for j in range(len(workers_by_load)):
                    target_load, target_worker_id = workers_by_load[j]
                    
                    # Skip if this is the same worker
                    if target_worker_id == source_worker_id:
                        continue
                    
                    target_state = worker_state[target_worker_id]
                    
                    # Check if the target worker can handle this task
                    if (task['task_type'] in target_state['task_types'] and
                        task['cpu_needed'] <= target_state['cpu_remaining'] and
                        task['memory_needed'] <= target_state['memory_remaining'] and
                        task['disk_io_needed'] <= target_state['io_remaining']):
                        
                        # Calculate new loads if we move this task
                        new_source_load = source_load - task_load
                        new_target_load = target_load + task_load
                        
                        # Move the task if it improves the makespan or balances the load
                        if max(new_source_load, new_target_load) < current_makespan:
                            # Update worker states
                            worker_state[source_worker_id]['cpu_remaining'] += task['cpu_needed']
                            worker_state[source_worker_id]['memory_remaining'] += task['memory_needed']
                            worker_state[source_worker_id]['io_remaining'] += task['disk_io_needed']
                            worker_state[source_worker_id]['load'] -= task_load
                            worker_state[source_worker_id]['assigned_tasks'].remove(task_id)
                            
                            worker_state[target_worker_id]['cpu_remaining'] -= task['cpu_needed']
                            worker_state[target_worker_id]['memory_remaining'] -= task['memory_needed']
                            worker_state[target_worker_id]['io_remaining'] -= task['disk_io_needed']
                            worker_state[target_worker_id]['load'] += task_load
                            worker_state[target_worker_id]['assigned_tasks'].append(task_id)
                            
                            # Update result
                            result[source_worker_id].remove(task_id)
                            result[target_worker_id].append(task_id)
                            
                            # Update the sorted list of workers by load
                            workers_by_load[i] = (new_source_load, source_worker_id)
                            workers_by_load[j] = (new_target_load, target_worker_id)
                            workers_by_load.sort()
                            
                            # Update the current makespan
                            current_makespan = max([state['load'] for state in worker_state.values()])
                            
                            improved = True
                            break
                
                if improved:
                    break
            
            if improved:
                break
        
        if not improved:
            break