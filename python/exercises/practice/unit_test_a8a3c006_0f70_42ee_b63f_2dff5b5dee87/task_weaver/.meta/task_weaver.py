import heapq
from collections import defaultdict, deque


def schedule_tasks(tasks, machines, parallelism_limit):
    """
    Schedule tasks to machines while respecting dependencies, resource constraints,
    and parallelism limit to minimize the overall completion time.
    
    Args:
        tasks: List of task dictionaries, each containing task_id, dependencies,
               cpu_requirement, memory_requirement, and execution_time.
        machines: List of machine dictionaries, each containing machine_id,
                  cpu_capacity, and memory_capacity.
        parallelism_limit: Maximum number of tasks that can run in parallel.
    
    Returns:
        A schedule dictionary mapping task_id to a dictionary with machine_id and start_time.
    """
    
    # Check for cycles in the task dependency graph
    if has_cycle(tasks):
        raise Exception("Cyclic dependencies detected. Cannot schedule tasks.")
    
    # Create a dictionary to map task_id to the task
    task_dict = {task["task_id"]: task for task in tasks}
    
    # Count the number of dependencies for each task
    in_degree = {task["task_id"]: len(task["dependencies"]) for task in tasks}
    
    # Create an adjacency list to represent the dependency graph
    graph = defaultdict(list)
    for task in tasks:
        task_id = task["task_id"]
        for dep_id in task["dependencies"]:
            graph[dep_id].append(task_id)
    
    # Create a priority queue for ready tasks (tasks with in_degree = 0)
    ready_tasks = [(0, task["task_id"]) for task in tasks if in_degree[task["task_id"]] == 0]
    heapq.heapify(ready_tasks)  # Priority by earliest possible start time
    
    # Initialize schedule and track resource usage over time
    schedule = {}
    machine_events = []  # List of (time, machine_id, is_release_event, cpu, memory, task_id)
    
    # Track the number of currently running tasks
    running_tasks = 0
    
    # Initialize the current time
    current_time = 0
    
    # Process tasks until all are scheduled
    while ready_tasks or machine_events:
        # Process machine events (task completions) that occur before or at current_time
        while machine_events and machine_events[0][0] <= current_time:
            event_time, machine_id, is_release_event, cpu, memory, task_id = heapq.heappop(machine_events)
            
            if is_release_event:
                # Release resources
                for machine in machines:
                    if machine["machine_id"] == machine_id:
                        machine["cpu_capacity"] += cpu
                        machine["memory_capacity"] += memory
                        break
                
                # Decrement running tasks counter
                running_tasks -= 1
                
                # Update dependencies for the completed task
                for next_task_id in graph[task_id]:
                    in_degree[next_task_id] -= 1
                    if in_degree[next_task_id] == 0:
                        # Add to ready queue with the earliest possible start time
                        heapq.heappush(ready_tasks, (event_time, next_task_id))
        
        if not ready_tasks and machine_events:
            # Fast-forward time to the next machine event
            current_time = machine_events[0][0]
            continue
        
        if not ready_tasks and not machine_events:
            # All tasks are scheduled
            break
        
        # Try to schedule a ready task
        if ready_tasks and running_tasks < parallelism_limit:
            _, task_id = heapq.heappop(ready_tasks)
            task = task_dict[task_id]
            
            # Find the earliest time and machine that can accommodate this task
            earliest_time = current_time
            best_machine = None
            best_start_time = float('inf')
            
            # Calculate the earliest possible start time based on dependencies
            for dep_id in task["dependencies"]:
                if dep_id in schedule:
                    dep_task = task_dict[dep_id]
                    dep_end_time = schedule[dep_id]["start_time"] + dep_task["execution_time"]
                    earliest_time = max(earliest_time, dep_end_time)
            
            # Sort machines by resource availability (descending) to try best-fit first
            sorted_machines = sorted(
                machines, 
                key=lambda m: (m["cpu_capacity"], m["memory_capacity"]),
                reverse=True
            )
            
            for machine in sorted_machines:
                if (machine["cpu_capacity"] >= task["cpu_requirement"] and 
                    machine["memory_capacity"] >= task["memory_requirement"]):
                    
                    # This machine can accommodate the task right now
                    best_machine = machine
                    best_start_time = earliest_time
                    break
            
            if best_machine is not None:
                # Schedule the task
                schedule[task_id] = {
                    "machine_id": best_machine["machine_id"],
                    "start_time": best_start_time
                }
                
                # Allocate resources
                best_machine["cpu_capacity"] -= task["cpu_requirement"]
                best_machine["memory_capacity"] -= task["memory_requirement"]
                
                # Schedule release of resources
                end_time = best_start_time + task["execution_time"]
                heapq.heappush(
                    machine_events,
                    (end_time, best_machine["machine_id"], True, 
                     task["cpu_requirement"], task["memory_requirement"], task_id)
                )
                
                # Increment running tasks counter
                running_tasks += 1
            else:
                # No machine can accommodate this task, push it back with a later start time
                # We'll try again when resources are released
                heapq.heappush(ready_tasks, (current_time + 1, task_id))
                
                if not machine_events:
                    # If there are no future events, we have a resource starvation problem
                    raise Exception(f"Task {task_id} requires more resources than any available machine can provide.")
                
                # Advance time to the next event
                if machine_events:
                    current_time = machine_events[0][0]
        elif running_tasks >= parallelism_limit:
            # We've hit the parallelism limit, wait for a task to finish
            if machine_events:
                current_time = machine_events[0][0]
            else:
                raise Exception("Reached parallelism limit with no future events. This should not happen.")
        else:
            # No ready tasks but we have future events
            if machine_events:
                current_time = machine_events[0][0]
            else:
                # This should never happen given our loop conditions
                break
    
    # Check if all tasks are scheduled
    if len(schedule) != len(tasks):
        unscheduled = [t["task_id"] for t in tasks if t["task_id"] not in schedule]
        raise Exception(f"Could not schedule all tasks. Unscheduled tasks: {unscheduled}")
    
    # Reset machine capacities to their original values
    for machine_orig in machines:
        machine_id = machine_orig["machine_id"]
        for event in machine_events:
            if event[1] == machine_id and event[2]:  # is_release_event
                machine_orig["cpu_capacity"] += event[3]  # cpu
                machine_orig["memory_capacity"] += event[4]  # memory
    
    return schedule


def has_cycle(tasks):
    """
    Detect if there's a cycle in the task dependency graph using DFS.
    
    Args:
        tasks: List of task dictionaries
    
    Returns:
        True if a cycle is detected, False otherwise
    """
    # Create a dictionary to map task_id to the task
    task_dict = {task["task_id"]: task for task in tasks}
    
    # Create an adjacency list to represent the dependency graph
    graph = defaultdict(list)
    for task in tasks:
        task_id = task["task_id"]
        for dep_id in task["dependencies"]:
            if dep_id not in task_dict:
                raise Exception(f"Dependency {dep_id} for task {task_id} does not exist.")
            graph[task_id].append(dep_id)
    
    # Track visited and currently in stack nodes
    visited = set()
    rec_stack = set()
    
    def is_cyclic(node):
        visited.add(node)
        rec_stack.add(node)
        
        for neighbor in graph[node]:
            if neighbor not in visited:
                if is_cyclic(neighbor):
                    return True
            elif neighbor in rec_stack:
                return True
        
        rec_stack.remove(node)
        return False
    
    # Check each node
    for task in tasks:
        task_id = task["task_id"]
        if task_id not in visited:
            if is_cyclic(task_id):
                return True
    
    return False