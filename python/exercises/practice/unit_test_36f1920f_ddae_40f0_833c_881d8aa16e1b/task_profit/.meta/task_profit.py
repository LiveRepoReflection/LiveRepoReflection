def task_profit_function(tasks):
    if not tasks:
        return 0

    # Sort tasks in descending order based on profit
    tasks_sorted = sorted(tasks, key=lambda x: x[1], reverse=True)

    # Determine the maximum deadline to initialize the DSU structure
    max_deadline = max(deadline for deadline, _ in tasks_sorted)

    # Initialize the disjoint set (union-find) structure for time slots
    parent = list(range(max_deadline + 1))

    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]

    total_profit = 0

    # Process each task in order of highest profit first
    for deadline, profit in tasks_sorted:
        # Find the latest available slot on or before the task's deadline
        available_slot = find(deadline)
        if available_slot > 0:
            total_profit += profit
            # Mark this slot as occupied by linking it to the next available slot
            parent[available_slot] = find(available_slot - 1)

    return total_profit