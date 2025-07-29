import heapq
from collections import defaultdict, deque

def compute_min_total_lateness(tasks):
    # Map tasks by id for easy lookup
    task_map = {task["id"]: task for task in tasks}
    
    # Build graph: key = task_id, value = list of dependent task ids
    graph = defaultdict(list)
    # indegree of each task
    indegree = {task["id"]: 0 for task in tasks}
    
    # Create graph and count indegree for each task
    for task in tasks:
        for dep in task["dependencies"]:
            graph[dep].append(task["id"])
            indegree[task["id"]] += 1

    # Priority queue of available tasks with no unsatisfied dependencies
    # Use deadline as primary key, then task id for tie-breaking
    available = []
    for task_id, count in indegree.items():
        if count == 0:
            heapq.heappush(available, (task_map[task_id]["deadline"], task_id))
    
    current_time = 0
    total_lateness = 0

    # Process tasks in order: always pick the available task with the smallest deadline.
    while available:
        deadline, task_id = heapq.heappop(available)
        task = task_map[task_id]
        current_time += task["duration"]
        total_lateness += max(0, current_time - task["deadline"])
        
        # Process dependents
        for neighbor in graph[task_id]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                heapq.heappush(available, (task_map[neighbor]["deadline"], neighbor))
    
    return total_lateness

if __name__ == "__main__":
    # Sample manual test run
    tasks = [
        {"id": 1, "duration": 5, "deadline": 10, "dependencies": []},
        {"id": 2, "duration": 3, "deadline": 15, "dependencies": [1]},
        {"id": 3, "duration": 7, "deadline": 20, "dependencies": [1, 2]},
        {"id": 4, "duration": 2, "deadline": 12, "dependencies": []}
    ]
    print(compute_min_total_lateness(tasks))