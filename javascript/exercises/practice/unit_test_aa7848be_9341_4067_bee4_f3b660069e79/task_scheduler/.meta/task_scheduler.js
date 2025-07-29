'use strict';

function topologicalSort(tasks) {
  const inDegree = new Map();
  const graph = new Map();

  tasks.forEach(task => {
    inDegree.set(task.id, 0);
    graph.set(task.id, []);
  });

  tasks.forEach(task => {
    task.dependencies.forEach(dep => {
      if (!graph.has(dep)) {
        throw new Error(`Task dependency ${dep} not found`);
      }
      graph.get(dep).push(task.id);
      inDegree.set(task.id, inDegree.get(task.id) + 1);
    });
  });

  const queue = [];
  for (const [id, degree] of inDegree.entries()) {
    if (degree === 0) {
      queue.push(id);
    }
  }

  const sorted = [];
  while (queue.length) {
    const current = queue.shift();
    sorted.push(current);
    for (const neighbor of graph.get(current)) {
      inDegree.set(neighbor, inDegree.get(neighbor) - 1);
      if (inDegree.get(neighbor) === 0) {
        queue.push(neighbor);
      }
    }
  }

  if (sorted.length !== tasks.length) {
    throw new Error('Cycle detected in tasks dependencies');
  }

  return sorted;
}

function scheduleTasks(tasks, workers) {
  const taskMap = new Map();
  tasks.forEach(task => {
    taskMap.set(task.id, task);
  });

  // Obtain a valid topological order of tasks.
  const order = topologicalSort(tasks);

  // For each worker, track when it becomes available. Initially all are available at time 0.
  const workerAvailability = new Map();
  workers.forEach(worker => {
    workerAvailability.set(worker.id, 0);
  });

  // Prepare the schedule result and finish times for each task.
  const schedule = {};
  const taskFinish = new Map();

  // Process tasks in the order of dependency resolution.
  for (const taskId of order) {
    const task = taskMap.get(taskId);

    // Determine the earliest start time based on dependencies.
    let depFinish = 0;
    for (const dep of task.dependencies) {
      const finishTime = taskFinish.get(dep);
      if (finishTime === undefined) {
        throw new Error(`Task dependency ${dep} not scheduled`);
      }
      depFinish = Math.max(depFinish, finishTime);
    }

    // Identify eligible workers based on resource requirements.
    const eligibleWorkers = workers.filter(worker =>
      worker.cpu >= task.cpu &&
      worker.memory >= task.memory &&
      worker.disk >= task.disk
    );

    if (eligibleWorkers.length === 0) {
      throw new Error(`No worker meets the resource requirements for task ${task.id}`);
    }

    // Choose the worker that minimizes the finish time for the task.
    let selectedWorker = null;
    let bestFinishTime = Infinity;
    eligibleWorkers.forEach(worker => {
      const workerReady = workerAvailability.get(worker.id);
      const startTime = Math.max(workerReady, depFinish);
      const finishTime = startTime + task.time;
      if (finishTime < bestFinishTime) {
        bestFinishTime = finishTime;
        selectedWorker = worker;
      }
    });

    schedule[task.id] = selectedWorker.id;
    workerAvailability.set(selectedWorker.id, bestFinishTime);
    taskFinish.set(task.id, bestFinishTime);
  }

  // Compute the overall makespan (maximum finish time among all tasks).
  let makespan = 0;
  for (const finishTime of taskFinish.values()) {
    makespan = Math.max(makespan, finishTime);
  }

  return {
    makespan,
    schedule
  };
}

module.exports = { scheduleTasks };