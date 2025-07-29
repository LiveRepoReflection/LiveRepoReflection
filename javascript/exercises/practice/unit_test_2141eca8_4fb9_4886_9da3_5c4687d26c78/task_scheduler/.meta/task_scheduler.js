'use strict';

function scheduleTasks(tasks, penaltyWeight) {
  // Build tasks map, inDegree count, and dependency graph.
  const tasksMap = {};
  const inDegree = {};
  const graph = {};

  for (const task of tasks) {
    tasksMap[task.id] = task;
    inDegree[task.id] = task.dependencies.length;
    graph[task.id] = [];
  }

  // Build graph: for each task, add an edge from each dependency to this task.
  for (const task of tasks) {
    for (const dep of task.dependencies) {
      // If dependency is missing from tasks, the input is invalid.
      if (!(dep in graph)) {
        return null;
      }
      graph[dep].push(task.id);
    }
  }

  // Initialize available tasks (those with zero unsatisfied dependencies).
  const available = [];
  for (const id in inDegree) {
    if (inDegree[id] === 0) {
      available.push(tasksMap[Number(id)]);
    }
  }

  // Helper function to sort available tasks by deadline then lexicographically by id.
  const sortAvailable = () => {
    available.sort((a, b) => {
      if (a.deadline !== b.deadline) {
        return a.deadline - b.deadline;
      }
      return a.id - b.id;
    });
  };

  sortAvailable();

  const schedule = [];
  let currentTime = 0;

  // Process tasks in a greedy manner based on earliest deadline among available tasks.
  while (available.length > 0) {
    const task = available.shift();
    schedule.push(task.id);
    currentTime += task.duration;

    // For each task that depends on the current task, decrement its in-degree.
    for (const neighborId of graph[task.id]) {
      inDegree[neighborId]--;
      if (inDegree[neighborId] === 0) {
        available.push(tasksMap[neighborId]);
      }
    }
    sortAvailable();
  }

  // If schedule doesn't include all tasks, a cycle exists.
  if (schedule.length !== tasks.length) {
    return null;
  }

  return schedule;
}

module.exports = { scheduleTasks };