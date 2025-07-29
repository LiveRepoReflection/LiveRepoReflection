## Question: Optimal Task Scheduling with Dependencies and Deadlines

### Question Description

You are given a set of `N` tasks to be scheduled on a single processor. Each task `i` has the following properties:

*   `id[i]`: A unique identifier for the task (integer).
*   `duration[i]`: The time (in milliseconds) required to complete the task (integer).
*   `deadline[i]`: The deadline (in milliseconds) by which the task must be completed (integer). The deadline is relative to the start of the scheduling process (time 0).
*   `dependencies[i]`: A list of task `id`s that must be completed before task `i` can start. This forms a Directed Acyclic Graph (DAG).

Your goal is to determine a schedule that minimizes the total *lateness* of all tasks. Lateness is defined as `max(0, completion_time - deadline)`.

If a task cannot be completed by its deadline, the lateness is the difference between its completion time and deadline. The total lateness is the sum of the lateness of all tasks.

**Constraints:**

1.  **Dependency Constraint:** A task can only start after all its dependencies have been completed.
2.  **Single Processor Constraint:** Only one task can be executed at any given time.
3.  **Non-preemption:** Once a task starts executing, it must run to completion without interruption.

**Input:**

The input will be a JavaScript array of task objects, structured as follows:

```javascript
const tasks = [
  { id: 1, duration: 10, deadline: 50, dependencies: [] },
  { id: 2, duration: 20, deadline: 100, dependencies: [1] },
  { id: 3, duration: 15, deadline: 60, dependencies: [1] },
  { id: 4, duration: 25, deadline: 120, dependencies: [2, 3] },
];
```

**Output:**

Your function should return the *minimum total lateness* achievable by any valid schedule. If it's impossible to complete all tasks while respecting dependencies, return `-1`.

**Optimization Requirements:**

*   The number of tasks `N` can be up to 15.
*   The algorithm must be efficient enough to handle all possible task combinations within a reasonable time limit (e.g., a few seconds). Brute-force solutions are unlikely to pass all test cases.
*   Consider techniques like dynamic programming or branch and bound to prune the search space.

**Example:**

For the input above, a possible optimal schedule is:

1.  Task 1 (duration 10, completion time 10, lateness 0)
2.  Task 3 (duration 15, completion time 25, lateness 0)
3.  Task 2 (duration 20, completion time 45, lateness 0)
4.  Task 4 (duration 25, completion time 70, lateness 0)

Total lateness: 0

Another possible valid schedule is:
1. Task 1 (duration 10, completion time 10, lateness 0)
2. Task 2 (duration 20, completion time 30, lateness 0)
3. Task 3 (duration 15, completion time 45, lateness 0)
4. Task 4 (duration 25, completion time 70, lateness 0)

Total lateness: 0

**Edge Cases to Consider:**

*   Cyclic dependencies (should result in a return of -1).
*   Tasks with deadlines in the past (relative to time 0).
*   Empty task list.
*   Tasks with zero duration.
*   Tasks with very large durations or deadlines.

Good luck!
