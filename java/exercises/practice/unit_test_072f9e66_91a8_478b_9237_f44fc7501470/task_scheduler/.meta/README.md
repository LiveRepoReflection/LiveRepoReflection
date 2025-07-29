# Task Scheduler

This project implements an optimal task scheduling system for a large-scale distributed computing platform. The scheduler aims to maximize the number of tasks completed before their deadlines, while respecting task dependencies and resource constraints.

## Implementation Details

The `TaskScheduler` class uses a priority-based scheduling algorithm with the following features:

1. **Dependency Resolution**: Ensures tasks are only scheduled after all of their dependencies have been completed.
2. **Resource Management**: Allocates and releases resources based on task requirements and completions.
3. **Priority-based Selection**: Prioritizes tasks using a combination of Earliest Deadline First (EDF) and Shortest Job First (SJF) policies.
4. **Deadlock Avoidance**: Detects and avoids circular dependencies that could lead to deadlocks.
5. **Deadline Validation**: Ensures all scheduled tasks can complete before their deadlines.

The algorithm uses a greedy approach with look-ahead capability to find a valid schedule that maximizes the number of tasks completed before their deadlines.

## Time Complexity

- Building dependency graph: O(n), where n is the number of tasks
- Deadlock detection: O(n + e), where e is the number of dependency edges
- Task scheduling: O(n²), as for each task we need to evaluate all remaining tasks

Overall complexity: O(n²)

## Space Complexity

- O(n + e) for storing the dependency graph and various tracking data structures

## Usage
