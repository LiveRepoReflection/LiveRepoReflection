import threading
import time
import random

def orchestrate_tasks(tasks, num_workers, total_resources, failure_rate):
    start_time = time.time()
    lock = threading.Lock()
    condition = threading.Condition(lock)

    # Build task information maps.
    tasks_info = {task["id"]: task for task in tasks}
    prereq_count = {}
    dependents = {}
    task_states = {}

    for task in tasks:
        tid = task["id"]
        task_states[tid] = "pending"
        prereq_count[tid] = len(task["dependencies"])
        dependents[tid] = []
    for task in tasks:
        for dep in task["dependencies"]:
            dependents[dep].append(task["id"])

    available_resources = total_resources
    worker_semaphore = threading.Semaphore(num_workers)
    running_tasks = 0
    threads = []

    def cancel_dependents(task_id):
        for dep_id in dependents[task_id]:
            if task_states[dep_id] == "pending":
                task_states[dep_id] = "cancelled"
                cancel_dependents(dep_id)

    def run_task(task):
        nonlocal available_resources, running_tasks
        tid = task["id"]
        exec_time = task["execution_time"]
        # Simulate task execution time.
        time.sleep(exec_time)
        with lock:
            # Decide if the task fails based on failure_rate.
            if random.random() < failure_rate:
                task_states[tid] = "failed"
                cancel_dependents(tid)
            else:
                task_states[tid] = "completed"
            # Release the allocated resources.
            available_resources += task["resources_required"]
            # Update prerequisite count for dependents.
            for dep_id in dependents[tid]:
                if task_states[dep_id] == "pending":
                    prereq_count[dep_id] -= 1
            running_tasks -= 1
            condition.notify_all()
        worker_semaphore.release()

    with lock:
        while True:
            unfinished = any(state == "pending" or state == "running" for state in task_states.values())
            if not unfinished and running_tasks == 0:
                break
            scheduled = False
            for tid, state in list(task_states.items()):
                if state == "pending" and prereq_count[tid] == 0 and available_resources >= tasks_info[tid]["resources_required"]:
                    worker_semaphore.acquire()
                    task_states[tid] = "running"
                    available_resources -= tasks_info[tid]["resources_required"]
                    running_tasks += 1
                    t = threading.Thread(target=run_task, args=(tasks_info[tid],))
                    t.start()
                    threads.append(t)
                    scheduled = True
            if not scheduled:
                condition.wait(timeout=0.1)

    for t in threads:
        t.join()
    completion_time = time.time() - start_time
    overall_status = "success" if all(state in ["completed", "cancelled"] for state in task_states.values()) and not any(state == "failed" for state in task_states.values()) else "failure"
    return {"status": overall_status, "completion_time": completion_time, "task_states": task_states}