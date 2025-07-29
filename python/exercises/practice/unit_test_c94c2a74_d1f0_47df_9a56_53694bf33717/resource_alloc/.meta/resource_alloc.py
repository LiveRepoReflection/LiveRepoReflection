def schedule_tasks(N, M, W, node_capacities, task_definitions, C):
    # Build task dictionary and dependency graph
    tasks = {}
    indegree = {}
    graph = {}
    for i, (arrival, req, exec_time, deps, output) in enumerate(task_definitions):
        tasks[i] = {'arrival': arrival, 'req': req, 'exec': exec_time, 'deps': deps, 'output': output}
        indegree[i] = len(deps)
        graph[i] = []
    for i, task in tasks.items():
        for dep in task['deps']:
            graph[dep].append(i)
    # Compute topological order using Kahn's algorithm
    queue = []
    for i in range(len(task_definitions)):
        if indegree[i] == 0:
            queue.append(i)
    topo_order = []
    while queue:
        u = queue.pop(0)
        topo_order.append(u)
        for v in graph[u]:
            indegree[v] -= 1
            if indegree[v] == 0:
                queue.append(v)
    if len(topo_order) != len(task_definitions):
        raise ValueError("Cycle detected in task dependencies.")

    # Initialize resource usage timeline for each node from time 0 to W-1.
    node_usage = []
    for i in range(N):
        usage = [[0] * M for _ in range(W)]
        node_usage.append(usage)

    # Dictionary to store assignment: task_id -> (node, start_time)
    assignment = {}
    # Dictionary to store finish times: task_id -> finish_time
    finish_times = {}

    for task_id in topo_order:
        task = tasks[task_id]
        arrival = task['arrival']
        exec_time = task['exec']
        req = task['req']
        # Earliest start is the maximum of arrival time and dependencies' finish times.
        earliest = arrival
        if task['deps']:
            dep_finish_time = max(finish_times[dep] for dep in task['deps'])
            if dep_finish_time > earliest:
                earliest = dep_finish_time

        # Determine candidate nodes: prefer nodes used by dependencies.
        preferred_nodes = set()
        for dep in task['deps']:
            if dep in assignment:
                preferred_nodes.add(assignment[dep][0])
        if preferred_nodes:
            nodes_order = list(preferred_nodes) + [node for node in range(N) if node not in preferred_nodes]
        else:
            nodes_order = list(range(N))

        scheduled = False
        # Try each candidate node.
        for node in nodes_order:
            # Try each possible starting time from earliest to latest possible start time.
            for start in range(earliest, W - exec_time + 1):
                can_schedule = True
                # Check resource availability in each time slot during the task execution.
                for t in range(start, start + exec_time):
                    for j in range(M):
                        if node_usage[node][t][j] + req[j] > node_capacities[node][j]:
                            can_schedule = False
                            break
                    if not can_schedule:
                        break
                if can_schedule:
                    # Schedule the task in this node at the selected start time.
                    for t in range(start, start + exec_time):
                        for j in range(M):
                            node_usage[node][t][j] += req[j]
                    assignment[task_id] = (node, start)
                    finish_times[task_id] = start + exec_time
                    scheduled = True
                    break
            if scheduled:
                break
        if not scheduled:
            raise ValueError(f"Task {task_id} cannot be scheduled within the given time window.")

    # Return the schedule as a list of tuples sorted by task_id.
    schedule_list = []
    for task_id in sorted(assignment.keys()):
        node, start = assignment[task_id]
        schedule_list.append((task_id, node, start))
    return schedule_list


if __name__ == '__main__':
    # Example execution for manual testing.
    N = 2
    M = 2
    W = 10
    node_capacities = [
        [4, 8],
        [2, 4]
    ]
    task_definitions = [
        (0, [1, 2], 3, [], 10),
        (1, [2, 1], 2, [0], 5),
        (2, [1, 1], 4, [], 0)
    ]
    C = 0.1
    result = schedule_tasks(N, M, W, node_capacities, task_definitions, C)
    print(result)