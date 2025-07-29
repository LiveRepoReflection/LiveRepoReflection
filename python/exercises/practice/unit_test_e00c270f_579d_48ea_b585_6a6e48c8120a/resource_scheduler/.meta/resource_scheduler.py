from bisect import bisect_left, insort

def schedule_tasks(N, M, tasks, machines):
    # If no tasks, return 0 immediately.
    if N == 0 or not tasks:
        return 0

    # Determine the maximum deadline among tasks.
    T_max = max(deadline for _, deadline in tasks)

    # Initialize time slots from 1 to T_max.
    # For each time slot, maintain a sorted list of tuples (available_capacity, machine_index)
    # representing the remaining capacity of each machine at that time slot.
    time_slots = [[] for _ in range(T_max + 1)]
    for t in range(1, T_max + 1):
        for machine_index, cap in enumerate(machines):
            time_slots[t].append((cap, machine_index))
        time_slots[t].sort()

    # Sort tasks by deadline and then by resource requirement in ascending order.
    # Each task is a tuple (resource_required, deadline)
    tasks_sorted = sorted(tasks, key=lambda task: (task[1], task[0]))

    scheduled_count = 0
    # Attempt to schedule each task.
    for r, d in tasks_sorted:
        scheduled = False
        # Try to assign task in the latest possible time slot up to its deadline.
        for t in range(d, 0, -1):
            slot = time_slots[t]
            # Use binary search to find a machine with remaining capacity >= r.
            idx = bisect_left(slot, (r, -1))
            if idx < len(slot):
                available_cap, machine_id = slot.pop(idx)
                # Deduct the required resource.
                remaining_cap = available_cap - r
                # Insert the updated capacity back into the sorted list.
                insort(slot, (remaining_cap, machine_id))
                scheduled_count += 1
                scheduled = True
                break
        # If the task cannot be scheduled within its deadline, move onto the next task.
    return scheduled_count

if __name__ == "__main__":
    # Example execution for quick testing:
    tasks = [(5, 3), (10, 2), (3, 2), (7, 3)]
    machines = [10, 10]
    print(schedule_tasks(len(tasks), len(machines), tasks, machines))