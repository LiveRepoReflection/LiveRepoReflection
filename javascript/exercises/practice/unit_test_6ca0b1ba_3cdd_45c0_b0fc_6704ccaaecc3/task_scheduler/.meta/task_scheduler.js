function scheduleTasks(tasks) {
  // Create a mapping from task id to task object
  const taskMap = new Map();
  for (const task of tasks) {
    taskMap.set(task.id, { ...task });
  }

  // Initialize in-degree map and graph for dependency tracking.
  const inDegree = new Map();
  const graph = new Map();
  for (const task of tasks) {
    inDegree.set(task.id, task.dependencies.length);
    graph.set(task.id, []);
  }
  for (const task of tasks) {
    for (const dep of task.dependencies) {
      if (!graph.has(dep)) {
        throw new Error('Invalid dependency: Task ' + dep + ' not found.');
      }
      graph.get(dep).push(task.id);
    }
  }

  // Use Kahn's algorithm with a greedy selection based on earliest deadline (and highest penalty in tie)
  const available = [];
  for (const task of tasks) {
    if (inDegree.get(task.id) === 0) {
      available.push(task.id);
    }
  }

  const schedule = [];
  let currentTime = 0;
  while (available.length > 0) {
    // Sort available tasks by deadline ascending; if equal, by penalty descending.
    available.sort((a, b) => {
      const taskA = taskMap.get(a);
      const taskB = taskMap.get(b);
      if (taskA.deadline !== taskB.deadline) {
        return taskA.deadline - taskB.deadline;
      } else {
        return taskB.penalty - taskA.penalty;
      }
    });
    
    const currentTaskId = available.shift();
    schedule.push(currentTaskId);
    const currentTask = taskMap.get(currentTaskId);
    currentTime += currentTask.duration;
    
    // Decrease in-degree for all dependent tasks and add tasks with zero in-degree to available queue.
    for (const neighborId of graph.get(currentTaskId)) {
      inDegree.set(neighborId, inDegree.get(neighborId) - 1);
      if (inDegree.get(neighborId) === 0) {
        available.push(neighborId);
      }
    }
  }
  
  // If not all tasks are scheduled, there is a circular dependency.
  if (schedule.length !== tasks.length) {
    throw new Error('Circular dependency detected.');
  }
  
  // Simulate execution to calculate total penalty.
  let totalPenalty = 0;
  let timeElapsed = 0;
  for (const taskId of schedule) {
    const t = taskMap.get(taskId);
    timeElapsed += t.duration;
    if (timeElapsed > t.deadline) {
      totalPenalty += t.penalty;
    }
  }
  
  return { schedule, totalPenalty };
}

module.exports = { scheduleTasks };