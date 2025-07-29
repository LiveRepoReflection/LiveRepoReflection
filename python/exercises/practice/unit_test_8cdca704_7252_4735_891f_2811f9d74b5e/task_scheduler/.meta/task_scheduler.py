def schedule_tasks(num_nodes, worker_resources, num_tasks, task_requirements, network_bandwidth, execution_times):
    schedule = []
    for i in range(num_tasks):
        cpu_req, mem_req, disk_req, data_size, deadline = task_requirements[i]
        best_node = None
        best_finish_time = float('inf')
        for node in range(num_nodes):
            cpu_avail, mem_avail, disk_avail = worker_resources[node]
            if cpu_avail < cpu_req or mem_avail < mem_req or disk_avail < disk_req:
                continue
            # Calculate transfer penalty. Data is originally at node 0.
            if node == 0:
                transfer_time = 0
            else:
                bandwidth = network_bandwidth[0][node]
                # Given bandwidth is positive according to constraints.
                transfer_time = data_size / bandwidth
            finish_time = execution_times[i][node] + transfer_time
            if finish_time <= deadline and finish_time < best_finish_time:
                best_finish_time = finish_time
                best_node = node
        if best_node is None:
            raise Exception(f"Task {i} cannot be scheduled given its deadline and resource constraints.")
        schedule.append(best_node)
    return schedule

if __name__ == "__main__":
    # Example usage:
    num_nodes = 2
    worker_resources = [(4, 8, 10), (8, 16, 20)]
    num_tasks = 3
    task_requirements = [
        (2, 4, 5, 2, 100),
        (1, 2, 3, 1, 120),
        (3, 6, 7, 3, 150)
    ]
    network_bandwidth = [
        [1e9, 1],
        [1, 1e9]
    ]
    execution_times = [
        [10, 12],
        [15, 13],
        [20, 18]
    ]
    sched = schedule_tasks(num_nodes, worker_resources, num_tasks, task_requirements, network_bandwidth, execution_times)
    print("Schedule:", sched)