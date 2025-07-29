const { Scheduler } = require('./task_scheduler');

describe("Task Scheduler", () => {
  let scheduler;

  beforeEach(() => {
    scheduler = new Scheduler();
  });

  afterEach(() => {
    // Optionally reset scheduler state if needed.
  });

  test("should add a valid worker and task", () => {
    const worker = { id: "worker1", cpu: 4, memory: 1024, available: true };
    expect(() => scheduler.addWorker(worker)).not.toThrow();
    const task = { id: "task1", dependencies: [], cpu: 2, memory: 512, duration: 1000 };
    expect(() => scheduler.addTask(task)).not.toThrow();
  });

  test("should throw error for duplicate worker id", () => {
    const worker = { id: "worker1", cpu: 4, memory: 1024, available: true };
    scheduler.addWorker(worker);
    expect(() => scheduler.addWorker(worker)).toThrow();
  });

  test("should throw error for duplicate task id", () => {
    const task = { id: "task1", dependencies: [], cpu: 2, memory: 512, duration: 1000 };
    scheduler.addTask(task);
    expect(() => scheduler.addTask(task)).toThrow();
  });

  test("should schedule task when worker available and dependencies met", () => {
    const worker = { id: "worker1", cpu: 4, memory: 1024, available: true };
    scheduler.addWorker(worker);
    const task = { id: "task1", dependencies: [], cpu: 2, memory: 512, duration: 1000 };
    scheduler.addTask(task);
    const scheduledCount = scheduler.schedule();
    expect(scheduledCount).toBe(1);
    expect(scheduler.getTaskStatus("task1")).toBe("running");
  });

  test("should not schedule task if insufficient resources", () => {
    const worker = { id: "worker1", cpu: 2, memory: 256, available: true };
    scheduler.addWorker(worker);
    const task = { id: "task1", dependencies: [], cpu: 4, memory: 512, duration: 1000 };
    scheduler.addTask(task);
    const scheduledCount = scheduler.schedule();
    expect(scheduledCount).toBe(0);
    expect(scheduler.getTaskStatus("task1")).toBe("pending");
  });

  test("should execute tasks and mark them as completed", async () => {
    jest.useFakeTimers();
    const worker = { id: "worker1", cpu: 4, memory: 1024, available: true };
    scheduler.addWorker(worker);
    const task = { id: "task1", dependencies: [], cpu: 2, memory: 512, duration: 1000 };
    scheduler.addTask(task);
    scheduler.schedule();
    // Start task execution simulation.
    scheduler.runTasks();
    // Fast-forward time by task duration.
    jest.advanceTimersByTime(1000);
    // Wait for any pending promises to resolve.
    await Promise.resolve();
    expect(scheduler.getTaskStatus("task1")).toBe("completed");
    jest.useRealTimers();
  });

  test("should detect circular dependency and throw error", () => {
    const taskA = { id: "taskA", dependencies: ["taskB"], cpu: 1, memory: 256, duration: 500 };
    const taskB = { id: "taskB", dependencies: ["taskA"], cpu: 1, memory: 256, duration: 500 };
    scheduler.addTask(taskA);
    expect(() => scheduler.addTask(taskB)).toThrow();
  });

  test("should requeue task if worker is removed during execution", async () => {
    jest.useFakeTimers();
    const worker1 = { id: "worker1", cpu: 4, memory: 1024, available: true };
    const worker2 = { id: "worker2", cpu: 4, memory: 1024, available: true };
    scheduler.addWorker(worker1);
    scheduler.addWorker(worker2);
    const task = { id: "task1", dependencies: [], cpu: 2, memory: 512, duration: 1000 };
    scheduler.addTask(task);
    scheduler.schedule();
    // Remove the worker that might have been assigned the task.
    scheduler.removeWorker("worker1");
    // Task should revert to pending because its worker was removed.
    expect(scheduler.getTaskStatus("task1")).toBe("pending");
    // Try to reschedule on the available worker.
    scheduler.schedule();
    expect(scheduler.getTaskStatus("task1")).toBe("running");
    scheduler.runTasks();
    jest.advanceTimersByTime(1000);
    await Promise.resolve();
    expect(scheduler.getTaskStatus("task1")).toBe("completed");
    jest.useRealTimers();
  });

  test("should mark dependent task as failed if dependency fails", async () => {
    jest.useFakeTimers();
    const worker = { id: "worker1", cpu: 4, memory: 1024, available: true };
    scheduler.addWorker(worker);
    // Simulate a task that will fail during execution.
    // For the purpose of testing, assume that a task with duration 0 will simulate a failure.
    const task1 = { id: "task1", dependencies: [], cpu: 2, memory: 512, duration: 0 };
    scheduler.addTask(task1);
    const task2 = { id: "task2", dependencies: ["task1"], cpu: 2, memory: 512, duration: 1000 };
    scheduler.addTask(task2);
    scheduler.schedule();
    scheduler.runTasks();
    jest.advanceTimersByTime(0);
    await Promise.resolve();
    expect(scheduler.getTaskStatus("task1")).toBe("failed");
    // On subsequent scheduling, dependent task should detect failed dependency.
    scheduler.schedule();
    expect(scheduler.getTaskStatus("task2")).toBe("failed");
    jest.useRealTimers();
  });

  test("should return available workers", () => {
    const worker1 = { id: "worker1", cpu: 4, memory: 1024, available: true };
    const worker2 = { id: "worker2", cpu: 2, memory: 512, available: true };
    scheduler.addWorker(worker1);
    scheduler.addWorker(worker2);
    const available = scheduler.getAvailableWorkers();
    expect(available.sort()).toEqual(["worker1", "worker2"].sort());
  });
});