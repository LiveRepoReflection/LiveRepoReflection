/**
 * Optimize the execution order and schedule of tasks to minimize the weighted average completion time (WACT).
 * If any task requires more resources than available, or if scheduling is impossible due to resource constraints, returns -1.
 *
 * @param {Array} tasks - An array of task objects. Each task has:
 *    { number } id - Unique identifier.
 *    { Object } resourceRequirements - { cpu: number, memory: number }
 *    { Array } dependencies - Array of task ids that must be completed before this one.
 *    { number } estimatedExecutionTime - Execution time in seconds.
 *    { number } priority - Priority of the task (higher is more important).
 *
 * @param {Object} resources - An object containing total available resources: { cpu: number, memory: number }
 *
 * @returns {number} The minimum weighted average completion time (WACT) as a floating-point number, or -1 if scheduling is impossible.
 */
function optimizeTasks(tasks, resources) {
  const totalTasks = tasks.length;
  // Map tasks by id, and pre-check if any task is unschedulable due to high resource requirements.
  const taskMap = new Map();
  for (const task of tasks) {
    if (task.resourceRequirements.cpu > resources.cpu || task.resourceRequirements.memory > resources.memory) {
      return -1; // Task requires more resources than available at any moment.
    }
    taskMap.set(task.id, task);
  }

  // Build indegree and dependency mapping.
  const indegree = new Map();
  const dependents = new Map();
  for (const task of tasks) {
    indegree.set(task.id, task.dependencies.length);
    for (const dep of task.dependencies) {
      if (!dependents.has(dep)) {
        dependents.set(dep, []);
      }
      dependents.get(dep).push(task.id);
    }
  }

  // Initialize ready tasks list (tasks with no unresolved dependencies).
  const readyTasks = [];
  for (const task of tasks) {
    if (indegree.get(task.id) === 0) {
      readyTasks.push(task);
    }
  }
  
  // Function to compute available resources given currently running tasks.
  function getAvailableResources(running) {
    let usedCpu = 0, usedMemory = 0;
    for (const rt of running) {
      usedCpu += rt.task.resourceRequirements.cpu;
      usedMemory += rt.task.resourceRequirements.memory;
    }
    return {
      cpu: resources.cpu - usedCpu,
      memory: resources.memory - usedMemory
    };
  }

  // Sort function for ready tasks based on a heuristic ratio: priority / estimatedExecutionTime
  function sortReadyTasks(tasksArr) {
    return tasksArr.sort((a, b) => {
      const ratioA = a.priority / a.estimatedExecutionTime;
      const ratioB = b.priority / b.estimatedExecutionTime;
      return ratioB - ratioA;
    });
  }

  // Running tasks: each entry { task, finishTime }
  const runningTasks = [];
  // Completion times: map from task id to finish time.
  const completionTimes = new Map();
  
  let currentTime = 0;
  let completedCount = 0;

  while (completedCount < totalTasks) {
    // Try to schedule ready tasks based on available resources.
    let scheduledSomething = false;
    let available = getAvailableResources(runningTasks);
    
    // Sort ready tasks according to heuristic.
    sortReadyTasks(readyTasks);
    
    // Attempt to schedule each ready task if resources allow.
    // We'll try repeatedly to incorporate newly available tasks.
    let scheduleFound = true;
    while (scheduleFound && readyTasks.length > 0) {
      scheduleFound = false;
      available = getAvailableResources(runningTasks);
      for (let i = 0; i < readyTasks.length; i++) {
        const task = readyTasks[i];
        const req = task.resourceRequirements;
        if (req.cpu <= available.cpu && req.memory <= available.memory) {
          // Schedule this task.
          const finishTime = currentTime + task.estimatedExecutionTime;
          runningTasks.push({ task, finishTime });
          // Remove task from readyTasks.
          readyTasks.splice(i, 1);
          scheduledSomething = true;
          scheduleFound = true;
          break; // Restart scanning readyTasks.
        }
      }
    }
    
    // If no tasks were scheduled and there are running tasks, advance time.
    if (runningTasks.length > 0) {
      // Find the next finish time.
      let nextFinishTime = Infinity;
      for (const rt of runningTasks) {
        if (rt.finishTime < nextFinishTime) {
          nextFinishTime = rt.finishTime;
        }
      }
      currentTime = nextFinishTime;
      // Process finished tasks (there might be more than one finishing at the same time)
      const finishedTasks = [];
      for (let i = runningTasks.length - 1; i >= 0; i--) {
        if (runningTasks[i].finishTime === currentTime) {
          finishedTasks.push(runningTasks[i].task);
          // Record completion time.
          completionTimes.set(runningTasks[i].task.id, currentTime);
          runningTasks.splice(i, 1);
          completedCount++;
        }
      }
      // For each finished task, update dependents' indegree.
      for (const finishedTask of finishedTasks) {
        if (dependents.has(finishedTask.id)) {
          for (const depId of dependents.get(finishedTask.id)) {
            indegree.set(depId, indegree.get(depId) - 1);
            if (indegree.get(depId) === 0) {
              readyTasks.push(taskMap.get(depId));
            }
          }
        }
      }
    } else {
      // There are no running tasks. If there are ready tasks, schedule them; if not, scheduling is blocked.
      if (readyTasks.length === 0) {
        return -1;
      }
      // Else, currentTime stays same (should not happen since available resources are reset)
    }
  }
  
  // Calculate Weighted Average Completion Time (WACT).
  let weightedSum = 0;
  for (const task of tasks) {
    const finishTime = completionTimes.get(task.id);
    weightedSum += finishTime * task.priority;
  }
  return weightedSum / totalTasks;
}

module.exports = { optimizeTasks };