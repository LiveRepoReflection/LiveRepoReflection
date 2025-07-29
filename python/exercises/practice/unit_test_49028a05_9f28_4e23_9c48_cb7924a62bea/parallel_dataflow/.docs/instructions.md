## Question: Parallel Data Processing with Complex Dependencies

### Question Description

You are tasked with designing and implementing a system for processing a large dataset in parallel. The dataset consists of records, each identified by a unique ID. The processing involves a series of tasks, each operating on a subset of the records. Crucially, these tasks have dependencies: some tasks must complete before others can begin, and these dependencies can form complex, cyclic relationships. Furthermore, records can have dependencies among each other, which affects the tasks each record can run on.

Specifically:

1.  **Data Records:** The dataset is a collection of records. Each record `r` has a unique `id` (integer), and some `data` (string).

2.  **Tasks:** There are `N` tasks (numbered 0 to N-1). Each task `t` operates on a set of records.

3.  **Task Dependencies:** A task `t1` may depend on another task `t2`. This means `t1` cannot start processing any record until `t2` has finished processing ALL records that `t1` also processes. Task dependencies can be cyclic.

4.  **Record Dependencies:** A record `r1` may depend on another record `r2`. This means that no task can process record `r1` until all tasks that it shares with record `r2` are completed for record `r2`. Record dependencies can also be cyclic.

5.  **Parallelism:** You have access to `P` worker threads for processing.

6.  **Failure Handling:** Tasks can fail. If a task fails while processing a record, it needs to be retried (with exponential backoff) up to a maximum number of retries. If it persistently fails after max retries, the entire processing should halt, and an error must be raised (e.g. `ProcessingFailureError`).

7.  **Resource Constraints:** Each task requires a certain amount of memory. The total memory used by tasks running concurrently cannot exceed a fixed limit `M`.

8.  **Priorities:** Each task has a priority level associated with it. Higher priority tasks should be prioritized when scheduling. If there is a task and its dependencies are met, and there is enough memory, but there is a lower priority task running, the lower priority task must be preempted and the higher priority task must be run.

Your goal is to implement a system that efficiently processes the dataset in parallel, respecting all dependencies, constraints, and failure handling requirements.

**Input:**

*   A list of records: `records: List[Record]`
*   A list of tasks: `tasks: List[Task]` where each task has a `priority`, `memory_required`, and a function `process(record: Record) -> bool` which returns `True` if process successful and `False` otherwise.
*   A dictionary representing task dependencies: `task_dependencies: Dict[int, List[int]]` where key is the task ID and value is the list of task IDs it depends on.
*   A dictionary representing record dependencies: `record_dependencies: Dict[int, List[int]]` where key is the record ID and value is the list of record IDs it depends on.
*   Number of worker threads: `P: int`
*   Maximum memory limit: `M: int`
*   Maximum retries: `max_retries: int`
*   Initial backoff: `initial_backoff: int`

**Output:**

*   None (The system should process all records successfully or raise a `ProcessingFailureError` if a record persistently fails).

**Constraints:**

*   Implement a robust and efficient parallel processing system.
*   Handle task and record dependencies correctly.
*   Manage resource constraints (memory).
*   Implement exponential backoff and retry mechanism for failed tasks.
*   Gracefully handle cyclic dependencies and avoid deadlocks.
*   Prioritize tasks based on priority level.
*   Ensure the code is thread-safe.
*   Optimize for throughput.
*   The number of records and tasks can be very large (millions).
*   Memory limit `M` is significantly smaller than the total memory required to run all tasks concurrently.
*   All inputs are valid (no negative values, etc.)

**Error Handling:**

*   Raise a custom exception `ProcessingFailureError` if a task fails after `max_retries`.
*   Handle potential deadlocks gracefully (e.g., by detecting cycles in task/record dependencies).

**Example:**

Imagine a scenario where you're processing financial transactions. Tasks could represent different stages of processing (validation, fraud detection, ledger update). Dependencies might exist due to data consistency requirements (e.g., ledger update depends on successful validation). Records could depend on each other if they are linked in a transaction chain.

Good luck! This is a challenging problem that requires careful design and implementation. Consider breaking it down into smaller, manageable components and thinking about the data structures and algorithms you'll need to use.
