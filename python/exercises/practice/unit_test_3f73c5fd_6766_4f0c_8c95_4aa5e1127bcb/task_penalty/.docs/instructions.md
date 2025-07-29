## Question: Optimal Task Scheduling with Dependencies and Deadlines

### Project Name:

`optimal-task-scheduler`

### Question Description:

You are given a set of `N` tasks to be scheduled on a single processor. Each task `i` has the following attributes:

*   `id_i`: A unique integer identifier for the task (1 <= `id_i` <= N).
*   `duration_i`: The time (in arbitrary units) required to execute the task.
*   `deadline_i`: The time by which the task must be completed.
*   `penalty_i`: The penalty incurred if the task is completed after its deadline.
*   `dependencies_i`: A list of task `id`s that must be completed before task `i` can start.

Your goal is to determine the optimal schedule that minimizes the total penalty incurred due to late tasks. The schedule must respect the task dependencies.  The tasks must be executed one at a time with no preemption.

**Input:**

You are given a list of `N` tasks, where each task is represented as a tuple:

`(id_i, duration_i, deadline_i, penalty_i, dependencies_i)`

**Constraints:**

*   1 <= `N` <= 20
*   1 <= `duration_i` <= 100
*   1 <= `deadline_i` <= 1000
*   0 <= `penalty_i` <= 1000
*   Dependencies form a directed acyclic graph (DAG).  There will be no circular dependencies.
*   Task IDs are unique and range from 1 to N.
*   The input list is not necessarily sorted by task ID.

**Output:**

Return the *minimum* total penalty achievable by scheduling the tasks in a valid order, respecting dependencies and deadlines.

**Example:**

```python
tasks = [
    (1, 5, 10, 20, []),
    (2, 3, 15, 10, [1]),
    (3, 2, 12, 30, [1]),
    (4, 4, 20, 5, [2, 3]),
]

# Expected Output (Illustrative - the actual optimal order may differ):
# One possible optimal schedule is: 1 -> 3 -> 2 -> 4
# Total penalty: 0 (all tasks complete before their deadlines)
# Another possible schedule: 1 -> 2 -> 3 -> 4
# Total penalty: 0 (all tasks complete before their deadlines)
# A less optimal schedule: 3 -> 1 -> 2 -> 4
# Total penalty: 20 (task 1 is late, so 20 penalty)

#Note that the correct solution should return the minimum achievable penalty over all possible schedules.
```

**Judging Criteria:**

*   Correctness: Your solution must return the correct minimum penalty for all valid input task sets.
*   Efficiency: Given the small input size, a brute-force approach with memoization or dynamic programming is expected.  Solutions that are excessively slow (e.g., exponential time without memoization) will likely time out.
*   Handling Edge Cases: Ensure your code handles cases with no dependencies, all tasks having the same deadline, or cases where no schedule can avoid penalties.

**Bonus:**

Can you adapt your solution to handle a slightly larger number of tasks (e.g., N <= 25) with optimized memoization techniques?
