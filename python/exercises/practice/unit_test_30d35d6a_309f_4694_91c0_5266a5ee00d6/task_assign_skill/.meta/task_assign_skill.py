def min_completion_time(employees, tasks, dependencies, n, m):
    # Check that every task can be executed by at least one employee.
    for req_skills, duration in tasks:
        if not any(req_skills.issubset(emp) for emp in employees):
            return -1

    # Build dependency graph and check for cycles using Kahn's algorithm.
    from collections import defaultdict, deque
    graph = defaultdict(list)
    in_degree = [0] * m
    for pre, post in dependencies:
        graph[pre].append(post)
        in_degree[post] += 1

    queue = deque([i for i in range(m) if in_degree[i] == 0])
    visited = 0
    while queue:
        u = queue.popleft()
        visited += 1
        for v in graph[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)

    # If not all tasks are visited, there is a cycle.
    if visited != m:
        return -1

    # Since tasks are executed sequentially due to shared global resource and dependency constraints,
    # the minimum total completion time is the sum of the durations of all tasks.
    total_time = sum(duration for _, duration in tasks)
    return total_time

if __name__ == '__main__':
    # Sample manual test run.
    employees = [
        {"A", "B"},
        {"B", "C"}
    ]
    tasks = [
        ({"A"}, 5),
        ({"B"}, 10),
        ({"C"}, 7)
    ]
    dependencies = [
        (0, 1),
        (1, 2)
    ]
    n = len(employees)
    m = len(tasks)
    print(min_completion_time(employees, tasks, dependencies, n, m))