class Scheduler {
  constructor() {
    this.tasks = new Map(); // Map of taskId -> task object
    this.workers = new Map(); // Map of workerId -> worker object
    this.taskTimers = new Map(); // Map of taskId -> timer reference
  }

  addWorker(worker) {
    if (this.workers.has(worker.id)) {
      throw new Error("Duplicate worker id");
    }
    if (worker.cpu < 0 || worker.memory < 0) {
      throw new Error("Invalid resource values");
    }
    if (typeof worker.available !== "boolean") {
      throw new Error("Worker availability must be boolean");
    }
    // Create a clone of the worker to prevent external mutation.
    this.workers.set(worker.id, { ...worker });
  }

  removeWorker(workerId) {
    if (!this.workers.has(workerId)) {
      throw new Error("Worker not found");
    }
    // If the worker is currently running a task, requeue that task.
    for (let task of this.tasks.values()) {
      if (task.assignedWorker === workerId && task.status === "running") {
        task.status = "pending";
        task.assignedWorker = null;
      }
    }
    this.workers.delete(workerId);
  }

  addTask(task) {
    if (this.tasks.has(task.id)) {
      throw new Error("Duplicate task id");
    }
    if (task.cpu < 0 || task.memory < 0 || task.duration < 0) {
      throw new Error("Invalid resource request");
    }
    // Initialize task status and assignment.
    const newTask = { ...task, status: "pending", assignedWorker: null };
    this.tasks.set(task.id, newTask);
    // Perform circular dependency check using DFS.
    const visited = new Set();
    const recStack = new Set();

    const hasCycle = (currentId) => {
      if (!this.tasks.has(currentId)) return false;
      if (!visited.has(currentId)) {
        visited.add(currentId);
        recStack.add(currentId);
        const currTask = this.tasks.get(currentId);
        for (let dep of currTask.dependencies) {
          if (!visited.has(dep) && hasCycle(dep)) return true;
          else if (recStack.has(dep)) return true;
        }
      }
      recStack.delete(currentId);
      return false;
    };

    if (hasCycle(task.id)) {
      this.tasks.delete(task.id);
      throw new Error("Circular dependency detected");
    }
  }

  getAvailableWorkers() {
    const available = [];
    for (let [id, worker] of this.workers.entries()) {
      if (worker.available) {
        available.push(id);
      }
    }
    return available;
  }

  getTaskStatus(taskId) {
    if (!this.tasks.has(taskId)) {
      throw new Error("Task not found");
    }
    return this.tasks.get(taskId).status;
  }

  schedule() {
    let scheduledCount = 0;
    // Collect tasks that are pending and ready to run (dependencies satisfied).
    const pendingTasks = [];
    for (let task of this.tasks.values()) {
      if (task.status === "pending") {
        let hasFailedDependency = false;
        let allDepsComplete = true;
        for (let dep of task.dependencies) {
          if (this.tasks.has(dep)) {
            const depStatus = this.tasks.get(dep).status;
            if (depStatus === "failed") {
              hasFailedDependency = true;
              break;
            } else if (depStatus !== "completed") {
              allDepsComplete = false;
            }
          } else {
            // Dependency not found yet; treat as not complete.
            allDepsComplete = false;
          }
        }
        if (hasFailedDependency) {
          task.status = "failed";
          continue;
        }
        if (!allDepsComplete) continue;
        pendingTasks.push(task);
      }
    }
    // Sort pending tasks by the number of dependencies (ascending).
    pendingTasks.sort((a, b) => a.dependencies.length - b.dependencies.length);

    // Attempt to assign each pending task to an available worker.
    for (let task of pendingTasks) {
      const candidates = [];
      for (let worker of this.workers.values()) {
        if (
          worker.available &&
          worker.cpu >= task.cpu &&
          worker.memory >= task.memory
        ) {
          candidates.push(worker);
        }
      }
      if (candidates.length === 0) continue;
      // Among candidates, choose the worker with the highest (cpu + memory).
      candidates.sort((a, b) => (b.cpu + b.memory) - (a.cpu + a.memory));
      const chosen = candidates[0];
      task.status = "running";
      task.assignedWorker = chosen.id;
      chosen.available = false;
      // Simulate task execution using setTimeout.
      const timer = setTimeout(() => {
        if (task.duration === 0) {
          // Simulate task failure if duration is zero.
          task.status = "failed";
        } else {
          task.status = "completed";
        }
        // Free the worker if it still exists.
        if (this.workers.has(chosen.id)) {
          const workerObj = this.workers.get(chosen.id);
          workerObj.available = true;
        }
        // Remove the timer reference.
        this.taskTimers.delete(task.id);
        // Auto-schedule any pending tasks.
        this.schedule();
      }, task.duration);
      this.taskTimers.set(task.id, timer);
      scheduledCount++;
    }
    return scheduledCount;
  }

  runTasks() {
    // Trigger scheduling to run tasks.
    this.schedule();
  }
}

module.exports = { Scheduler };