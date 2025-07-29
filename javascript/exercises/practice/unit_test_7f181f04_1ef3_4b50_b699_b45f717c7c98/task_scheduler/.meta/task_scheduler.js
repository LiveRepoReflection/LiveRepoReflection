/**
 * Returns an array of task ids that can be scheduled to finish before their deadlines.
 * The returned schedule is the lexicographically smallest among all optimal schedules.
 *
 * @param {Array} tasks - List of task objects with properties:
 *                        id: number,
 *                        duration: number,
 *                        deadline: number,
 *                        dependencies: number[]
 * @returns {number[]} - Array of task ids in the order they should be executed.
 */
function scheduleTasks(tasks) {
  if (!tasks || tasks.length === 0) return [];

  // Build maps for tasks, graph, in-degrees.
  const taskMap = new Map();
  const graph = new Map();
  const inDegree = new Map();
  for (const task of tasks) {
    taskMap.set(task.id, task);
    inDegree.set(task.id, 0);
    graph.set(task.id, []);
  }

  // Build dependency graph: for each dependency, count in-degree and record outgoing edges.
  for (const task of tasks) {
    for (const dep of task.dependencies) {
      // If dependency doesn't exist in tasks, ignore (or treat as unschedulable)
      if (!taskMap.has(dep)) continue;
      graph.get(dep).push(task.id);
      inDegree.set(task.id, inDegree.get(task.id) + 1);
    }
  }

  // Use Kahn's algorithm with lexicographical order (smallest id first) to get topological order.
  const available = [];
  for (const [id, deg] of inDegree.entries()) {
    if (deg === 0) {
      available.push(id);
    }
  }
  // Sort available tasks by id (ensuring lexicographically smallest order)
  available.sort((a, b) => a - b);
  const topoOrder = [];
  while (available.length > 0) {
    const id = available.shift();
    topoOrder.push(id);
    for (const neighbor of graph.get(id)) {
      inDegree.set(neighbor, inDegree.get(neighbor) - 1);
      if (inDegree.get(neighbor) === 0) {
        available.push(neighbor);
      }
    }
    available.sort((a, b) => a - b);
  }

  // If topological order does not include all tasks, there is a cycle.
  if (topoOrder.length !== tasks.length) return [];

  // Scheduling: We simulate the sequential execution of tasks in topoOrder.
  // A task is only scheduled if all its dependencies have been scheduled
  // and including it does not violate its deadline.
  const scheduled = new Set();
  const result = [];
  let currentTime = 0;
  // Create a lookup for task dependencies for fast check.
  const depsLookup = new Map();
  for (const task of tasks) {
    depsLookup.set(task.id, new Set(task.dependencies));
  }

  // Process tasks in the lexicographically smallest topological order.
  for (const id of topoOrder) {
    const task = taskMap.get(id);
    // Check if all dependencies have been scheduled.
    let allDepsScheduled = true;
    for (const dep of depsLookup.get(id)) {
      if (!scheduled.has(dep)) {
        allDepsScheduled = false;
        break;
      }
    }
    if (!allDepsScheduled) {
      // If dependencies not met, skip this task.
      continue;
    }
    // Check if scheduling this task would complete before its deadline.
    if (currentTime + task.duration <= task.deadline) {
      currentTime += task.duration;
      scheduled.add(id);
      result.push(id);
    }
    // If the task cannot meet its deadline, it is skipped.
    // Its dependents will in turn be skipped because of unmet dependencies.
  }
  return result;
}

module.exports = { scheduleTasks };