"use strict";
function scheduleTasks(tasks, workers, deadline) {
  if (!workers || workers.length === 0) {
    return null;
  }
  if (!tasks || tasks.length === 0) {
    return { makespan: 0, assignments: {} };
  }

  // Create a cache for networkLatency calls to reduce redundant computations.
  const latencyCache = new Map();
  function getLatency(loc1, loc2) {
    const key = loc1 + "_" + loc2;
    if (latencyCache.has(key)) {
      return latencyCache.get(key);
    }
    const latency = global.networkLatency(loc1, loc2);
    latencyCache.set(key, latency);
    return latency;
  }

  // Precompute the fixed overhead for each worker: the sum of latencies from origin->worker and worker->origin.
  const workerData = workers.map((w, index) => {
    const overhead = getLatency("origin", w.location) + getLatency(w.location, "origin");
    return {
      id: index,
      speed: w.speed,
      overhead: overhead,
      assignedTime: 0 // cumulative execution time for tasks assigned to this worker.
    };
  });

  // Use a greedy heuristic: sort tasks descending by duration for efficient scheduling.
  const tasksSorted = tasks.map((task, index) => ({ id: index, duration: task.duration }));
  tasksSorted.sort((a, b) => b.duration - a.duration);

  // Assignment mapping: task id -> worker id.
  const assignments = {};

  // For each task, assign it to the worker that, if given this task, will finish it earliest.
  for (const task of tasksSorted) {
    let bestWorker = null;
    let bestFinishTime = Infinity;

    for (const worker of workerData) {
      // Compute the cost for processing the task on this worker.
      // Each task incurs the fixed overhead plus its processing time scaled by worker speed.
      const taskCost = worker.overhead + (task.duration / worker.speed);
      const finishTime = worker.assignedTime + taskCost;
      if (finishTime < bestFinishTime) {
        bestFinishTime = finishTime;
        bestWorker = worker;
      }
    }

    // Assign the task to the selected worker.
    bestWorker.assignedTime = bestFinishTime;
    assignments[task.id] = bestWorker.id;
  }

  // Overall makespan is the maximum finish time among all workers.
  const makespan = Math.max(...workerData.map(w => w.assignedTime));
  if (makespan > deadline) {
    return null;
  }
  return { makespan, assignments };
}

module.exports = { scheduleTasks };