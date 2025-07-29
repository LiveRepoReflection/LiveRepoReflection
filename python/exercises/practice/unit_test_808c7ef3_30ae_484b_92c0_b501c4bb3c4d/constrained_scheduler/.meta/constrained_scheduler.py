import heapq
from collections import defaultdict, deque

def schedule_tasks(tasks, machines):
    if not machines:
        raise ValueError("No machines available.")

    # Build machine lookup and filter out machines that can never run any task requirement.
    machine_lookup = {}
    for m in machines:
        machine_lookup[m["machine_id"]] = {
            "total_cpu_cores": m["total_cpu_cores"],
            "total_memory_gb": m["total_memory_gb"],
            # Maintain a list of scheduled intervals: each is (start, end, cpu_cores, memory_gb)
            "intervals": []
        }
    
    # Build task lookup and dependencies graph.
    task_lookup = {}
    graph = defaultdict(list)
    in_degree = {}
    for t in tasks:
        task_lookup[t["task_id"]] = t
        in_degree[t["task_id"]] = len(t["dependencies"])
        for dep in t["dependencies"]:
            graph[dep].append(t["task_id"])
    
    # Topological sort (Kahn's algorithm)
    queue = deque([tid for tid in in_degree if in_degree[tid] == 0])
    topo_order = []
    while queue:
        tid = queue.popleft()
        topo_order.append(tid)
        for neigh in graph[tid]:
            in_degree[neigh] -= 1
            if in_degree[neigh] == 0:
                queue.append(neigh)
    
    if len(topo_order) != len(tasks):
        raise ValueError("Cycle detected in task dependencies.")
    
    # Dictionary to store the finish time of each task
    task_finish_time = {}

    # Result schedule: task_id -> (machine_id, start_time, end_time)
    schedule = {}

    # Process tasks in topological order.
    for tid in topo_order:
        task = task_lookup[tid]
        # Check if any machine can ever satisfy the basic resource demands.
        valid_machine_found = False
        for m in machine_lookup.values():
            if m["total_cpu_cores"] >= task["cpu_cores"] and m["total_memory_gb"] >= task["memory_gb"]:
                valid_machine_found = True
                break
        if not valid_machine_found:
            raise ValueError(f"Task {tid} requires more resources than any available machine.")
        
        # Earliest possible start time based on dependencies.
        earliest_start = 0.0
        for dep in task["dependencies"]:
            earliest_start = max(earliest_start, task_finish_time[dep])
        
        # For each machine, find earliest slot >= earliest_start that can host the task.
        best_machine = None
        best_start = None
        best_end = None
        for machine_id, machine in machine_lookup.items():
            # Skip machine if basic capacity not sufficient.
            if machine["total_cpu_cores"] < task["cpu_cores"] or machine["total_memory_gb"] < task["memory_gb"]:
                continue
            candidate_start = find_earliest_slot(machine, task, earliest_start)
            if candidate_start is not None:
                candidate_end = candidate_start + task["estimated_runtime"]
                if best_end is None or candidate_end < best_end:
                    best_machine = machine_id
                    best_start = candidate_start
                    best_end = candidate_end

        if best_machine is None:
            raise ValueError(f"Cannot schedule task {tid} due to resource constraints.")
        
        # Record the scheduled task.
        schedule[tid] = (best_machine, best_start, best_end)
        task_finish_time[tid] = best_end
        # Update the chosen machine's scheduled intervals.
        machine_lookup[best_machine]["intervals"].append((best_start, best_end, task["cpu_cores"], task["memory_gb"]))
        # Keep intervals sorted by start time for easier timeline checking.
        machine_lookup[best_machine]["intervals"].sort(key=lambda x: x[0])
    
    return schedule

def find_earliest_slot(machine, task, candidate_start):
    """
    For a given machine, task, and earliest possible start time, find the earliest start time
    such that the task can be scheduled continuously for its estimated_runtime without exceeding resource capacity.
    machine: dict with keys "total_cpu_cores", "total_memory_gb", "intervals" (list of (start, end, cpu, mem))
    task: dict with keys "cpu_cores", "memory_gb", "estimated_runtime"
    Returns: earliest start time (float) if possible, else None.
    """
    duration = task["estimated_runtime"]
    total_cpu = machine["total_cpu_cores"]
    total_mem = machine["total_memory_gb"]
    scheduled = machine["intervals"]

    # Gather candidate time points: all interval boundaries that are >= candidate_start.
    candidate_times = {candidate_start}
    for interval in scheduled:
        start, end, _, _ = interval
        if start >= candidate_start:
            candidate_times.add(start)
        if end >= candidate_start:
            candidate_times.add(end)
    candidate_times = sorted(candidate_times)

    # Check for each candidate start time if task can be scheduled.
    for start_time in candidate_times:
        # Check the candidate window from start_time to start_time+duration.
        end_time = start_time + duration
        if is_slot_feasible(scheduled, start_time, end_time, task, total_cpu, total_mem):
            return start_time
    # Also consider if there are no scheduled intervals after candidate_start.
    if not scheduled:
        return candidate_start
    # If last candidate time doesn't lead to a fit, consider starting after the last scheduled interval.
    last_end = max(interval[1] for interval in scheduled if interval[1] >= candidate_start) if scheduled else candidate_start
    test_time = max(candidate_start, last_end)
    if is_slot_feasible(scheduled, test_time, test_time + duration, task, total_cpu, total_mem):
        return test_time

    # If no candidate found, then try a simple incremental search (with a small epsilon increment)
    epsilon = 0.001
    t = candidate_start
    # Set a maximum search limit to avoid infinite loops.
    max_search = candidate_start + 10000
    while t < max_search:
        if is_slot_feasible(scheduled, t, t + duration, task, total_cpu, total_mem):
            return t
        t += epsilon
    return None

def is_slot_feasible(scheduled, candidate_start, candidate_end, task, total_cpu, total_mem):
    """
    Check if the task can be scheduled in the candidate window [candidate_start, candidate_end)
    without exceeding machine resources given the already scheduled intervals.
    scheduled: list of intervals (start, end, cpu, mem)
    task: dict with keys "cpu_cores", "memory_gb", "estimated_runtime"
    """
    # Create events for the candidate window.
    events = []
    # Add candidate window boundaries
    events.append((candidate_start, 0, 0))
    events.append((candidate_end, 0, 0))
    for interval in scheduled:
        s, e, cpu, mem = interval
        # If the interval overlaps the candidate window
        if e <= candidate_start or s >= candidate_end:
            continue
        overlap_start = max(candidate_start, s)
        overlap_end = min(candidate_end, e)
        events.append((overlap_start, cpu, mem))
        events.append((overlap_end, -cpu, -mem))
    # Sort events; if same time, update resource changes together.
    events.sort(key=lambda x: (x[0], x[1], x[2]))
    current_cpu = 0
    current_mem = 0
    prev_time = candidate_start
    for time, cpu_change, mem_change in events:
        # Check over the interval [prev_time, time), the resource usage is constant.
        if prev_time < time:
            if current_cpu + task["cpu_cores"] > total_cpu or current_mem + task["memory_gb"] > total_mem:
                return False
        current_cpu += cpu_change
        current_mem += mem_change
        prev_time = time
    return True