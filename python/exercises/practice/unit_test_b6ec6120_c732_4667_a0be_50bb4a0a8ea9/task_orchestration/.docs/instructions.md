## Question: Asynchronous Task Orchestration with Dependency Resolution

### Question Description

You are building a distributed task processing system where tasks have dependencies on each other. Each task performs a specific operation and produces a result. The system needs to execute these tasks in a way that respects their dependencies, maximizes parallelism, and handles potential failures gracefully.

You are given a directed acyclic graph (DAG) representing the tasks and their dependencies. Each node in the graph represents a task, and each edge represents a dependency: Task `A` -> Task `B` means Task `B` depends on the output of Task `A`. A task can only start execution once all its dependencies have been successfully completed.

Each task is represented by a unique ID (integer) and a function that simulates the task's execution. This function takes a dictionary of task results (keyed by task ID) as input (representing the results of its dependencies) and returns a result (of any type). If a task fails during execution, the function should raise an exception.

Your task is to implement a function `orchestrate_tasks(task_graph, task_functions, max_workers)` that takes the following arguments:

*   `task_graph`: A dictionary representing the DAG. Keys are task IDs (integers), and values are lists of task IDs that are dependencies of the key task. For example, `{1: [], 2: [1], 3: [1, 2]}` represents a graph where task 1 has no dependencies, task 2 depends on task 1, and task 3 depends on tasks 1 and 2.

*   `task_functions`: A dictionary mapping task IDs (integers) to functions. Each function takes a dictionary of dependency results as input and returns a result.

*   `max_workers`: An integer representing the maximum number of tasks that can be executed concurrently.

The `orchestrate_tasks` function should:

1.  Execute the tasks in the `task_graph` in a way that respects their dependencies.

2.  Maximize parallelism by executing independent tasks concurrently, up to the `max_workers` limit.

3.  Handle task failures gracefully. If a task fails (raises an exception), all tasks that depend on it should be marked as failed and not executed.

4.  Return a dictionary mapping task IDs to their results. If a task failed, its value in the dictionary should be `None`.

**Constraints and Requirements:**

*   The `task_graph` is guaranteed to be a valid DAG (no cycles).
*   The task functions are assumed to be independent of each other (no shared mutable state).
*   The system should be designed to be resilient to individual task failures. A single task failure should not bring down the entire system.
*   The solution should be efficient and minimize the overall execution time. Consider using concurrency (e.g., threads, processes, or asyncio) to achieve parallelism.
*   You must handle potential race conditions appropriately if using threads.
*   Assume that the task functions can take a variable amount of time to execute (some may be quick, others may be slow).
*   The return dictionary should contain *all* task IDs from the task graph, even if the tasks failed.

**Example:**

```python
task_graph = {
    1: [],
    2: [1],
    3: [1],
    4: [2, 3],
    5: [4]
}

def task_func_1(dependencies):
  return 10

def task_func_2(dependencies):
  return dependencies[1] * 2

def task_func_3(dependencies):
  return dependencies[1] + 5

def task_func_4(dependencies):
  return dependencies[2] + dependencies[3]

def task_func_5(dependencies):
  return dependencies[4] * 3

task_functions = {
    1: task_func_1,
    2: task_func_2,
    3: task_func_3,
    4: task_func_4,
    5: task_func_5
}

max_workers = 2

results = orchestrate_tasks(task_graph, task_functions, max_workers)

# Expected Output (order may vary):
# {1: 10, 2: 20, 3: 15, 4: 35, 5: 105}
```

**Bonus:**

*   Implement a mechanism to retry failed tasks (up to a certain number of retries).
*   Implement a mechanism to monitor the progress of the task execution (e.g., display a progress bar).
*   Consider the implications of memory management when dealing with large task results. How would you handle tasks that produce very large outputs?
*   How would you adapt the solution to work in a distributed environment, where tasks are executed on different machines?

This problem requires a good understanding of asynchronous programming, dependency management, error handling, and concurrency. It's designed to be challenging and requires careful consideration of various design trade-offs. Good luck!
