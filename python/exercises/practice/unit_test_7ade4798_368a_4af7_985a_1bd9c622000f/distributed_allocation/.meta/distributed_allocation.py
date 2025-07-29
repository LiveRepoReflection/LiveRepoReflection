def solve(N, M, worker_capacities, task_resources, task_dependencies, new_tasks):
    # Combine initial tasks with new tasks.
    combined_task_resources = task_resources + [nt[1] for nt in new_tasks]
    combined_task_dependencies = [list(deps) for deps in task_dependencies] + [list(nt[2]) for nt in new_tasks]
    T = len(combined_task_resources)
    
    # Build the dependency graph for topological sorting.
    # For each task j, for each dependency dep in combined_task_dependencies[j],
    # we add an edge from dep to j.
    adj = [[] for _ in range(T)]
    indegree = [0] * T
    for j in range(T):
        for dep in combined_task_dependencies[j]:
            adj[dep].append(j)
            indegree[j] += 1

    # Compute a topological order using Kahn's algorithm.
    from collections import deque
    q = deque()
    for i in range(T):
        if indegree[i] == 0:
            q.append(i)
    topo_order = []
    while q:
        u = q.popleft()
        topo_order.append(u)
        for v in adj[u]:
            indegree[v] -= 1
            if indegree[v] == 0:
                q.append(v)
    # If not all tasks are in topo_order then the input was not a valid DAG.
    if len(topo_order) != T:
        # For safety, mark all tasks as unassigned.
        return [-1] * T

    # Allocate tasks respecting dependency and resource constraints.
    allocation = [-1] * T
    for task in topo_order:
        # Check if all dependencies were successfully allocated.
        can_execute = True
        for dep in combined_task_dependencies[task]:
            if allocation[dep] == -1:
                can_execute = False
                break
        if not can_execute:
            allocation[task] = -1
            continue
        # Assign the task to the first available worker that has sufficient capacity.
        assigned_worker = -1
        for i in range(N):
            if worker_capacities[i] >= combined_task_resources[task]:
                assigned_worker = i
                break
        allocation[task] = assigned_worker

    return allocation