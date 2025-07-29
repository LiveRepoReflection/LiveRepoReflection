/**
 * Schedules tasks to maximize the number of tasks completed before their deadlines.
 * Each task has an id, executionTime, deadline, and dependencies.
 * Tasks that are part of a cycle are removed.
 * Tasks are scheduled greedily from those with all dependencies met,
 * prioritizing earliest deadline, then fewer original dependencies, then smaller id.
 *
 * @param {Array} tasks - Array of task objects.
 * @param {number} currentTime - The starting time in milliseconds.
 * @returns {Array} - An array of task ids representing the schedule.
 */
function scheduleTasks(tasks, currentTime) {
  // Create a map of task id to task object.
  const taskMap = new Map();
  tasks.forEach(task => {
    // Record original dependency count for tie-breaking.
    taskMap.set(task.id, { ...task, origDepCount: task.dependencies.length });
  });

  // Build the dependency graph: mapping each task id to its direct dependents.
  const dependents = new Map();
  taskMap.forEach((_, id) => {
    dependents.set(id, []);
  });
  taskMap.forEach((task) => {
    task.dependencies.forEach(dep => {
      if (taskMap.has(dep)) {
        dependents.get(dep).push(task.id);
      }
    });
  });

  // Cycle detection using Kahn's algorithm.
  const inDegree = new Map();
  taskMap.forEach((task, id) => {
    // Only count dependencies that exist in taskMap.
    const count = task.dependencies.filter(dep => taskMap.has(dep)).length;
    inDegree.set(id, count);
  });

  const queue = [];
  inDegree.forEach((deg, id) => {
    if (deg === 0) {
      queue.push(id);
    }
  });

  const processed = new Set();
  while (queue.length > 0) {
    const id = queue.shift();
    processed.add(id);
    const children = dependents.get(id) || [];
    children.forEach(childId => {
      if (!inDegree.has(childId)) return;
      inDegree.set(childId, inDegree.get(childId) - 1);
      if (inDegree.get(childId) === 0) {
        queue.push(childId);
      }
    });
  }
  // Remove tasks that are not processed (i.e., in cycles)
  for (const id of taskMap.keys()) {
    if (!processed.has(id)) {
      taskMap.delete(id);
    }
  }

  // Rebuild the dependency graph and dependency counts for the remaining tasks.
  const remainingDependents = new Map();
  const remainingDepsCount = new Map();
  taskMap.forEach((task, id) => {
    // Count only dependencies that are still in taskMap.
    const count = task.dependencies.filter(dep => taskMap.has(dep)).length;
    remainingDepsCount.set(id, count);
    remainingDependents.set(id, []);
  });
  taskMap.forEach((task, id) => {
    task.dependencies.forEach(dep => {
      if (taskMap.has(dep)) {
        remainingDependents.get(dep).push(id);
      }
    });
  });

  // Initialize the list of available tasks (those with no unsatisfied dependencies).
  let available = [];
  remainingDepsCount.forEach((count, id) => {
    if (count === 0) {
      available.push(taskMap.get(id));
    }
  });
  // Sorting based on: earliest deadline, then fewer original dependencies, then smaller id.
  const sortAvailable = () => {
    available.sort((a, b) => {
      if (a.deadline !== b.deadline) {
        return a.deadline - b.deadline;
      }
      if (a.origDepCount !== b.origDepCount) {
        return a.origDepCount - b.origDepCount;
      }
      return a.id - b.id;
    });
  };
  sortAvailable();

  const result = [];

  // Simulation: process available tasks in order.
  while (available.length > 0) {
    const task = available.shift();
    // Check if scheduling this task allows completion by its deadline.
    if (currentTime + task.executionTime <= task.deadline) {
      // Schedule the task.
      result.push(task.id);
      currentTime += task.executionTime;
      // For each dependent, decrement the count of unscheduled dependencies.
      const deps = remainingDependents.get(task.id);
      deps.forEach(dependentId => {
        if (!remainingDepsCount.has(dependentId)) return;
        remainingDepsCount.set(dependentId, remainingDepsCount.get(dependentId) - 1);
        // A dependent becomes available only if all of its dependencies have been scheduled.
        if (remainingDepsCount.get(dependentId) === 0) {
          available.push(taskMap.get(dependentId));
        }
      });
      sortAvailable();
    } else {
      // If the task cannot be completed by its deadline, it and its dependent subtree are unschedulable.
      const skipQueue = [task.id];
      while (skipQueue.length > 0) {
        const skipId = skipQueue.shift();
        const depList = remainingDependents.get(skipId);
        depList.forEach(depId => {
          if (remainingDepsCount.has(depId)) {
            // Remove this dependent task from consideration.
            remainingDepsCount.delete(depId);
            skipQueue.push(depId);
          }
        });
      }
    }
  }

  return result;
}

module.exports = { scheduleTasks };