## Question: Optimal Task Scheduling with Dependencies and Deadlines

### Question Description

You are given a set of `N` tasks. Each task `i` has the following properties:

*   `id_i`: A unique integer identifier for the task (1 <= `id_i` <= N).
*   `duration_i`: An integer representing the time (in arbitrary units) required to complete the task.
*   `deadline_i`: An integer representing the deadline for the task. The task must be completed by this time.
*   `dependencies_i`: A list of task IDs that must be completed before task `i` can start.

Your goal is to find a schedule for completing all `N` tasks such that the total *lateness* is minimized. The lateness of a task is defined as `max(0, completion_time - deadline)`. The *total lateness* is the sum of the lateness of all tasks.

**Constraints:**

*   You can only work on one task at a time.
*   You must respect all dependencies. A task cannot start until all its dependencies are completed.
*   All tasks are available to be scheduled from time 0.
*   The number of tasks `N` can be large (up to 100,000).
*   The `duration_i` and `deadline_i` values can be large (up to 1,000,000,000).
*   The number of dependencies for each task can vary.
*   Cycles in the dependencies are **not** allowed.

**Input:**

The input will be provided as a list of tasks. Each task is represented by a tuple (or similar data structure, depending on the language) containing `id_i`, `duration_i`, `deadline_i`, and `dependencies_i`.

**Output:**

Your function should return the minimum total lateness achievable by scheduling all the tasks.

**Example:**

Let's say you have the following tasks:

*   Task 1: id=1, duration=5, deadline=10, dependencies=[]
*   Task 2: id=2, duration=3, deadline=12, dependencies=[1]
*   Task 3: id=3, duration=7, deadline=20, dependencies=[1, 2]
*   Task 4: id=4, duration=2, deadline=15, dependencies=[]

A possible schedule could be:

1.  Task 1 (0-5)
2.  Task 4 (5-7)
3.  Task 2 (7-10)
4.  Task 3 (10-17)

Latenesses:

*   Task 1: max(0, 5-10) = 0
*   Task 4: max(0, 7-15) = 0
*   Task 2: max(0, 10-12) = 0
*   Task 3: max(0, 17-20) = 0

Total Lateness: 0

However, depending on the algorithm used, other schedules might exist with potentially different lateness values. The goal is to find the *minimum* possible total lateness.

**Efficiency Requirements:**

Your solution should be efficient enough to handle a large number of tasks (up to 100,000) within a reasonable time limit.  Consider the time complexity of your algorithm carefully. Naive solutions might time out for larger inputs.

**Judging Criteria:**

Your solution will be judged based on its correctness (producing the minimum possible total lateness) and its efficiency (running within the time limit for various test cases, including large inputs). Corner cases and edge cases will be heavily tested.
