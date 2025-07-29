class Scheduler {
  constructor() {
    this.tasks = new Map(); // key: task id, value: task object
    this.runningTasks = []; // tasks in the running state
    this.completed = new Set(); // ids of completed tasks
    this.removed = new Set(); // ids of removed tasks (deadlock resolution)
    this.availableWorkers = 0; // count of available worker nodes
  }

  addTask(taskId, processingTime, dependencies) {
    if (this.tasks.has(taskId)) {
      throw new Error(`Task ${taskId} already exists`);
    }
    if (typeof processingTime !== 'number' || processingTime < 1 || processingTime > 100) {
      throw new Error(`Invalid processing time for task ${taskId}`);
    }
    if (!Array.isArray(dependencies)) {
      throw new Error('Dependencies must be an array');
    }
    this.tasks.set(taskId, {
      id: taskId,
      processingTime,
      remaining: processingTime,
      dependencies: [...dependencies],
      state: 'waiting'
    });
    // Attempt scheduling after adding new task.
    this.scheduleTasks();
  }

  workerAvailable() {
    this.availableWorkers += 1;
    this.scheduleTasks();
  }

  getCurrentState() {
    const running = this.runningTasks.map(task => ({
      taskId: task.id,
      remaining: task.remaining
    }));
    const waiting = [];
    for (const task of this.tasks.values()) {
      if (task.state === 'waiting') {
        const waitingFor = task.dependencies.filter(dep => 
          !(this.completed.has(dep) || this.removed.has(dep))
        );
        waiting.push({ taskId: task.id, waitingFor });
      }
    }
    const completed = Array.from(this.completed);
    const removed = Array.from(this.removed);
    return { running, waiting, completed, removed };
  }

  simulateTick() {
    const completedThisTick = [];
    for (const task of this.runningTasks) {
      task.remaining -= 1;
      if (task.remaining <= 0) {
        completedThisTick.push(task);
      }
    }
    for (const task of completedThisTick) {
      task.state = 'completed';
      this.completed.add(task.id);
      this.runningTasks = this.runningTasks.filter(t => t.id !== task.id);
    }
    // After processing a tick, check if any tasks can now be scheduled.
    this.scheduleTasks();
  }

  scheduleTasks() {
    let scheduled = true;
    // Continue scheduling while workers are available and scheduling actions are taken.
    while (this.availableWorkers > 0 && scheduled) {
      scheduled = false;
      for (const task of this.tasks.values()) {
        if (task.state === 'waiting') {
          const waitingFor = task.dependencies.filter(dep =>
            !(this.completed.has(dep) || this.removed.has(dep))
          );
          if (waitingFor.length === 0) {
            task.state = 'running';
            this.runningTasks.push(task);
            this.availableWorkers -= 1;
            scheduled = true;
            if (this.availableWorkers <= 0) break;
          }
        }
      }
      // If workers are still available but no task was scheduled this round,
      // check for deadlock among waiting tasks.
      if (this.availableWorkers > 0 && !scheduled) {
        const deadlockedTasks = this.detectDeadlock();
        if (deadlockedTasks.size > 0) {
          // Choose the least valuable task (lowest processing time, tie-break by alphabetical order)
          let candidate = null;
          for (const taskId of deadlockedTasks) {
            const task = this.tasks.get(taskId);
            if (task.state !== 'waiting') continue;
            if (candidate === null) {
              candidate = task;
            } else {
              if (task.processingTime < candidate.processingTime) {
                candidate = task;
              } else if (task.processingTime === candidate.processingTime && task.id < candidate.id) {
                candidate = task;
              }
            }
          }
          if (candidate !== null) {
            candidate.state = 'removed';
            this.removed.add(candidate.id);
            scheduled = true;
          }
        }
      }
    }
  }

  detectDeadlock() {
    const waitingTasks = new Set();
    for (const task of this.tasks.values()) {
      if (task.state === 'waiting') {
        waitingTasks.add(task.id);
      }
    }
    const graph = {};
    waitingTasks.forEach(taskId => {
      const task = this.tasks.get(taskId);
      // Only consider dependencies that are in waitingTasks.
      graph[taskId] = task.dependencies.filter(dep => waitingTasks.has(dep));
    });
    const visited = new Set();
    const recStack = new Set();
    const deadlocked = new Set();

    const dfs = (node) => {
      if (!visited.has(node)) {
        visited.add(node);
        recStack.add(node);
        for (const neighbor of graph[node] || []) {
          if (!visited.has(neighbor) && dfs(neighbor)) {
            deadlocked.add(node);
            return true;
          } else if (recStack.has(neighbor)) {
            deadlocked.add(node);
            return true;
          }
        }
      }
      recStack.delete(node);
      return false;
    };

    for (const node of Object.keys(graph)) {
      dfs(node);
    }
    return deadlocked;
  }
}

module.exports = { Scheduler };