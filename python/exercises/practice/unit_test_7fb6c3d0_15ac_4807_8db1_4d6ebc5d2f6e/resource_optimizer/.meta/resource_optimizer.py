import heapq

def optimize_allocation(resource_capacities, tasks, task_durations):
    if not tasks:
        return []

    # Create a list of tasks with their deadline, duration and resource requirements
    task_list = []
    for task_id, deadline, resource_requests in tasks:
        duration = task_durations.get(task_id, 0)
        task_list.append((deadline, duration, task_id, resource_requests))

    # Sort tasks by deadline (Earliest Deadline First)
    task_list.sort()

    current_time = 0
    scheduled_tasks = []
    available_resources = resource_capacities.copy()
    task_queue = []

    for deadline, duration, task_id, resource_requests in task_list:
        # Check if task can be completed before deadline
        if current_time + duration > deadline:
            continue

        # Check if resources are available
        feasible = True
        for resource, amount in resource_requests.items():
            if available_resources.get(resource, 0) < amount:
                feasible = False
                break

        if feasible:
            # Allocate resources
            for resource, amount in resource_requests.items():
                available_resources[resource] -= amount

            # Schedule task
            scheduled_tasks.append(task_id)
            heapq.heappush(task_queue, (current_time + duration, task_id, resource_requests))
            current_time += duration
        else:
            # Try to see if we can preempt existing tasks
            if task_queue:
                earliest_completion, earliest_id, earliest_resources = task_queue[0]
                if earliest_completion > deadline:
                    continue  # Can't help

                # Check if preempting would allow this task to run
                temp_resources = available_resources.copy()
                for resource, amount in resource_requests.items():
                    temp_resources[resource] = temp_resources.get(resource, 0) - amount
                    if temp_resources[resource] < 0:
                        break
                else:
                    # Preempt the earliest task
                    heapq.heappop(task_queue)
                    for resource, amount in earliest_resources.items():
                        available_resources[resource] += amount
                    scheduled_tasks.remove(earliest_id)
                    current_time = earliest_completion

                    # Try to schedule current task
                    for resource, amount in resource_requests.items():
                        available_resources[resource] -= amount
                    scheduled_tasks.append(task_id)
                    heapq.heappush(task_queue, (current_time + duration, task_id, resource_requests))
                    current_time += duration

    return scheduled_tasks