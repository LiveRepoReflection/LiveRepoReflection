def assign_tasks(current_time, tasks, workers):
    """
    Assigns tasks to worker nodes to minimize the total cost while meeting deadlines and resource constraints.
    
    Parameters:
        current_time (int): The current system time.
        tasks (list of tuples): Each tuple is (task_id, deadline, duration, cpu, memory, network).
        workers (list of tuples): Each tuple is (worker_id, cpu_capacity, memory_capacity, network_capacity, cost_per_unit_time).
    
    Returns:
        dict: A dictionary mapping task_id to worker_id for the optimal assignment.
              Returns an empty dictionary if no feasible assignment exists.
    """
    # Preprocess: For each worker, store available_time (initially current_time).
    # Also, convert worker info into a dict mapping worker_id to its attributes.
    worker_info = {}
    for worker in workers:
        worker_id, cpu_cap, mem_cap, net_cap, cost = worker
        worker_info[worker_id] = {
            "cpu": cpu_cap,
            "memory": mem_cap,
            "network": net_cap,
            "cost": cost,
            "available_time": current_time  # when the worker is free to start a new task
        }
    
    # Sort tasks by deadline to prioritize scheduling tasks with tighter deadlines.
    sorted_tasks = sorted(tasks, key=lambda t: t[1])  # deadline t[1]
    
    assignment = {}
    
    for task in sorted_tasks:
        task_id, deadline, duration, required_cpu, required_memory, required_network = task
        
        best_worker_id = None
        best_cost = None
        # Evaluate each worker to check if the task can be scheduled
        for worker in workers:
            worker_id, cpu_cap, mem_cap, net_cap, cost = worker
            # Check resource constraints
            if required_cpu > cpu_cap or required_memory > mem_cap or required_network > net_cap:
                continue
            # Determine start time on this worker
            available_time = worker_info[worker_id]["available_time"]
            start_time = available_time  # tasks are scheduled sequentially
            finish_time = start_time + duration
            # Check if task can be finished before its deadline
            if finish_time > deadline:
                continue
            # Calculate the cost for this task on this worker.
            task_cost = cost * duration
            # Choose the worker with minimal incremental cost.
            if best_worker_id is None or task_cost < best_cost:
                best_worker_id = worker_id
                best_cost = task_cost
            # If cost is the same, select the worker with earlier availability.
            elif task_cost == best_cost and worker_info[worker_id]["available_time"] < worker_info[best_worker_id]["available_time"]:
                best_worker_id = worker_id
        
        # If no feasible worker found, assignment fails; return empty dictionary.
        if best_worker_id is None:
            return {}
        # Otherwise, assign the task to the chosen worker.
        assignment[task_id] = best_worker_id
        # Update the chosen worker's available time.
        worker_info[best_worker_id]["available_time"] += duration
        
    return assignment


if __name__ == '__main__':
    # Example usage:
    # Define some sample tasks and workers.
    current_time = 0
    tasks = [
        (1, 10, 5, 2, 1024, 100),
        (2, 15, 5, 2, 1024, 100),
        (3, 20, 5, 2, 1024, 100)
    ]
    workers = [
        (100, 4, 2048, 200, 0.5),
        (101, 4, 2048, 200, 1.0)
    ]
    result = assign_tasks(current_time, tasks, workers)
    print("Task Assignment:", result)