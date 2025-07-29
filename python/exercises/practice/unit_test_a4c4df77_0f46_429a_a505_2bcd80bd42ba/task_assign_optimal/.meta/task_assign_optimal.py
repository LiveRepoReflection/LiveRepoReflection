def calculate_runtime(task_runtime, cpu_req, cpu_capacity, mem_req, mem_capacity, io_req, io_speed):
    """
    Estimates the runtime of a task on a given machine.
    This is a simplified model that uses available machine resources.
    """
    cpu_factor = min(1.0, cpu_capacity / cpu_req) if cpu_req > 0 else 1.0
    mem_factor = min(1.0, mem_capacity / mem_req) if mem_req > 0 else 1.0
    adjusted_io_speed = max(0.1, io_speed)  # Avoid division by zero or negative values
    io_factor = adjusted_io_speed
    return int(task_runtime / (cpu_factor * mem_factor * io_factor))


def assign_tasks(cpu_req, mem_req, io_req, deadline, estimated_runtime,
                 cpu_capacity, mem_capacity, io_speed, overload_penalty):
    """
    Assign tasks to machines to maximize the number of tasks that can be completed
    before their deadlines.

    Parameters:
      cpu_req: List of CPU cores required for each task.
      mem_req: List of memory (GB) required for each task.
      io_req: List of Disk I/O requirements for each task.
      deadline: List of deadlines (in seconds) for each task.
      estimated_runtime: List of estimated runtimes for tasks (in seconds).
      cpu_capacity: List of CPU capacities for each machine.
      mem_capacity: List of memory capacities for each machine.
      io_speed: List of I/O speed factors for each machine.
      overload_penalty: Factor by which the estimated runtime is multiplied if a machine is overloaded.

    Returns:
      A list of machine indices (0-indexed) assigned to each task.
    """
    num_tasks = len(cpu_req)
    num_machines = len(cpu_capacity)
    # Initialize the assignment list with -1 (unassigned)
    assignment = [-1] * num_tasks
    # Track the total CPU and memory used on each machine
    used_cpu = [0] * num_machines
    used_mem = [0] * num_machines

    # Process tasks sorted by their deadlines (earliest deadline first)
    tasks = list(range(num_tasks))
    tasks.sort(key=lambda i: deadline[i])

    for i in tasks:
        best_machine = None
        best_metric = None
        # Evaluate each machine for task i
        for j in range(num_machines):
            # Compute the new resource usage if task i is assigned to machine j
            new_cpu = used_cpu[j] + cpu_req[i]
            new_mem = used_mem[j] + mem_req[i]
            # Determine if machine j becomes overloaded
            overloaded = new_cpu > cpu_capacity[j] or new_mem > mem_capacity[j]
            penalty = overload_penalty if overloaded else 1
            # Adjust the task's runtime by the penalty if overloaded
            task_runtime_value = estimated_runtime[i] * penalty
            # Calculate the actual runtime for task i on machine j
            runtime = calculate_runtime(task_runtime_value, cpu_req[i], cpu_capacity[j],
                                        mem_req[i], mem_capacity[j], io_req[i], io_speed[j])
            finishable = runtime <= deadline[i]
            # Tie-breaking metric:
            # 1. Tasks that can finish before deadline (finishable: 0 vs non-finishable: 1)
            # 2. Lower runtime is preferred
            # 3. Minimal incremental resource usage (sum of cpu and memory after assignment)
            resource_usage = new_cpu + new_mem
            metric = (0 if finishable else 1, runtime, resource_usage)
            if best_machine is None or metric < best_metric:
                best_machine = j
                best_metric = metric
        # Assign task i to the best machine found
        assignment[i] = best_machine
        used_cpu[best_machine] += cpu_req[i]
        used_mem[best_machine] += mem_req[i]

    return assignment