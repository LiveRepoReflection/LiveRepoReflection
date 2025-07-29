const { scheduleTasks } = require('./task_scheduler');

describe('Task Scheduler', () => {
  test('should schedule basic tasks with no dependencies', () => {
    const tasks = [
      { id: 1, executionTime: 5, deadline: 10, dependencies: [] },
      { id: 2, executionTime: 5, deadline: 20, dependencies: [] },
    ];
    const currentTime = 0;
    const result = scheduleTasks(tasks, currentTime);
    // Expected order: [1, 2] as tasks are sorted by earlier deadline.
    expect(result).toEqual([1, 2]);
  });

  test('should schedule tasks with linear dependencies', () => {
    const tasks = [
      { id: 1, executionTime: 10, deadline: 30, dependencies: [] },
      { id: 2, executionTime: 5, deadline: 25, dependencies: [1] },
      { id: 3, executionTime: 5, deadline: 40, dependencies: [2] },
    ];
    const currentTime = 0;
    const result = scheduleTasks(tasks, currentTime);
    // The only valid order that respects dependencies and deadlines is [1, 2, 3].
    expect(result).toEqual([1, 2, 3]);
  });

  test('should not schedule a task if its deadline cannot be met', () => {
    const tasks = [
      { id: 1, executionTime: 10, deadline: 15, dependencies: [] },
      { id: 2, executionTime: 10, deadline: 25, dependencies: [] },
    ];
    const currentTime = 7;
    // Task 1 would finish at time 17 (>15), so only task 2 can be scheduled.
    const result = scheduleTasks(tasks, currentTime);
    expect(result).toEqual([2]);
  });

  test('should select the maximum number of tasks possible', () => {
    const tasks = [
      { id: 1, executionTime: 5, deadline: 10, dependencies: [] },
      { id: 2, executionTime: 10, deadline: 20, dependencies: [] },
      { id: 3, executionTime: 2, deadline: 8, dependencies: [] },
      { id: 4, executionTime: 3, deadline: 15, dependencies: [] },
    ];
    const currentTime = 0;
    // Optimal order by deadlines and execution times is [3, 1, 4, 2].
    const result = scheduleTasks(tasks, currentTime);
    expect(result).toEqual([3, 1, 4, 2]);
  });

  test('should schedule tasks with complex dependencies and ordering rules', () => {
    const tasks = [
      { id: 1, executionTime: 3, deadline: 10, dependencies: [] },
      { id: 2, executionTime: 4, deadline: 15, dependencies: [1] },
      { id: 3, executionTime: 2, deadline: 8, dependencies: [] },
      { id: 4, executionTime: 5, deadline: 20, dependencies: [2, 3] },
      { id: 5, executionTime: 3, deadline: 12, dependencies: [1] },
      { id: 6, executionTime: 1, deadline: 10, dependencies: [3] },
    ];
    const currentTime = 0;
    // Among available tasks, task 3 (deadline 8) should be prioritized over task 1 (deadline 10).
    // One feasible valid schedule: [3, 1, 6, 5, 2, 4]
    // Execution times: 0+2=2 (task3), 2+3=5 (task1), 5+1=6 (task6), 6+3=9 (task5), 9+4=13 (task2), 13+5=18 (task4)
    // All tasks meet their deadlines.
    const result = scheduleTasks(tasks, currentTime);
    expect(result).toEqual([3, 1, 6, 5, 2, 4]);
  });

  test('should skip tasks involved in a direct circular dependency', () => {
    const tasks = [
      { id: 1, executionTime: 5, deadline: 15, dependencies: [2] },
      { id: 2, executionTime: 5, deadline: 15, dependencies: [1] },
      { id: 3, executionTime: 3, deadline: 10, dependencies: [] },
    ];
    const currentTime = 0;
    // Tasks 1 and 2 are in a cycle, hence unschedulable. Only task 3 may be scheduled.
    const result = scheduleTasks(tasks, currentTime);
    expect(result).toEqual([3]);
  });

  test('should handle tasks with an indirect circular dependency', () => {
    const tasks = [
      { id: 1, executionTime: 2, deadline: 10, dependencies: [] },
      { id: 2, executionTime: 3, deadline: 15, dependencies: [1] },
      { id: 3, executionTime: 4, deadline: 20, dependencies: [2] },
      { id: 4, executionTime: 5, deadline: 25, dependencies: [3, 5] },
      { id: 5, executionTime: 1, deadline: 5, dependencies: [4] }, // Cycle exists between tasks 4 and 5.
    ];
    const currentTime = 0;
    // Only tasks 1, 2, and 3 can be scheduled as tasks 4 and 5 form a cycle.
    const result = scheduleTasks(tasks, currentTime);
    expect(result).toEqual([1, 2, 3]);
  });

  test('should return an empty schedule when no tasks can be completed on time', () => {
    const tasks = [
      { id: 1, executionTime: 10, deadline: 5, dependencies: [] },
      { id: 2, executionTime: 8, deadline: 7, dependencies: [] },
    ];
    const currentTime = 0;
    const result = scheduleTasks(tasks, currentTime);
    expect(result).toEqual([]);
  });
});