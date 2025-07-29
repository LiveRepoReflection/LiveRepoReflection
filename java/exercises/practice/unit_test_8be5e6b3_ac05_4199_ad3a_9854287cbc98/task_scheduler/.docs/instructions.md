## Question: Efficient Task Scheduling with Dependencies and Deadlines

### Question Description

You are tasked with designing an efficient task scheduler for a complex project. The project consists of a set of tasks, each with dependencies on other tasks, a processing time, and a deadline. The scheduler must determine the optimal execution order of tasks to minimize the number of late tasks while respecting all dependencies.

**Task Definition:**

Each task is represented by the following attributes:

*   `id`: A unique integer identifier for the task.
*   `processing_time`: An integer representing the time required to complete the task.
*   `deadline`: An integer representing the latest time by which the task must be completed.
*   `dependencies`: A list of task IDs that must be completed before this task can start.

**Scheduler Requirements:**

1.  **Dependency Constraints:** The scheduler must ensure that all dependencies of a task are completed before the task can be executed.
2.  **Deadline Optimization:** The scheduler must prioritize tasks to minimize the number of tasks that are completed after their deadlines.
3.  **Efficient Execution:** The scheduler must determine an execution order that allows the maximum amount of tasks to be completed on time.
4.  **Handling Circular Dependencies:** The scheduler must detect and handle cases where circular dependencies exist within the task set. If circular dependencies are found, the scheduler should throw an exception.
5.  **Task Cancellation:** A task can be cancelled at any point. If a task is cancelled, all tasks that directly or indirectly depend on it should also be cancelled. Cancelled tasks should not be considered in the final scheduling.

**Input:**

The input consists of:

*   An integer `n` representing the number of tasks.
*   A list of `n` tasks, where each task is represented by its `id`, `processing_time`, `deadline`, and `dependencies`.
*   A list of task IDs to be cancelled.

**Output:**

The output should be an ordered list of task IDs representing the optimal execution order of tasks. If the scheduler cannot find a valid schedule that meets all constraints, it should return an empty list.

**Constraints:**

*   1 <= `n` <= 100,000
*   1 <= `id` <= `n`
*   1 <= `processing_time` <= 10,000
*   1 <= `deadline` <= 1,000,000
*   The number of dependencies for each task is at most 10.
*   Task IDs are unique.

**Example:**

```
n = 4
tasks = [
  {id: 1, processing_time: 2, deadline: 5, dependencies: []},
  {id: 2, processing_time: 3, deadline: 7, dependencies: [1]},
  {id: 3, processing_time: 1, deadline: 4, dependencies: [1]},
  {id: 4, processing_time: 4, deadline: 9, dependencies: [2, 3]}
]
cancelled_tasks = []

Output: [1, 3, 2, 4]
```

**Judging Criteria:**

The solution will be judged based on the following criteria:

*   **Correctness:** The scheduler must produce a valid execution order that respects all dependencies.
*   **Optimization:** The scheduler should minimize the number of late tasks.
*   **Efficiency:** The solution must be able to handle large input sizes within a reasonable time limit.
*   **Robustness:** The solution must handle edge cases, such as circular dependencies and invalid input.
*   **Code Quality:** The code should be well-structured, readable, and maintainable.
