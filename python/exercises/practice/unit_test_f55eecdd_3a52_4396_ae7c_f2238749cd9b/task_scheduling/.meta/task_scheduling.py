from functools import lru_cache

def schedule_tasks(N, K, tasks):
    # Build a dictionary mapping task id -> (processing_time, deadline, dependencies)
    task_map = {}
    for tid, proc, deadline, deps in tasks:
        task_map[tid] = (proc, deadline, deps)
    
    # Check for cycle using topological sort
    graph = {tid: [] for tid in task_map.keys()}
    indegree = {tid: 0 for tid in task_map.keys()}
    for tid, (proc, deadline, deps) in task_map.items():
        for d in deps:
            if d in task_map:
                graph[d].append(tid)
                indegree[tid] += 1

    queue = [tid for tid in task_map if indegree[tid] == 0]
    count = 0
    while queue:
        cur = queue.pop(0)
        count += 1
        for neigh in graph[cur]:
            indegree[neigh] -= 1
            if indegree[neigh] == 0:
                queue.append(neigh)
    if count < N:
        return -1

    ALL_MASK = (1 << N) - 1

    @lru_cache(maxsize=None)
    def dp(mask, machine_times):
        # machine_times is a tuple of K integers representing the finish time of each machine (sorted)
        if mask == ALL_MASK:
            return 0
        best = float('inf')
        # Try to schedule any available task
        for tid in range(N):
            if mask & (1 << tid):
                continue
            proc, deadline, deps = task_map[tid]
            # Task is available only if all its dependencies are done
            if any((mask & (1 << d)) == 0 for d in deps):
                continue
            # Try scheduling on each machine
            for i in range(K):
                current_time = machine_times[i]
                finish_time = current_time + proc
                tardiness = finish_time - deadline if finish_time > deadline else 0
                new_times = list(machine_times)
                new_times[i] = finish_time
                new_times.sort()
                new_machine_times = tuple(new_times)
                new_mask = mask | (1 << tid)
                candidate = tardiness + dp(new_mask, new_machine_times)
                if candidate < best:
                    best = candidate
        return best

    initial_machine_times = tuple([0] * K)
    return dp(0, initial_machine_times)

if __name__ == '__main__':
    # Example usage:
    tasks = [
        (0, 3, 5, []),
        (1, 2, 5, [])
    ]
    result = schedule_tasks(2, 2, tasks)
    print(result)