from collections import defaultdict, deque
from typing import List, Tuple, Set

def find_optimal_schedule(n: int, resources: int, task_resources: List[int], 
                         task_deadlines: List[int], dependencies: List[List[int]]) -> List[Tuple[int, int]]:
    def is_valid_schedule(schedule: List[Tuple[int, int]]) -> bool:
        timeline = defaultdict(int)
        for start_time, task_idx in schedule:
            if timeline[start_time] + task_resources[task_idx] > resources:
                return False
            timeline[start_time] += task_resources[task_idx]
        return True

    def get_earliest_start_time(task: int, completed_tasks: Set[int], 
                              current_schedule: List[Tuple[int, int]]) -> int:
        # Check dependencies
        max_dependency_time = -1
        for dep in dependencies[task]:
            if dep not in completed_tasks:
                return -1
            for start_time, task_idx in current_schedule:
                if task_idx == dep:
                    max_dependency_time = max(max_dependency_time, start_time + 1)

        # Find earliest time slot that satisfies resource constraints
        earliest_time = max(0, max_dependency_time)
        while earliest_time < task_deadlines[task] - 1:
            # Create temporary schedule with new task
            temp_schedule = current_schedule + [(earliest_time, task)]
            if is_valid_schedule(temp_schedule):
                return earliest_time
            earliest_time += 1
        return -1

    def compute_priorities() -> List[Tuple[int, float]]:
        # Calculate in-degree for topological sort
        in_degree = [len(deps) for deps in dependencies]
        
        # Calculate critical path length for each task
        critical_paths = [0] * n
        zero_in_degree = deque([i for i, deg in enumerate(in_degree) if deg == 0])
        
        while zero_in_degree:
            task = zero_in_degree.popleft()
            # Find dependent tasks
            for next_task in range(n):
                if task in dependencies[next_task]:
                    critical_paths[next_task] = max(critical_paths[next_task], 
                                                  critical_paths[task] + 1)
                    in_degree[next_task] -= 1
                    if in_degree[next_task] == 0:
                        zero_in_degree.append(next_task)

        # Calculate priority score based on multiple factors
        priorities = []
        for task in range(n):
            score = (
                -task_deadlines[task] * 1000  # Earlier deadline -> higher priority
                - task_resources[task] * 10    # Less resources -> higher priority
                + critical_paths[task] * 100   # Longer critical path -> higher priority
                + len([t for t in range(n) if task in dependencies[t]]) * 50  # More dependents -> higher priority
            )
            priorities.append((task, score))
        
        return sorted(priorities, key=lambda x: x[1], reverse=True)

    def schedule_tasks() -> List[Tuple[int, int]]:
        best_schedule = []
        best_count = -1
        
        # Try different priority orderings
        priorities = compute_priorities()
        
        current_schedule = []
        completed_tasks = set()
        
        for task, _ in priorities:
            if task in completed_tasks:
                continue
                
            start_time = get_earliest_start_time(task, completed_tasks, current_schedule)
            if start_time != -1:
                current_schedule.append((start_time, task))
                completed_tasks.add(task)
                
                # Update best schedule if needed
                if len(completed_tasks) > best_count:
                    best_count = len(completed_tasks)
                    best_schedule = current_schedule.copy()
                elif len(completed_tasks) == best_count:
                    # If same number of tasks, prefer schedule with earlier completion time
                    current_makespan = max(t[0] + 1 for t in current_schedule)
                    best_makespan = max(t[0] + 1 for t in best_schedule)
                    if current_makespan < best_makespan:
                        best_schedule = current_schedule.copy()

        return best_schedule

    # Input validation
    if not (1 <= n <= 1000 and 1 <= resources <= 1000):
        return []
    
    for i in range(n):
        if not (1 <= task_resources[i] <= resources and 
                1 <= task_deadlines[i] <= 10000 and 
                0 <= len(dependencies[i]) <= n):
            return []

    # Check for cycles in dependencies
    def has_cycle(task: int, visited: Set[int], stack: Set[int]) -> bool:
        visited.add(task)
        stack.add(task)
        
        for dep in dependencies[task]:
            if dep not in visited:
                if has_cycle(dep, visited, stack):
                    return True
            elif dep in stack:
                return True
                
        stack.remove(task)
        return False

    visited = set()
    stack = set()
    for task in range(n):
        if task not in visited:
            if has_cycle(task, visited, stack):
                return []  # Invalid DAG

    return schedule_tasks()