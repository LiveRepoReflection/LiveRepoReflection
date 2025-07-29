import asyncio
import logging
from collections import defaultdict, deque

logging.basicConfig(filename="scheduler.log", level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

class CycleError(Exception):
    pass

async def run_scheduler(tasks, num_workers, max_concurrency_per_worker, execution_times, task_failures):
    total_concurrency = num_workers * max_concurrency_per_worker
    semaphore = asyncio.Semaphore(total_concurrency)
    lock = asyncio.Lock()
    
    # Initialize task state: status can be "pending", "success", "failed", "skipped"
    statuses = {tid: "pending" for tid in tasks}
    
    # Build dependency graph: in_degree and children mapping.
    in_degree = {}
    children = defaultdict(list)
    for tid, details in tasks.items():
        deps = details.get("dependencies", [])
        in_degree[tid] = len(deps)
        for dep in deps:
            children[dep].append(tid)
    
    # Cycle detection using Kahn's algorithm.
    queue = deque([tid for tid in tasks if in_degree[tid] == 0])
    processed = 0
    temp_in_degree = in_degree.copy()
    while queue:
        current = queue.popleft()
        processed += 1
        for child in children[current]:
            temp_in_degree[child] -= 1
            if temp_in_degree[child] == 0:
                queue.append(child)
    if processed != len(tasks):
        raise CycleError("A cycle was detected in the task dependencies.")
    
    # Priority queue for tasks: (priority, task_id)
    ready_queue = asyncio.PriorityQueue()
    
    # Initially add tasks with no dependencies
    for tid, details in tasks.items():
        if in_degree[tid] == 0:
            await ready_queue.put((details.get("priority", 1000), tid))
    
    # Dictionary to store original dependencies for checking dependency outcomes.
    task_dependencies = {tid: list(tasks[tid].get("dependencies", [])) for tid in tasks}
    
    async def process_task(tid):
        task_detail = tasks[tid]
        func_name = task_detail.get("function")
        delay = execution_times.get(func_name, 1)
        logging.info(f"Task {tid} started. Function: {func_name}")
        
        # Acquire semaphore slot
        async with semaphore:
            try:
                await asyncio.sleep(delay)
                if task_failures.get(tid, False):
                    raise Exception(f"Task {tid} simulated failure.")
                async with lock:
                    statuses[tid] = "success"
                logging.info(f"Task {tid} completed successfully.")
            except Exception as e:
                async with lock:
                    statuses[tid] = "failed"
                logging.error(f"Task {tid} failed with error: {e}")
        # After task completion, update children tasks
        async with lock:
            for child in children[tid]:
                in_degree[child] -= 1
                if in_degree[child] == 0:
                    # Check dependency statuses of child
                    deps = task_dependencies[child]
                    if any(statuses[dep] != "success" for dep in deps):
                        statuses[child] = "skipped"
                        logging.info(f"Task {child} skipped due to dependency failure.")
                        # Even though skipped, still need to propagate to its children.
                        for grandchild in children[child]:
                            in_degree[grandchild] -= 1
                    else:
                        await ready_queue.put((tasks[child].get("priority", 1000), child))
    
    # Set to track running asyncio Tasks.
    running_tasks = set()
    
    # Main scheduling loop: schedule tasks as they become ready.
    while True:
        async with lock:
            # If no task is ready and no tasks are pending in the ready_queue
            all_done = all(status in ("success", "failed", "skipped") for status in statuses.values())
        if all_done:
            break
        # Schedule all tasks from ready_queue.
        while not ready_queue.empty():
            priority, task_id = await ready_queue.get()
            # Only schedule if the task is still pending.
            async with lock:
                if statuses[task_id] != "pending":
                    continue
            task_coro = process_task(task_id)
            task_obj = asyncio.create_task(task_coro)
            running_tasks.add(task_obj)
            # Remove completed tasks from running_tasks.
            task_obj.add_done_callback(lambda t: running_tasks.discard(t))
        if running_tasks:
            # Wait a short interval for tasks to progress.
            await asyncio.sleep(0.1)
        else:
            # No running tasks but not all tasks finished implies they were skipped.
            break

    # For any task that remains pending (could not be scheduled because dependency skipped), mark as skipped.
    async with lock:
        for tid in statuses:
            if statuses[tid] == "pending":
                statuses[tid] = "skipped"
                logging.info(f"Task {tid} marked as skipped due to unresolved dependencies.")
    return statuses