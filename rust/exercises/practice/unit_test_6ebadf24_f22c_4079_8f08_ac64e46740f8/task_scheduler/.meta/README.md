# Task Scheduler

## Problem Overview

This is a solution to the optimal task scheduling problem with dependencies and deadlines. The problem involves scheduling a set of tasks with dependencies, processing times, and deadlines to minimize the total weighted tardiness.

## Implementation Approach

The solution uses a branch and bound algorithm to explore different task orderings, with several optimizations:

1. **Circular Dependency Detection**: We first check if the task graph contains any circular dependencies, which would make scheduling impossible.

2. **Earliest Start Time Calculation**: For each task, we calculate the earliest possible start time by performing a topological sort of the dependency graph.

3. **Branch and Bound**: We recursively explore different valid schedules, pruning branches that cannot lead to a better solution than the best found so far.

4. **Pruning**: We avoid exploring schedules that already exceed the best tardiness found so far.

## Time Complexity

The worst-case time complexity is O(n!), as we potentially need to explore all valid permutations of tasks. However, the branch and bound approach with pruning significantly reduces the search space in practice.

## Space Complexity

The space complexity is O(n) for storing the schedule and the set of scheduled tasks, plus additional O(n) space for the recursive call stack.