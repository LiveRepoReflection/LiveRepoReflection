'use strict';

const { scheduleTasks } = require('../task_scheduler');

describe('Task Scheduler', () => {

  test('empty task list returns empty schedule', () => {
    const tasks = [];
    const penaltyWeight = 1;
    const result = scheduleTasks(tasks, penaltyWeight);
    expect(result).toEqual([]);
  });

  test('single task returns its id', () => {
    const tasks = [
      { id: 0, duration: 5, deadline: 5, dependencies: [] }
    ];
    const penaltyWeight = 1;
    const result = scheduleTasks(tasks, penaltyWeight);
    expect(result).toEqual([0]);
  });

  test('chain dependencies schedule', () => {
    const tasks = [
      { id: 0, duration: 2, deadline: 5, dependencies: [] },
      { id: 1, duration: 3, deadline: 7, dependencies: [0] },
      { id: 2, duration: 1, deadline: 10, dependencies: [1] }
    ];
    const penaltyWeight = 1;
    const result = scheduleTasks(tasks, penaltyWeight);
    expect(result).toEqual([0, 1, 2]);
  });

  test('independent tasks with optimal order', () => {
    const tasks = [
      { id: 0, duration: 5, deadline: 5, dependencies: [] },
      { id: 1, duration: 3, deadline: 8, dependencies: [] }
    ];
    const penaltyWeight = 1;
    const result = scheduleTasks(tasks, penaltyWeight);
    expect(result).toEqual([0, 1]);
  });

  test('complex dependencies and penalties', () => {
    const tasks = [
      { id: 0, duration: 2, deadline: 4, dependencies: [] },
      { id: 1, duration: 3, deadline: 5, dependencies: [] },
      { id: 2, duration: 2, deadline: 10, dependencies: [0, 1] },
      { id: 3, duration: 4, deadline: 12, dependencies: [0] }
    ];
    const penaltyWeight = 2;
    // Expected schedule: [0, 1, 2, 3] will have finish times:
    // Task 0: finish at 2 (lateness = 0)
    // Task 1: finish at 5 (lateness = 0)
    // Task 2: finish at 7 (lateness = 0)
    // Task 3: finish at 11 (lateness = 0)
    expect(scheduleTasks(tasks, penaltyWeight)).toEqual([0, 1, 2, 3]);
  });

  test('tie-breaking: lexicographical order when penalty equal', () => {
    const tasks = [
      { id: 1, duration: 2, deadline: 5, dependencies: [] },
      { id: 0, duration: 2, deadline: 5, dependencies: [] }
    ];
    const penaltyWeight = 1;
    // Both orders [1,0] and [0,1] yield total penalty 0.
    // Lexicographically smallest (treating ids as numbers) is [0,1].
    expect(scheduleTasks(tasks, penaltyWeight)).toEqual([0, 1]);
  });

  test('circular dependency returns null', () => {
    const tasks = [
      { id: 0, duration: 3, deadline: 5, dependencies: [1] },
      { id: 1, duration: 2, deadline: 4, dependencies: [0] }
    ];
    const penaltyWeight = 1;
    expect(scheduleTasks(tasks, penaltyWeight)).toBeNull();
  });

  test('complex cycle detection with indirect cycle returns null', () => {
    const tasks = [
      { id: 0, duration: 1, deadline: 3, dependencies: [1] },
      { id: 1, duration: 2, deadline: 5, dependencies: [2] },
      { id: 2, duration: 3, deadline: 7, dependencies: [0] },
      { id: 3, duration: 4, deadline: 10, dependencies: [] }
    ];
    const penaltyWeight = 1;
    expect(scheduleTasks(tasks, penaltyWeight)).toBeNull();
  });

  test('multiple valid schedules, choose lexicographically smallest', () => {
    const tasks = [
      { id: 2, duration: 2, deadline: 8, dependencies: [0, 1] },
      { id: 0, duration: 3, deadline: 7, dependencies: [] },
      { id: 1, duration: 3, deadline: 7, dependencies: [] }
    ];
    const penaltyWeight = 1;
    // Two orders [0,1,2] and [1,0,2] are valid.
    // Lexicographically smallest is [0,1,2].
    expect(scheduleTasks(tasks, penaltyWeight)).toEqual([0, 1, 2]);
  });
});