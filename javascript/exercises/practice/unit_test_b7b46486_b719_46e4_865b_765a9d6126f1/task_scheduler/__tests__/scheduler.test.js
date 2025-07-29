const { Scheduler } = require('../scheduler');

describe('Task Scheduler', () => {
  let scheduler;
  
  beforeEach(() => {
    // Assume Scheduler is a class that resets its state in the constructor.
    scheduler = new Scheduler();
  });

  test('initial state should be empty', () => {
    const state = scheduler.getCurrentState();
    expect(state.running).toEqual([]);
    expect(state.waiting).toEqual([]);
    expect(state.completed).toEqual([]);
    expect(state.removed).toEqual([]);
  });

  test('schedules a single independent task correctly', () => {
    scheduler.addTask('A', 3, []);
    // One worker available, assign the task.
    scheduler.workerAvailable();

    let state = scheduler.getCurrentState();
    expect(state.running).toContainEqual({ taskId: 'A', remaining: 3 });
    expect(state.waiting).toEqual([]);
    expect(state.completed).toEqual([]);
    expect(state.removed).toEqual([]);

    // Simulate ticks until completion
    scheduler.simulateTick(); // remaining 2
    scheduler.simulateTick(); // remaining 1
    scheduler.simulateTick(); // task completes
    state = scheduler.getCurrentState();
    expect(state.completed).toContain('A');
    expect(state.running).toEqual([]);
  });

  test('schedules tasks with dependencies correctly', () => {
    // Task A independent, Task B and C depend on A.
    scheduler.addTask('A', 2, []);
    scheduler.addTask('B', 3, ['A']);
    scheduler.addTask('C', 1, ['A']);

    // Only one worker available for now.
    scheduler.workerAvailable();
    // Task A should be scheduled as it has no dependencies.
    let state = scheduler.getCurrentState();
    expect(state.running).toContainEqual({ taskId: 'A', remaining: 2 });
    expect(state.waiting).toEqual([
      { taskId: 'B', waitingFor: ['A'] },
      { taskId: 'C', waitingFor: ['A'] }
    ]);
    
    // Complete task A.
    scheduler.simulateTick(); // remaining 1 for A
    scheduler.simulateTick(); // A completes
    state = scheduler.getCurrentState();
    expect(state.completed).toContain('A');
    // Now free worker should be assigned to waiting tasks.
    scheduler.workerAvailable();
    // Depending on scheduler implementation, one of B or C can run.
    state = scheduler.getCurrentState();
    expect(state.running.length).toBeGreaterThanOrEqual(1);
    // Both B and C should be in waiting or running.
    const waitingIds = state.waiting.map(t => t.taskId);
    const runningIds = state.running.map(t => t.taskId);
    expect([...waitingIds, ...runningIds]).toEqual(expect.arrayContaining(['B', 'C']));
    
    // Complete remaining tasks.
    while (scheduler.getCurrentState().running.length > 0 || scheduler.getCurrentState().waiting.length > 0) {
      // Always free worker if available.
      scheduler.workerAvailable();
      scheduler.simulateTick();
    }
    state = scheduler.getCurrentState();
    expect(state.completed).toEqual(expect.arrayContaining(['A', 'B', 'C']));
  });

  test('handles multiple workers concurrently', () => {
    // Add independent tasks.
    scheduler.addTask('A', 4, []);
    scheduler.addTask('B', 2, []);
    scheduler.addTask('C', 3, []);
    scheduler.addTask('D', 1, []);

    // Simulate more workers available.
    scheduler.workerAvailable();
    scheduler.workerAvailable();
    scheduler.workerAvailable();
    scheduler.workerAvailable();

    let state = scheduler.getCurrentState();
    expect(state.running.length).toBe(4);
    expect(state.waiting).toEqual([]);

    // Simulate ticks until all tasks complete.
    for (let i = 0; i < 4; i++) {
      scheduler.simulateTick();
      // After each tick, try to free any available worker if tasks are pending.
      scheduler.workerAvailable();
    }
    state = scheduler.getCurrentState();
    expect(state.running).toEqual([]);
    expect(state.completed).toEqual(expect.arrayContaining(['A', 'B', 'C', 'D']));
  });

  test('detects and resolves a deadlock by removing a task', () => {
    // Create cyclic dependency: A depends on B, B depends on A.
    scheduler.addTask('A', 5, ['B']);
    scheduler.addTask('B', 3, ['A']);
    // Add an independent task for comparison.
    scheduler.addTask('C', 2, []);
    
    // Make a worker available for C.
    scheduler.workerAvailable();
    let state = scheduler.getCurrentState();
    // Task C should be scheduled immediately.
    expect(state.running).toContainEqual({ taskId: 'C', remaining: 2 });
    
    // Now, with worker availability, try to schedule tasks A and B.
    scheduler.workerAvailable();
    
    // At this point, tasks A and B are waiting for each other.
    state = scheduler.getCurrentState();
    // Expect that tasks A and B remain waiting, deadlock resolution should trigger.
    // Simulate a tick to trigger deadlock check.
    scheduler.simulateTick();
    
    // Assume scheduler internally detects deadlock and removes one task.
    state = scheduler.getCurrentState();
    // The removed task should be the one with minimal processing time (B: 3 vs A: 5).
    expect(state.removed).toContain('B');
    // Task A should now have its dependency on B removed. Make worker available.
    scheduler.workerAvailable();
    // Continue simulation until tasks complete.
    while (scheduler.getCurrentState().running.length > 0 || scheduler.getCurrentState().waiting.length > 0) {
      scheduler.workerAvailable();
      scheduler.simulateTick();
    }
    state = scheduler.getCurrentState();
    expect(state.completed).toContain('C');
    expect(state.completed).toContain('A');
    expect(state.removed).toContain('B');
  });

  test('handles invalid dependencies gracefully', () => {
    // Add a task with an invalid dependency (nonexistent task)
    scheduler.addTask('A', 2, ['Z']);
    
    scheduler.workerAvailable();
    let state = scheduler.getCurrentState();
    // Task A should remain waiting because its dependency is not met.
    expect(state.waiting).toContainEqual({ taskId: 'A', waitingFor: ['Z'] });
    
    // Now add task Z.
    scheduler.addTask('Z', 1, []);
    scheduler.workerAvailable();
    // Simulate tick to complete Z.
    scheduler.simulateTick();
    state = scheduler.getCurrentState();
    expect(state.completed).toContain('Z');
    
    // Now task A dependency should be resolved.
    scheduler.workerAvailable();
    // Simulate ticks until completion.
    while (scheduler.getCurrentState().running.length > 0 || scheduler.getCurrentState().waiting.length > 0) {
      scheduler.workerAvailable();
      scheduler.simulateTick();
    }
    state = scheduler.getCurrentState();
    expect(state.completed).toContain('A');
  });

  test('handles duplicate task submissions gracefully', () => {
    // Add task A.
    scheduler.addTask('A', 3, []);
    // Add duplicate task A.
    expect(() => {
      scheduler.addTask('A', 4, []);
    }).toThrow();
    
    // Process the valid task.
    scheduler.workerAvailable();
    scheduler.simulateTick();
    scheduler.simulateTick();
    scheduler.simulateTick();
    const state = scheduler.getCurrentState();
    expect(state.completed).toContain('A');
  });
});