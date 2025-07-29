const { optimizeTasks } = require('./task_optimize');

describe('optimizeTasks', () => {
  test('Single task with no dependency', () => {
    const tasks = [
      {
        id: 0,
        resourceRequirements: { cpu: 10, memory: 20 },
        dependencies: [],
        estimatedExecutionTime: 5,
        priority: 5
      }
    ];
    const resources = { cpu: 10, memory: 20 };
    // Task 0 finishes at time 5. WACT = (5 * 5) / 1 = 25.
    const result = optimizeTasks(tasks, resources);
    expect(result).toBeCloseTo(25, 5);
  });

  test('Sequential tasks with dependencies', () => {
    const tasks = [
      {
        id: 0,
        resourceRequirements: { cpu: 2, memory: 2 },
        dependencies: [],
        estimatedExecutionTime: 5,
        priority: 5
      },
      {
        id: 1,
        resourceRequirements: { cpu: 2, memory: 2 },
        dependencies: [0],
        estimatedExecutionTime: 10,
        priority: 10
      },
      {
        id: 2,
        resourceRequirements: { cpu: 2, memory: 2 },
        dependencies: [0, 1],
        estimatedExecutionTime: 15,
        priority: 1
      }
    ];
    const resources = { cpu: 4, memory: 4 };
    // Execution simulation:
    // Task 0: Runs from 0 -> 5.
    // Task 1: Starts at 5, runs to 15.
    // Task 2: Starts at 15, runs to 30.
    // WACT = (5*5 + 15*10 + 30*1) / 3 = (25 + 150 + 30) / 3 = 205 / 3 ≈ 68.33333.
    const result = optimizeTasks(tasks, resources);
    expect(result).toBeCloseTo(68.33333, 5);
  });

  test('Concurrent tasks without dependencies', () => {
    const tasks = [
      {
        id: 0,
        resourceRequirements: { cpu: 5, memory: 5 },
        dependencies: [],
        estimatedExecutionTime: 10,
        priority: 5
      },
      {
        id: 1,
        resourceRequirements: { cpu: 5, memory: 5 },
        dependencies: [],
        estimatedExecutionTime: 20,
        priority: 10
      },
      {
        id: 2,
        resourceRequirements: { cpu: 5, memory: 5 },
        dependencies: [],
        estimatedExecutionTime: 30,
        priority: 1
      }
    ];
    const resources = { cpu: 10, memory: 10 };
    // Optimal scheduling simulation:
    // Start Task 0 and Task 1 concurrently at time 0.
    // Task 0 finishes at time 10, Task 1 finishes at time 20.
    // At time 10, Task 2 starts and finishes at time 40.
    // WACT = (10*5 + 20*10 + 40*1) / 3 = (50 + 200 + 40) / 3 = 290 / 3 ≈ 96.66667.
    const result = optimizeTasks(tasks, resources);
    expect(result).toBeCloseTo(96.66667, 5);
  });

  test('Failure due to insufficient resources', () => {
    const tasks = [
      {
        id: 0,
        resourceRequirements: { cpu: 600, memory: 50 },
        dependencies: [],
        estimatedExecutionTime: 10,
        priority: 5
      }
    ];
    const resources = { cpu: 500, memory: 500 };
    // The task requires more CPU than available, hence it cannot be scheduled.
    const result = optimizeTasks(tasks, resources);
    expect(result).toBe(-1);
  });

  test('Complex dependency with concurrent scheduling', () => {
    const tasks = [
      {
        id: 0,
        resourceRequirements: { cpu: 3, memory: 3 },
        dependencies: [],
        estimatedExecutionTime: 5,
        priority: 5
      },
      {
        id: 1,
        resourceRequirements: { cpu: 4, memory: 2 },
        dependencies: [0],
        estimatedExecutionTime: 6,
        priority: 7
      },
      {
        id: 2,
        resourceRequirements: { cpu: 3, memory: 3 },
        dependencies: [0],
        estimatedExecutionTime: 8,
        priority: 3
      },
      {
        id: 3,
        resourceRequirements: { cpu: 2, memory: 4 },
        dependencies: [1, 2],
        estimatedExecutionTime: 10,
        priority: 9
      }
    ];
    const resources = { cpu: 7, memory: 7 };
    // Simulation:
    // Task 0: Runs from 0 -> 5.
    // At time 5, Tasks 1 and 2 run concurrently.
    // Task 1 finishes at 5+6=11, Task 2 finishes at 5+8=13.
    // Task 3 starts at 13 and finishes at 13+10=23.
    // WACT = (5*5 + 11*7 + 13*3 + 23*9) / 4 = (25 + 77 + 39 + 207) / 4 = 348 / 4 = 87.
    const result = optimizeTasks(tasks, resources);
    expect(result).toBeCloseTo(87, 5);
  });
});