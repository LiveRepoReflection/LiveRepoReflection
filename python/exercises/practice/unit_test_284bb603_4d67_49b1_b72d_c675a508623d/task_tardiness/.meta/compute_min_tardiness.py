from collections import deque

def compute_min_tardiness(tasks):
    # Build a lookup for task by id
    task_lookup = {task["id"]: task for task in tasks}
    n = len(tasks)

    # Build graph and indegree dictionary
    graph = {task["id"]: [] for task in tasks}
    indegree = {task["id"]: 0 for task in tasks}
    for task in tasks:
        for dep in task["dependencies"]:
            graph[dep].append(task["id"])
            indegree[task["id"]] += 1

    # Initialize queue for topological order processing
    queue = deque()
    for task_id, deg in indegree.items():
        if deg == 0:
            queue.append(task_id)

    # Dictionary to store computed finish times for tasks
    finish_time = {}

    # Process tasks in topological order
    processed_count = 0
    while queue:
        current = queue.popleft()
        processed_count += 1
        current_task = task_lookup[current]
        if not current_task["dependencies"]:
            # No prerequisites: finish time is its own duration
            finish_time[current] = current_task["duration"]
        else:
            # Start once all dependencies have finished
            max_dep_finish = max(finish_time[dep] for dep in current_task["dependencies"])
            finish_time[current] = max_dep_finish + current_task["duration"]

        # Reduce indegree for neighbors and add them if they become ready
        for neighbor in graph[current]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)

    # Check for cycles in the dependency graph
    if processed_count != n:
        raise ValueError("Cycle detected in task dependencies")

    # Calculate total tardiness as sum(max(0, finish_time - deadline)) for each task
    total_tardiness = 0
    for task_id, finish in finish_time.items():
        deadline = task_lookup[task_id]["deadline"]
        tardiness = finish - deadline
        if tardiness > 0:
            total_tardiness += tardiness

    return total_tardiness