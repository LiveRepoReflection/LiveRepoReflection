# Task Scheduler

This project implements an optimal task scheduling system for distributed computing environments.

## Overview

The TaskScheduler class schedules tasks optimally on a set of worker nodes, respecting task dependencies and deadlines while minimizing makespan (total execution time).

## Key Features

- Detects and handles circular dependencies
- Schedules tasks to meet all deadlines when possible
- Optimizes worker assignments based on processing capabilities
- Minimizes the overall makespan of the schedule
- Respects all task dependencies

## Algorithm

The implementation uses several algorithms:

1. **Topological Sort** - To order tasks based on dependencies
2. **Critical Path Method** - To calculate earliest start times for each task
3. **Priority-based Assignment** - To assign tasks to most suitable workers

## Classes

- **TaskScheduler** - Main class implementing the scheduling algorithm
- **Task** - Represents a task with processing time, deadline and dependencies
- **Worker** - Represents a worker node with processing capability
- **Assignment** - Represents the assignment of a task to a worker with start and end times

## Time Complexity

The overall time complexity is O(n log m), where:
- n is the number of tasks
- m is the number of workers

This is achieved through efficient prioritization and graph processing.