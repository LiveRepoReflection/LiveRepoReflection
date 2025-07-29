Okay, I'm ready to generate a challenging Java coding problem. Here it is:

**Project Title:**  Optimal Task Scheduling with Dependencies and Deadlines

**Problem Description:**

You are tasked with designing a task scheduling system for a large-scale distributed computing environment.  There are `N` independent tasks that need to be executed. Each task `i` has the following properties:

*   `taskId[i]`: A unique identifier for the task (integer).
*   `executionTime[i]`:  The time (in milliseconds) required to execute the task.
*   `deadline[i]`: The deadline (in milliseconds since the start of the scheduling window) by which the task must be completed.
*   `dependencies[i]`: A list of `taskId`s that must be completed *before* task `i` can start.  This represents task dependencies.  Note that cyclic dependencies are possible, and your solution *must* detect and handle them.

The system has `K` identical worker nodes that can execute tasks in parallel. Each worker node can execute only one task at any given time.

Your goal is to design an algorithm to schedule these tasks on the `K` worker nodes such that:

1.  All tasks are completed.
2.  The number of tasks that miss their deadlines is *minimized*.  This is the primary optimization goal.
3.  All dependencies are satisfied. A task can only start executing if all its dependencies have been completed.
4.  The makespan (total time to complete all tasks) should also be reasonably small, acting as a secondary optimization goal.  While minimizing deadline misses is paramount, try to finish all tasks quickly.

**Input:**

You will receive the following inputs:

*   `N`: The number of tasks (1 <= N <= 100,000).
*   `K`: The number of worker nodes (1 <= K <= 100).
*   `taskId`: An array of `N` unique task IDs (integers).
*   `executionTime`: An array of `N` execution times (integers, milliseconds).
*   `deadline`: An array of `N` deadlines (integers, milliseconds).
*   `dependencies`: A list of lists, where `dependencies[i]` is a list of `taskId`s representing the dependencies of task `i`. `dependencies[i]` can be empty.

**Output:**

Your program should return a list of integers representing the task IDs of the tasks that missed their deadlines. The returned list should be sorted in ascending order. If no tasks miss their deadlines, return an empty list.

**Constraints and Considerations:**

*   **Cyclic Dependencies:**  Your solution *must* detect cyclic dependencies. If cyclic dependencies are present, throw a custom exception `CyclicDependencyException`.
*   **Invalid Task IDs:** The `dependencies` list might contain task IDs that are not present in the `taskId` array. You should ignore such dependencies (treat them as if they don't exist) and log a warning message.
*   **Optimization:**  Finding the *absolute* minimum number of missed deadlines is likely NP-hard. Therefore, you are expected to develop a *heuristic* algorithm that provides a "good" (but not necessarily optimal) solution.  The judge will evaluate your solution based on the number of missed deadlines and the makespan, comparing your solution against other correct submissions.
*   **Efficiency:** Your solution should be efficient enough to handle large input sizes (N = 100,000) within a reasonable time limit (e.g., 10 seconds).  Consider the time complexity of your algorithms and data structures.
*   **Real-world Considerations:** Think about how your scheduling algorithm would behave in a real-world distributed computing environment.  Consider factors like task prioritization, resource contention, and potential for task failures (although you don't need to *implement* failure handling).
*   **Tie-breaking:** If multiple scheduling options appear equally good (e.g., both lead to the same number of missed deadlines), prioritize tasks with earlier deadlines and shorter execution times.
*   **Data Structure Choice:** The choice of data structures is critical for performance. Consider using appropriate data structures for representing tasks, dependencies, and worker node availability.
*   **Handling Zero Execution Time:** If any task has an execution time of 0, it should be scheduled as early as possible to not block other tasks dependent on it.

**Example:**

```
N = 5
K = 2
taskId = [1, 2, 3, 4, 5]
executionTime = [100, 50, 75, 25, 125]
deadline = [200, 150, 250, 100, 300]
dependencies = [[], [1], [2], [1, 2], [3, 4]]

// Possible Solution (not necessarily optimal):
// Tasks 1 and 4 are scheduled on worker nodes initially.
// Tasks 2 and 3 are scheduled after task 1 finishes.
// Task 5 is scheduled after tasks 3 and 4 finish.

// Expected Output (based on a particular scheduling result):
// [4, 5] (Tasks 4 and 5 missed their deadlines)
```

This problem requires a combination of graph algorithms (for dependency resolution), scheduling heuristics, and careful consideration of data structures and time complexity. Good luck!
