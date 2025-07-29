import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Callable, List, Optional

def orchestrate_tasks(
    task_graph: Dict[int, List[int]],
    task_functions: Dict[int, Callable[[Dict[int, Any]], Any]],
    max_workers: int
) -> Dict[int, Optional[Any]]:
    """
    Orchestrate task execution respecting dependencies with maximum parallelism.
    
    Args:
        task_graph: Dictionary mapping task IDs to their dependency lists
        task_functions: Dictionary mapping task IDs to their executable functions
        max_workers: Maximum number of tasks to execute concurrently
        
    Returns:
        Dictionary mapping task IDs to their results (None if failed)
    """
    results = {}
    task_status = {}  # Track task completion status: None=not started, True=success, False=failed
    task_queue = []
    execution_order = []
    
    # Initialize status tracking
    for task_id in task_graph:
        results[task_id] = None
        task_status[task_id] = None
    
    # Topological sort to determine execution order
    visited = set()
    temp_visited = set()
    
    def topological_sort(node):
        if node in temp_visited:
            return
        temp_visited.add(node)
        for neighbor in task_graph.get(node, []):
            topological_sort(neighbor)
        visited.add(node)
        execution_order.insert(0, node)
    
    for node in task_graph:
        if node not in visited:
            topological_sort(node)
    
    # Prepare task queue with tasks that have all dependencies satisfied
    def update_queue():
        for task_id in execution_order:
            if task_status[task_id] is None:  # Task not started
                dependencies = task_graph[task_id]
                if all(task_status.get(dep, False) is True for dep in dependencies):
                    task_queue.append(task_id)
                    execution_order.remove(task_id)
    
    update_queue()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {}
        
        while task_queue or futures:
            # Submit tasks that are ready to run
            while task_queue and len(futures) < max_workers:
                task_id = task_queue.pop(0)
                
                # Prepare dependency results
                dep_results = {
                    dep: results[dep]
                    for dep in task_graph[task_id]
                }
                
                # Submit task for execution
                future = executor.submit(
                    execute_task,
                    task_id,
                    task_functions[task_id],
                    dep_results
                )
                futures[future] = task_id
            
            # Wait for at least one task to complete
            if futures:
                done, _ = concurrent.futures.wait(
                    futures.keys(),
                    return_when=concurrent.futures.FIRST_COMPLETED
                )
                
                for future in done:
                    task_id = futures.pop(future)
                    try:
                        result = future.result()
                        results[task_id] = result
                        task_status[task_id] = True
                    except Exception:
                        task_status[task_id] = False
                        results[task_id] = None
                
                # Update queue with newly available tasks
                update_queue()
    
    return results

def execute_task(
    task_id: int,
    task_func: Callable[[Dict[int, Any]], Any],
    dep_results: Dict[int, Any]
) -> Any:
    """
    Execute a single task with proper error handling.
    
    Args:
        task_id: ID of the task to execute
        task_func: Function to execute
        dep_results: Dictionary of dependency results
        
    Returns:
        Result of the task execution
        
    Raises:
        Exception: If task execution fails
    """
    # Check if any dependencies failed
    if any(result is None for result in dep_results.values()):
        raise Exception(f"Task {task_id} dependencies failed")
    
    return task_func(dep_results)