import threading
import time
import heapq
from collections import defaultdict

class ProcessingFailureError(Exception):
    pass

class Record:
    def __init__(self, id, data):
        self.id = id
        self.data = data

class Task:
    def __init__(self, id, priority, memory_required):
        self.id = id
        self.priority = priority
        self.memory_required = memory_required

    # This method should be overridden by subclasses or assigned externally.
    def process(self, record):
        raise NotImplementedError("Subclasses or instances must implement process method.")

def process_dataflow(records, tasks, task_dependencies, record_dependencies, P, M, max_retries, initial_backoff):
    # Mapping record and task ids to instances
    record_map = {record.id: record for record in records}
    task_map = {task.id: task for task in tasks}

    # Build job graph: each job is defined by (record_id, task_id)
    # prerequisites: count of jobs that must complete before this job can start.
    # dependents: mapping from job_key to list of job_keys that depend on it.
    prereq_count = {}
    dependents = defaultdict(list)
    all_jobs = []
    # Create list of jobs:
    for r in records:
        for t in tasks:
            job_key = (r.id, t.id)
            count = 0
            # Task dependencies: For each dependency task d that task t depends on,
            # if d is among tasks, then (r, d) must complete before (r, t) starts.
            for dep in task_dependencies.get(t.id, []):
                if dep in task_map:
                    count += 1
                    dep_job = (r.id, dep)
                    dependents[dep_job].append(job_key)
            # Record dependencies: For each record dependency: if record r depends on r2,
            # then (r2, t) must complete before (r, t) starts, if r2 exists in our records.
            for dep_record in record_dependencies.get(r.id, []):
                if dep_record in record_map:
                    count += 1
                    dep_job = (dep_record, t.id)
                    dependents[dep_job].append(job_key)
            prereq_count[job_key] = count
            all_jobs.append(job_key)

    total_jobs = len(all_jobs)
    # Shared state variables
    available_memory = M
    completed_jobs = 0
    error_flag = None

    # Ready queue: min-heap keyed by (-priority, record_id, task_id) so that
    # highest priority is at the top. Each entry: ( -priority, record_id, task_id )
    ready_queue = []
    # job_attempts: mapping from job_key to number of attempts done.
    job_attempts = defaultdict(int)

    # For each job with prereq_count == 0, add to ready_queue.
    for job in all_jobs:
        if prereq_count[job] == 0:
            # Priority: use task priority, we want max priority first, so use negative.
            task_instance = task_map[job[1]]
            heapq.heappush(ready_queue, (-task_instance.priority, job[0], job[1]))

    # Lock and condition for managing ready_queue and shared state.
    lock = threading.Condition()

    # For mapping job keys to their associated record and task
    def get_job_details(job_key):
        r_id, t_id = job_key
        return record_map[r_id], task_map[t_id]

    # To help locate a job in the ready_queue, we maintain a set of job_keys in ready_queue.
    ready_set = set()
    for entry in ready_queue:
        ready_set.add((entry[1], entry[2]))

    def worker():
        nonlocal available_memory, completed_jobs, error_flag
        while True:
            with lock:
                # Wait until there's at least one ready job that can run under memory constraints,
                # or all jobs are processed, or an error occurred.
                while True:
                    if error_flag is not None:
                        return
                    if completed_jobs == total_jobs:
                        return
                    candidate_index = None
                    # Since ready_queue is a heap, we need to scan for a candidate that fits memory.
                    for index, entry in enumerate(ready_queue):
                        # entry structure: (-priority, record_id, task_id)
                        job_key = (entry[1], entry[2])
                        record_inst, task_inst = get_job_details(job_key)
                        if task_inst.memory_required <= available_memory:
                            candidate_index = index
                            break
                    if candidate_index is not None:
                        break
                    # No candidate found; wait until memory is freed or new job added.
                    lock.wait()
                # Pop candidate from heap. Since heapq does not support removal at arbitrary index,
                # we remove by popping all elements until we find the candidate.
                temp = []
                candidate_entry = None
                while ready_queue:
                    entry = heapq.heappop(ready_queue)
                    job_key = (entry[1], entry[2])
                    record_inst, task_inst = get_job_details(job_key)
                    if task_inst.memory_required <= available_memory and candidate_entry is None:
                        candidate_entry = entry
                        ready_set.remove(job_key)
                        break
                    else:
                        temp.append(entry)
                # Push back the entries we popped that were not selected.
                for entry in temp:
                    heapq.heappush(ready_queue, entry)
                if candidate_entry is None:
                    continue
                # Now we have candidate job.
                job_key = (candidate_entry[1], candidate_entry[2])
                record_inst, task_inst = get_job_details(job_key)
                available_memory -= task_inst.memory_required
            # Process the job outside the lock.
            success = False
            attempt = job_attempts[job_key] + 1
            while attempt <= max_retries:
                res = task_inst.process(record_inst)
                if res:
                    success = True
                    break
                else:
                    time_to_sleep = initial_backoff * (2 ** (attempt - 1))
                    time.sleep(time_to_sleep)
                    attempt += 1
            job_attempts[job_key] = attempt
            if not success:
                with lock:
                    error_flag = ProcessingFailureError(f"Task {task_inst.id} failed on Record {record_inst.id} after {max_retries} retries.")
                    lock.notify_all()
                return
            # Job succeeded; update dependency graph and release memory.
            with lock:
                completed_jobs += 1
                available_memory += task_inst.memory_required
                # For each dependent job of the current job, decrement their prereq_count.
                for dependent_job in dependents[job_key]:
                    prereq_count[dependent_job] -= 1
                    if prereq_count[dependent_job] == 0:
                        dep_record, dep_task = get_job_details(dependent_job)
                        entry = (-dep_task.priority, dependent_job[0], dependent_job[1])
                        heapq.heappush(ready_queue, entry)
                        ready_set.add(dependent_job)
                lock.notify_all()
    # Create and start worker threads.
    threads = []
    for _ in range(P):
        t_thread = threading.Thread(target=worker)
        t_thread.start()
        threads.append(t_thread)
    # Wait for all threads to finish.
    for t_thread in threads:
        t_thread.join()
    if error_flag is not None:
        raise error_flag