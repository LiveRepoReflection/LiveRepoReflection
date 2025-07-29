const { scheduleTasks } = require('./task_scheduler');

describe('scheduleTasks', () => {
  test('should return an empty array for empty input', () => {
    const input = [];
    expect(scheduleTasks(input)).toEqual([]);
  });

  test('should schedule a single task that meets its deadline', () => {
    const input = [
      { id: 0, duration: 3, deadline: 10, dependencies: [] }
    ];
    expect(scheduleTasks(input)).toEqual([0]);
  });

  test('should return empty array when a single task cannot meet its deadline', () => {
    const input = [
      { id: 0, duration: 5, deadline: 3, dependencies: [] }
    ];
    expect(scheduleTasks(input)).toEqual([]);
  });

  test('should schedule two independent tasks in lexicographically smallest order', () => {
    const input = [
      { id: 1, duration: 3, deadline: 8, dependencies: [] },
      { id: 0, duration: 4, deadline: 10, dependencies: [] }
    ];
    // Both orders [0,1] and [1,0] finish tasks by deadlines:
    // [0,1]: task0 finishes at 4 (<=10), task1 at 7 (<=8)
    // Lexicographically smallest is [0,1].
    expect(scheduleTasks(input)).toEqual([0,1]);
  });

  test('should schedule tasks with chain dependencies', () => {
    const input = [
      { id: 0, duration: 2, deadline: 3, dependencies: [] },
      { id: 1, duration: 2, deadline: 7, dependencies: [0] },
      { id: 2, duration: 4, deadline: 10, dependencies: [0, 1] }
    ];
    // Execution: task0 finishes at 2 (<=3), task1 finishes at 4 (<=7), task2 at 8 (<=10)
    expect(scheduleTasks(input)).toEqual([0,1,2]);
  });

  test('should detect cyclic dependencies and return empty schedule', () => {
    const input = [
      { id: 0, duration: 2, deadline: 10, dependencies: [1] },
      { id: 1, duration: 2, deadline: 10, dependencies: [0] }
    ];
    // Cycle between task0 and task1, so none of the tasks can be scheduled.
    expect(scheduleTasks(input)).toEqual([]);
  });

  test('should schedule a subset of tasks when one task cannot meet its deadline', () => {
    const input = [
      { id: 0, duration: 2, deadline: 10, dependencies: [] },
      { id: 1, duration: 3, deadline: 12, dependencies: [0] },
      { id: 2, duration: 1, deadline: 5, dependencies: [1] },
      { id: 3, duration: 2, deadline: 15, dependencies: [1] }
    ];
    // Chain [0,1,2] would finish at time 6, violating task2 deadline (5).
    // Best is to skip task2 and schedule [0,1,3] with finish times 2, 5, 7 respectively.
    expect(scheduleTasks(input)).toEqual([0,1,3]);
  });

  test('should work with unsorted tasks and complex dependencies', () => {
    const input = [
      { id: 3, duration: 2, deadline: 7, dependencies: [0, 2] },
      { id: 1, duration: 1, deadline: 3, dependencies: [] },
      { id: 2, duration: 2, deadline: 5, dependencies: [1] },
      { id: 0, duration: 2, deadline: 10, dependencies: [] }
    ];
    // One valid schedule is [0,1,2,3]:
    // task0 finishes at 2 (<=10), task1 at 3 (<=3), task2 at 5 (<=5), task3 at 7 (<=7).
    // Lexicographically smallest valid order is expected.
    expect(scheduleTasks(input)).toEqual([0,1,2,3]);
  });

  test('should choose lexicographically smallest schedule when multiple optimal schedules exist', () => {
    const input = [
      { id: 0, duration: 2, deadline: 10, dependencies: [] },
      { id: 1, duration: 2, deadline: 10, dependencies: [] },
      { id: 2, duration: 1, deadline: 7, dependencies: [] }
    ];
    // Possible valid schedules include [0,1,2] and [0,2,1]. 
    // Lexicographically smallest is [0,1,2].
    expect(scheduleTasks(input)).toEqual([0,1,2]);
  });
});