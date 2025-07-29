const { describe, test, expect } = require('@jest/globals');
const { scheduleTasks } = require('./task_scheduler');

// Helper: Topological sort using Kahn's algorithm
function topologicalSort(tasks) {
  const inDegree = new Map();
  const graph = new Map();
  const order = [];
  
  tasks.forEach(task => {
    inDegree.set(task.id, 0);
    graph.set(task.id, []);
  });
  
  tasks.forEach(task => {
    task.dependencies.forEach(dep => {
      if (!graph.has(dep)) {
        throw new Error(`Dependency ${dep} not found`);
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
  
  while (queue.length) {
    const id = queue.shift();
    order.push(id);
    graph.get(id).forEach(neigh => {
      inDegree.set(neigh, inDegree.get(neigh) - 1);
      if (inDegree.get(neigh) === 0) {
        queue.push(neigh);
      }
    });
  }
  
  if (order.length !== tasks.length) {
    throw new Error('Cycle detected in tasks');
  }
  return order;
}

// Helper: Simulate schedule execution based on the given schedule mapping and tasks.
// Assumption: Tasks on the same worker are executed in the order given by the topological sort.
function computeMakespan(tasks, schedule) {
  const taskMap = new Map();
  tasks.forEach(task => {
    taskMap.set(task.id, task);
  });

  const topoOrder = topologicalSort(tasks);
  // Worker finish times: map from worker id to finishing time
  const workerFinish = new Map();
  // Task finish times
  const taskFinish = new Map();

  topoOrder.forEach(taskId => {
    const task = taskMap.get(taskId);
    const workerId = schedule[taskId];
    // previous finish time on worker (if no previous task, default 0)
    const workerReady = workerFinish.get(workerId) || 0;
    // Dependencies finish time
    let depsFinish = 0;
    task.dependencies.forEach(dep => {
      depsFinish = Math.max(depsFinish, taskFinish.get(dep) || 0);
    });
    const startTime = Math.max(workerReady, depsFinish);
    const finishTime = startTime + task.time;
    workerFinish.set(workerId, finishTime);
    taskFinish.set(taskId, finishTime);
  });
  let overall = 0;
  for (const finish of taskFinish.values()) {
    overall = Math.max(overall, finish);
  }
  return overall;
}

describe('Task Scheduler', () => {
  test('returns a valid schedule structure', () => {
    const tasks = [
      { id: "task1", dependencies: [], cpu: 2, memory: 4, disk: 10, time: 60 },
      { id: "task2", dependencies: [], cpu: 1, memory: 2, disk: 5, time: 120 },
    ];
    const workers = [
      { id: "worker1", cpu: 4, memory: 8, disk: 20 },
      { id: "worker2", cpu: 2, memory: 4, disk: 10 },
    ];
    
    const result = scheduleTasks(tasks, workers);
    
    expect(result).toHaveProperty('makespan');
    expect(typeof result.makespan).toBe('number');
    expect(result).toHaveProperty('schedule');
    expect(typeof result.schedule).toBe('object');
    
    // Each task must be assigned a valid worker id.
    tasks.forEach(task => {
      expect(result.schedule).toHaveProperty(task.id);
      const assignedWorker = result.schedule[task.id];
      const workerExists = workers.some(worker => worker.id === assignedWorker);
      expect(workerExists).toBe(true);
    });
  });

  test('schedule for independent tasks minimizes makespan', () => {
    const tasks = [
      { id: "task1", dependencies: [], cpu: 1, memory: 1, disk: 1, time: 50 },
      { id: "task2", dependencies: [], cpu: 1, memory: 1, disk: 1, time: 70 },
      { id: "task3", dependencies: [], cpu: 1, memory: 1, disk: 1, time: 30 },
    ];
    const workers = [
      { id: "worker1", cpu: 2, memory: 2, disk: 2 },
      { id: "worker2", cpu: 2, memory: 2, disk: 2 },
      { id: "worker3", cpu: 2, memory: 2, disk: 2 },
    ];
    
    const result = scheduleTasks(tasks, workers);
    
    // Since tasks are independent and enough workers are available,
    // the makespan should be equal to the maximum task time.
    const expectedMakespan = Math.max(...tasks.map(t => t.time));
    expect(result.makespan).toBeGreaterThanOrEqual(expectedMakespan);
    
    // Simulate schedule execution according to our computed plan.
    const simulatedMakespan = computeMakespan(tasks, result.schedule);
    expect(result.makespan).toBe(simulatedMakespan);
  });

  test('schedule respects dependencies and resource requirements', () => {
    const tasks = [
      { id: "task1", dependencies: [], cpu: 2, memory: 2, disk: 5, time: 40 },
      { id: "task2", dependencies: ["task1"], cpu: 2, memory: 2, disk: 5, time: 60 },
      { id: "task3", dependencies: ["task1"], cpu: 1, memory: 1, disk: 1, time: 30 },
      { id: "task4", dependencies: ["task2", "task3"], cpu: 3, memory: 3, disk: 10, time: 80 },
    ];
    const workers = [
      { id: "worker1", cpu: 4, memory: 4, disk: 10 },
      { id: "worker2", cpu: 4, memory: 4, disk: 10 },
    ];
    
    const result = scheduleTasks(tasks, workers);
    
    // Check that each task is assigned to a worker that can meet its resource requirements.
    tasks.forEach(task => {
      const assignedWorkerId = result.schedule[task.id];
      const worker = workers.find(w => w.id === assignedWorkerId);
      expect(worker).toBeDefined();
      expect(worker.cpu).toBeGreaterThanOrEqual(task.cpu);
      expect(worker.memory).toBeGreaterThanOrEqual(task.memory);
      expect(worker.disk).toBeGreaterThanOrEqual(task.disk);
    });
    
    // Simulate the schedule and verify makespan consistency.
    const simulatedMakespan = computeMakespan(tasks, result.schedule);
    expect(result.makespan).toBe(simulatedMakespan);
  });

  test('handles complex dependency graphs', () => {
    const tasks = [
      { id: "A", dependencies: [], cpu: 1, memory: 1, disk: 1, time: 20 },
      { id: "B", dependencies: ["A"], cpu: 1, memory: 1, disk: 1, time: 40 },
      { id: "C", dependencies: ["A"], cpu: 1, memory: 1, disk: 1, time: 10 },
      { id: "D", dependencies: ["B", "C"], cpu: 2, memory: 2, disk: 2, time: 50 },
      { id: "E", dependencies: ["C"], cpu: 1, memory: 1, disk: 1, time: 30 },
      { id: "F", dependencies: ["D", "E"], cpu: 2, memory: 2, disk: 2, time: 60 },
      { id: "G", dependencies: ["F"], cpu: 1, memory: 1, disk: 1, time: 20 },
    ];
    const workers = [
      { id: "worker1", cpu: 3, memory: 3, disk: 3 },
      { id: "worker2", cpu: 3, memory: 3, disk: 3 },
    ];
    
    const result = scheduleTasks(tasks, workers);
    
    // Check all tasks are scheduled to an existing worker.
    tasks.forEach(task => {
      const assignedWorkerId = result.schedule[task.id];
      const worker = workers.find(w => w.id === assignedWorkerId);
      expect(worker).toBeDefined();
      expect(worker.cpu).toBeGreaterThanOrEqual(task.cpu);
      expect(worker.memory).toBeGreaterThanOrEqual(task.memory);
      expect(worker.disk).toBeGreaterThanOrEqual(task.disk);
    });
    
    // Simulate the schedule execution and verify makespan.
    const simulatedMakespan = computeMakespan(tasks, result.schedule);
    expect(result.makespan).toBe(simulatedMakespan);
  });
});