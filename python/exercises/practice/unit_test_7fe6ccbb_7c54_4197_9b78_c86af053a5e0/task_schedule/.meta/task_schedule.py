from collections import defaultdict, deque
import heapq

def schedule_tasks(n, deadline, duration, dependencies):
    """
    Schedule tasks to meet their deadlines while respecting dependencies.
    
    Args:
        n (int): The number of tasks.
        deadline (list): List of integers representing the deadline for each task.
        duration (list): List of integers representing the duration for each task.
        dependencies (list): List of lists, where dependencies[i] contains the task IDs 
                            that must be completed before task i can start.
    
    Returns:
        list: An ordered list of task IDs to execute. Empty list if impossible.
    """
    # Check for circular dependencies using DFS
    if has_cycle(n, dependencies):
        return []
    
    # Build the dependency graph and calculate in-degrees
    graph = defaultdict(list)
    in_degree = [0] * n
    for i in range(n):
        for dep in dependencies[i]:
            graph[dep].append(i)
            in_degree[i] += 1
    
    # Calculate earliest possible start times considering dependencies
    earliest_start = [0] * n
    q = deque([i for i in range(n) if in_degree[i] == 0])
    
    while q:
        task = q.popleft()
        for next_task in graph[task]:
            earliest_start[next_task] = max(earliest_start[next_task], 
                                           earliest_start[task] + duration[task])
            in_degree[next_task] -= 1
            if in_degree[next_task] == 0:
                q.append(next_task)
    
    # Calculate latest possible start times considering deadlines
    latest_start = [float('inf')] * n
    for i in range(n):
        latest_start[i] = deadline[i] - duration[i]
    
    # Calculate slack (flexibility) for each task
    slack = [latest - earliest for earliest, latest in zip(earliest_start, latest_start)]
    
    # Check if any task has negative slack (impossible to meet deadline)
    if any(s < 0 for s in slack):
        return []
    
    # Sort tasks by slack (prioritize tasks with less flexibility)
    task_priority = [(slack[i], i) for i in range(n)]
    task_priority.sort()
    
    # Schedule tasks using topological sort and prioritization
    schedule = []
    visited = [False] * n
    current_time = 0
    task_completion = {}
    
    while len(schedule) < n:
        candidate = None
        
        # Find the next available task with highest priority
        for _, task in task_priority:
            if not visited[task] and all(dep in task_completion for dep in dependencies[task]):
                if candidate is None or slack[task] < slack[candidate]:
                    candidate = task
        
        if candidate is None:
            # No available tasks, but we haven't scheduled all tasks
            return []
        
        # Schedule the task
        schedule.append(candidate)
        visited[candidate] = True
        
        # Update current time and check if deadline is met
        start_time = max(current_time, 
                         max([task_completion.get(dep, 0) for dep in dependencies[candidate]], 
                             default=0))
        end_time = start_time + duration[candidate]
        
        if end_time > deadline[candidate]:
            return []  # Deadline exceeded
        
        task_completion[candidate] = end_time
        current_time = end_time
    
    return schedule

def has_cycle(n, dependencies):
    """
    Detect cycles in the dependency graph using DFS.
    
    Args:
        n (int): Number of tasks.
        dependencies (list): List of dependencies for each task.
        
    Returns:
        bool: True if there's a cycle, False otherwise.
    """
    graph = defaultdict(list)
    for i in range(n):
        for dep in dependencies[i]:
            graph[dep].append(i)
    
    visited = [0] * n  # 0: unvisited, 1: visiting, 2: visited
    
    def dfs(node):
        if visited[node] == 1:
            return True  # Cycle detected
        if visited[node] == 2:
            return False  # Already visited, no cycle
        
        visited[node] = 1  # Mark as visiting
        
        for neighbor in graph[node]:
            if dfs(neighbor):
                return True
        
        visited[node] = 2  # Mark as visited
        return False
    
    for i in range(n):
        if visited[i] == 0:
            if dfs(i):
                return True
                
    return False