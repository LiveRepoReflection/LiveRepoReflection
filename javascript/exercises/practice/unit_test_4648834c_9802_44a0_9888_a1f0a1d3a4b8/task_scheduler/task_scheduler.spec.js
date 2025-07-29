const { scheduleTasks } = require('./task_scheduler');

describe("scheduleTasks", () => {
  beforeEach(() => {
    // Set up a dummy networkLatency function.
    // For simplicity, if both locations are the same return 0, otherwise return 10.
    global.networkLatency = (loc1, loc2) => {
      return loc1 === loc2 ? 0 : 10;
    };
  });

  afterEach(() => {
    delete global.networkLatency;
  });

  test("should return makespan 0 and empty assignments for empty tasks", () => {
    const tasks = [];
    const workers = [
      { speed: 1, location: "A" },
      { speed: 2, location: "B" }
    ];
    const deadline = 1000;
    const result = scheduleTasks(tasks, workers, deadline);
    expect(result).not.toBeNull();
    expect(result.makespan).toBe(0);
    expect(result.assignments).toEqual({});
  });

  test("should return null if no workers are available", () => {
    const tasks = [{ duration: 50 }];
    const workers = [];
    const deadline = 1000;
    const result = scheduleTasks(tasks, workers, deadline);
    expect(result).toBeNull();
  });

  test("should return null if deadline cannot be met", () => {
    // Create a scenario where the task's required time exceeds the deadline.
    // With our dummy networkLatency, cost = 10 (origin->remote) + (duration/speed) + 10 (remote->origin)
    // For a task with duration 1000 on a worker with speed 0.1:
    // Cost = 10 + (1000 / 0.1) + 10 = 10 + 10000 + 10 = 10020.
    const tasks = [{ duration: 1000 }];
    const workers = [{ speed: 0.1, location: "remote" }];
    const deadline = 5000;
    const result = scheduleTasks(tasks, workers, deadline);
    expect(result).toBeNull();
  });

  test("should schedule a single task on a single worker", () => {
    const tasks = [{ duration: 100 }];
    const workers = [{ speed: 2, location: "local" }];
    const deadline = 1000;
    // Expected cost: networkLatency(origin, "local") = 10,
    // processing time = 100 / 2 = 50,
    // networkLatency("local", origin) = 10,
    // total = 10 + 50 + 10 = 70.
    const expectedCost = 70;
    const result = scheduleTasks(tasks, workers, deadline);
    expect(result).not.toBeNull();
    expect(result.assignments).toHaveProperty("0", 0);
    expect(result.makespan).toBeCloseTo(expectedCost, 5);
  });

  test("should schedule multiple tasks on multiple workers within deadline", () => {
    const tasks = [
      { duration: 100 },
      { duration: 200 },
      { duration: 150 },
      { duration: 50 }
    ];
    const workers = [
      { speed: 1, location: "A" },
      { speed: 2, location: "B" }
    ];
    // With our dummy networkLatency:
    // For worker 0: cost for task = 10 + (duration/1) + 10.
    // For worker 1: cost for task = 10 + (duration/2) + 10.
    // The scheduler should balance tasks to minimize the makespan and meet the deadline.
    const deadline = 500;
    const result = scheduleTasks(tasks, workers, deadline);
    expect(result).not.toBeNull();
    const assignments = result.assignments;
    // Verify every task is assigned to a valid worker index.
    expect(Object.keys(assignments).length).toBe(tasks.length);
    Object.values(assignments).forEach(workerIndex => {
      expect(typeof workerIndex).toBe('number');
      expect(workerIndex).toBeGreaterThanOrEqual(0);
      expect(workerIndex).toBeLessThan(workers.length);
    });
    // The overall makespan must be less than or equal to the deadline.
    expect(result.makespan).toBeLessThanOrEqual(deadline);
  });

  test("should handle tasks with zero duration", () => {
    const tasks = [
      { duration: 0 },
      { duration: 0 }
    ];
    const workers = [
      { speed: 1, location: "X" }
    ];
    // Expected cost per task = networkLatency(origin, "X") + 0 + networkLatency("X", origin)
    // = 10 + 0 + 10 = 20. For two tasks processed sequentially on one worker, total = 40.
    const deadline = 50;
    const result = scheduleTasks(tasks, workers, deadline);
    expect(result).not.toBeNull();
    expect(result.assignments).toHaveProperty("0", 0);
    expect(result.assignments).toHaveProperty("1", 0);
    expect(result.makespan).toBeCloseTo(40, 5);
  });
});