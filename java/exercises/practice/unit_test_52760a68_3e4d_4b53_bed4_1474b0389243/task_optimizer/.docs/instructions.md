## Question: Optimal Task Assignment with Dependencies and Time Constraints

### Problem Description

You are tasked with optimizing the assignment of tasks to a team of engineers, subject to complex dependencies, time constraints, and engineer skill levels.

You are given:

*   `n`: The number of engineers in your team, labeled from `0` to `n-1`.
*   `m`: The number of tasks to be completed, labeled from `0` to `m-1`.
*   `skills[n][k]`: A 2D array representing the skill level of each engineer for different task categories. `skills[i][j]` denotes the skill level of engineer `i` in task category `j`. Higher values indicate better proficiency. Assume `k` is the number of task categories.
*   `tasks[m][2]`: A 2D array where each row represents a task. `tasks[i][0]` is the task category required for task `i`, and `tasks[i][1]` is the time (in hours) required to complete task `i`.
*   `dependencies[m]`: An array of lists representing task dependencies. `dependencies[i]` is a list of task indices that must be completed *before* task `i` can start. A task can have multiple dependencies.
*   `availability[n]`: An array representing the availability of each engineer, where `availability[i]` denotes the number of hours engineer `i` is available to work.
*   `deadline`: The overall deadline (in hours) for completing all tasks.

Your goal is to determine the **minimum total cost** to complete all tasks before the deadline, while respecting dependencies and engineer availability. The cost of assigning a task to an engineer is inversely proportional to the engineer's skill level in the task's category. Specifically, the cost of assigning task `i` to engineer `j` is `tasks[i][1] / skills[j][tasks[i][0]]`. If `skills[j][tasks[i][0]]` is 0, it means the engineer cannot perform the task, and the cost is considered infinite.

**Constraints:**

*   Each task must be assigned to exactly one engineer.
*   An engineer can work on multiple tasks, but not simultaneously.
*   Task dependencies must be strictly adhered to. A task cannot start until all its dependencies are completed.
*   Engineer availability cannot be exceeded.
*   All tasks must be completed by the given `deadline`.
*   `1 <= n <= 10`
*   `1 <= m <= 20`
*   `0 <= skills[i][j] <= 10`
*   `1 <= tasks[i][1] <= 10`
*   `0 <= dependencies[i].length < m`
*   `1 <= availability[i] <= 50`
*   `1 <= deadline <= 500`
*   It is guaranteed that all tasks can be completed within the deadline if assigned optimally.

**Input:**

*   `n`: The number of engineers (integer).
*   `m`: The number of tasks (integer).
*   `skills`: A 2D integer array representing engineer skills.
*   `tasks`: A 2D integer array representing task categories and durations.
*   `dependencies`: A list of lists representing task dependencies.
*   `availability`: An integer array representing engineer availability.
*   `deadline`: The overall deadline (integer).

**Output:**

*   The minimum total cost to complete all tasks before the deadline (double). Return `-1.0` if it's impossible to complete all tasks.

**Challenge:**

The complexity arises from the combination of task dependencies, engineer availability, the need to minimize cost based on varying skill levels, and the deadline constraint. Efficiently exploring the search space of possible task assignments while respecting all constraints is the core challenge. You need to carefully consider how to represent the task schedule, track dependencies, and evaluate the overall cost and feasibility of a given assignment. Dynamic Programming, graph algorithms or backtracking with pruning could be potential approaches. The small input sizes allows for less performant but still correct solutions; however, aiming for good time complexity will separate good solutions from excellent ones.
