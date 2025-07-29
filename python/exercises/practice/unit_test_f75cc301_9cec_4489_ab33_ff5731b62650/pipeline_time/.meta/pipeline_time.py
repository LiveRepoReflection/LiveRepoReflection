import heapq
from collections import defaultdict, deque

def min_total_time(tasks, dependencies, processing_times, num_workers):
    if not tasks:
        return 0

    # Build the dependency graph and indegree counts.
    graph = defaultdict(list)
    indegree = {task: 0 for task in tasks}
    for task, deps in dependencies.items():
        # Ensure that tasks with dependencies not in tasks list are added.
        if task not in indegree:
            indegree[task] = 0
        for dep in deps:
            graph[dep].append(task)
            indegree[task] += 1

    # Initialize the ready queue (tasks with no dependencies)
    ready = deque()
    for task in tasks:
        if indegree[task] == 0:
            ready.append(task)

    current_time = 0
    # Heap to track running tasks: (finish_time, task)
    running = []
    
    # Number of tasks processed
    tasks_processed = 0
    total_tasks = len(tasks)
    
    while ready or running:
        # Assign tasks from ready to available workers
        while ready and len(running) < num_workers:
            task = ready.popleft()
            finish_time = current_time + processing_times[task]
            heapq.heappush(running, (finish_time, task))
        
        if running:
            # Advance time to the next finishing task
            finish_time, finished_task = heapq.heappop(running)
            current_time = finish_time
            tasks_processed += 1
            
            # Process all tasks finishing at the same time
            finished_tasks = [finished_task]
            while running and running[0][0] == finish_time:
                ft, t = heapq.heappop(running)
                finished_tasks.append(t)
                tasks_processed += 1
            
            # For every finished task, reduce indegree of dependent tasks.
            for finished in finished_tasks:
                for dependent in graph[finished]:
                    indegree[dependent] -= 1
                    if indegree[dependent] == 0:
                        ready.append(dependent)
        else:
            # In case no tasks are currently running but some tasks are ready
            if ready:
                # This case happens if there is a gap.
                current_time += 1

    return current_time

if __name__ == '__main__':
    # For direct testing (not used when running unit tests)
    tasks = [1, 2, 3]
    dependencies = {1: [], 2: [1], 3: [2]}
    processing_times = {1: 3, 2: 2, 3: 4}
    num_workers = 2
    print(min_total_time(tasks, dependencies, processing_times, num_workers))