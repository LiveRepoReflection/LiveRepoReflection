const { scheduleTasks } = require('./task_scheduler');

describe('Task Scheduler', () => {
  test('should schedule tasks with no penalty when deadlines are met', () => {
    const tasks = [
      { id: 0, duration: 2, deadline: 5, penalty: 10, dependencies: [] },
      { id: 1, duration: 3, deadline: 10, penalty: 15, dependencies: [0] },
      { id: 2, duration: 4, deadline: 13, penalty: 20, dependencies: [0] }
    ];
    const result = scheduleTasks(tasks);
    // Verify that the schedule respects dependencies: task 0 must come before 1 and 2.
    const index0 = result.schedule.indexOf(0);
    const index1 = result.schedule.indexOf(1);
    const index2 = result.schedule.indexOf(2);
    expect(index0).toBeGreaterThanOrEqual(0);
    expect(index1).toBeGreaterThan(index0);
    expect(index2).toBeGreaterThan(index0);
    // In this case, all tasks meet deadlines so totalPenalty should be 0
    expect(result.totalPenalty).toBe(0);
  });

  test('should incur penalty for tasks completed after their deadlines', () => {
    const tasks = [
      { id: 0, duration: 4, deadline: 3, penalty: 50, dependencies: [] },
      { id: 1, duration: 2, deadline: 7, penalty: 30, dependencies: [] }
    ];
    const result = scheduleTasks(tasks);
    // There is no dependency so schedule order can be arbitrary.
    // Regardless of order, task 0 will finish late because its duration exceeds its deadline.
    // Hence, totalPenalty should include penalty of task 0 (50).
    expect(result.totalPenalty).toBe(50);
    // Validate that both tasks appear in the schedule
    expect(result.schedule.sort()).toEqual([0, 1]);
  });

  test('should throw an error when there is a circular dependency', () => {
    const tasks = [
      { id: 0, duration: 3, deadline: 10, penalty: 20, dependencies: [1] },
      { id: 1, duration: 2, deadline: 8, penalty: 15, dependencies: [0] }
    ];
    expect(() => scheduleTasks(tasks)).toThrow(Error);
  });

  test('should schedule tasks with same deadlines correctly', () => {
    const tasks = [
      { id: 0, duration: 1, deadline: 4, penalty: 10, dependencies: [] },
      { id: 1, duration: 2, deadline: 4, penalty: 20, dependencies: [0] },
      { id: 2, duration: 2, deadline: 4, penalty: 15, dependencies: [] }
    ];
    const result = scheduleTasks(tasks);
    // Check that dependency of task 1 is respected.
    const index0 = result.schedule.indexOf(0);
    const index1 = result.schedule.indexOf(1);
    expect(index0).toBeGreaterThanOrEqual(0);
    expect(index1).toBeGreaterThan(index0);
    // Some tasks might miss the deadline due to same target deadline
    // Calculate finish times based on schedule order to check expected penalties.
    let currentTime = 0;
    let expectedPenalty = 0;
    const taskMap = {};
    tasks.forEach(task => taskMap[task.id] = task);
    result.schedule.forEach(taskId => {
      currentTime += taskMap[taskId].duration;
      if (currentTime > taskMap[taskId].deadline) {
        expectedPenalty += taskMap[taskId].penalty;
      }
    });
    expect(result.totalPenalty).toBe(expectedPenalty);
  });

  test('should schedule complex tasks with multiple dependencies optimally', () => {
    const tasks = [
      { id: 0, duration: 3, deadline: 10, penalty: 5, dependencies: [] },
      { id: 1, duration: 2, deadline: 8, penalty: 7, dependencies: [0] },
      { id: 2, duration: 4, deadline: 12, penalty: 15, dependencies: [0] },
      { id: 3, duration: 1, deadline: 13, penalty: 10, dependencies: [1, 2] },
      { id: 4, duration: 3, deadline: 15, penalty: 20, dependencies: [2] }
    ];
    const result = scheduleTasks(tasks);
    // Verify that dependency constraints are respected.
    const positions = {};
    result.schedule.forEach((id, idx) => {
      positions[id] = idx;
    });
    expect(positions[0]).toBeLessThan(positions[1]);
    expect(positions[0]).toBeLessThan(positions[2]);
    expect(positions[1]).toBeLessThan(positions[3]);
    expect(positions[2]).toBeLessThan(positions[3]);
    expect(positions[2]).toBeLessThan(positions[4]);
    
    // Calculate total time and penalty based on the computed schedule.
    let totalTime = 0;
    let calculatedPenalty = 0;
    const taskMap = {};
    tasks.forEach(task => {
      taskMap[task.id] = task;
    });
    result.schedule.forEach(taskId => {
      totalTime += taskMap[taskId].duration;
      if (totalTime > taskMap[taskId].deadline) {
        calculatedPenalty += taskMap[taskId].penalty;
      }
    });
    expect(result.totalPenalty).toBe(calculatedPenalty);
  });
});