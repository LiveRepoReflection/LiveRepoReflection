def schedule_tasks(n, k, deadlines, affinities):
    # Create a list of lists to hold deadlines for tasks on each core.
    core_tasks = [[] for _ in range(k)]
    for i in range(n):
        core = affinities[i]
        core_tasks[core].append(deadlines[i])
    
    total_scheduled = 0
    # Process each core independently.
    for tasks in core_tasks:
        # Sort tasks by their deadlines.
        tasks.sort()
        current_time = 0
        for deadline in tasks:
            # If the current time slot is available before the deadline, schedule the task.
            if current_time < deadline:
                total_scheduled += 1
                current_time += 1
    return total_scheduled

if __name__ == "__main__":
    # Example usage:
    n = 5
    k = 2
    deadlines = [2, 2, 3, 4, 4]
    affinities = [0, 1, 0, 1, 0]
    print(schedule_tasks(n, k, deadlines, affinities))