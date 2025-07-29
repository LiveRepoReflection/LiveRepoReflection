# Task Master

## Overview

Task Master is a distributed task scheduler that efficiently allocates tasks to worker nodes while respecting task priorities and dependencies, and handling worker failures gracefully. The scheduler aims to minimize the total execution time (makespan) while ensuring task dependencies and priorities are respected.

## Features

- **Priority-based scheduling**: Tasks with higher priority (lower priority value) are scheduled first
- **Dependency management**: Tasks are only scheduled after all their dependencies have been completed
- **Fault tolerance**: Handles worker failures by rescheduling failed tasks
- **Visualization**: Provides Gantt chart visualization of the task schedule and dependency graph

## Usage
