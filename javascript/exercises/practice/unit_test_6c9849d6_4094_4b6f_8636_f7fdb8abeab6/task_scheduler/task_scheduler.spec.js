const { scheduleTasks } = require('./task_scheduler');

describe('scheduleTasks', () => {
  test('should return 0 for an empty task list', () => {
    expect(scheduleTasks([])).toBe(0);
  });

  test('should return minimum total lateness for sample tasks', () => {
    const tasks = [
      { id: 1, duration: 10, deadline: 50, dependencies: [] },
      { id: 2, duration: 20, deadline: 100, dependencies: [1] },
      { id: 3, duration: 15, deadline: 60, dependencies: [1] },
      { id: 4, duration: 25, deadline: 120, dependencies: [2, 3] },
    ];
    expect(scheduleTasks(tasks)).toBe(0);
  });

  test('should calculate lateness correctly when deadlines are missed', () => {
    const tasks = [
      { id: 1, duration: 10, deadline: 5, dependencies: [] } // lateness = 5
    ];
    expect(scheduleTasks(tasks)).toBe(5);
  });

  test('should choose optimal ordering to minimize total lateness', () => {
    // Two possible orders: one order may cause lateness while another yields none.
    const tasks = [
      { id: 1, duration: 10, deadline: 15, dependencies: [] },
      { id: 2, duration: 20, deadline: 40, dependencies: [1] },
      { id: 3, duration: 5, deadline: 30, dependencies: [1] },
      { id: 4, duration: 15, deadline: 55, dependencies: [2, 3] },
    ];
    // Optimal schedule: 1 -> 3 -> 2 -> 4 leads to total lateness = 0.
    expect(scheduleTasks(tasks)).toBe(0);
  });

  test('should return -1 when tasks have cyclic dependencies', () => {
    const tasks = [
      { id: 1, duration: 10, deadline: 50, dependencies: [2] },
      { id: 2, duration: 20, deadline: 70, dependencies: [1] },
    ];
    expect(scheduleTasks(tasks)).toBe(-1);
  });

  test('should handle tasks with zero duration properly', () => {
    const tasks = [
      { id: 1, duration: 0, deadline: 0, dependencies: [] },
      { id: 2, duration: 5, deadline: 4, dependencies: [1] } // finishes at 5, lateness = 1
    ];
    expect(scheduleTasks(tasks)).toBe(1);
  });

  test('should handle tasks with zero or negative deadlines', () => {
    const tasks = [
      { id: 1, duration: 5, deadline: 0, dependencies: [] } // lateness = 5
    ];
    expect(scheduleTasks(tasks)).toBe(5);
  });
});