const { TaskScheduler } = require('../task_scheduler.js');

describe('TaskScheduler', () => {
  let scheduler;
  let workerNodes;
  
  beforeEach(() => {
    workerNodes = ['worker1', 'worker2', 'worker3'];
    scheduler = new TaskScheduler(workerNodes);
  });

  afterEach(() => {
    scheduler.stop();
  });

  test('executes tasks based on priority and deadline', (done) => {
    const taskOrder = [];
    const completedTasks = new Set();

    scheduler.on('taskStarted', ({ taskId, workerId }) => {
      taskOrder.push(taskId);
    });

    scheduler.on('taskCompleted', ({ taskId, workerId }) => {
      completedTasks.add(taskId);
      if (completedTasks.size === 3) {
        // Expected order:
        // Task with highest priority first.
        // If priority is equal, task with earlier deadline comes next.
        // In this test:
        // taskB: priority 3, deadline far in the future.
        // taskC: priority 2, deadline is the earliest.
        // taskA: priority 1.
        expect(taskOrder[0]).toEqual('B');
        expect(taskOrder[1]).toEqual('C');
        expect(taskOrder[2]).toEqual('A');
        done();
      }
    });

    const now = Date.now();
    const createTask = (id, priority, deadlineOffset, duration) => {
      return {
        taskId: id,
        priority,
        deadline: now + deadlineOffset,
        execute: () => {
          return new Promise((resolve) => {
            setTimeout(resolve, duration);
          });
        }
      };
    };

    const taskA = createTask('A', 1, 3000, 50);
    const taskB = createTask('B', 3, 5000, 50);
    const taskC = createTask('C', 2, 1000, 50);

    scheduler.scheduleTask(taskA);
    scheduler.scheduleTask(taskB);
    scheduler.scheduleTask(taskC);

    scheduler.start();
  });

  test('reschedules a task on worker failure', (done) => {
    let executionAttempts = {};
    
    scheduler.on('taskFailed', ({ taskId, workerId, attempt }) => {
      executionAttempts[taskId] = attempt;
    });

    scheduler.on('taskCompleted', ({ taskId, workerId, attempt }) => {
      if (taskId === 'failureTask') {
        // The task should be attempted at least more than once due to failure.
        expect(executionAttempts[taskId]).toBeGreaterThanOrEqual(2);
        done();
      }
    });

    const task = {
      taskId: 'failureTask',
      priority: 2,
      deadline: Date.now() + 5000,
      execute: (() => {
        let attempts = 0;
        return () => {
          return new Promise((resolve, reject) => {
            attempts++;
            // Fail the first attempt and succeed on subsequent attempts.
            if (attempts === 1) {
              reject(new Error('Simulated failure'));
            } else {
              resolve();
            }
          });
        };
      })()
    };

    scheduler.scheduleTask(task);
    scheduler.start();
  });

  test('distributes tasks among available worker nodes', (done) => {
    const workerTaskMap = {};
    scheduler.on('taskCompleted', ({ taskId, workerId }) => {
      if (!workerTaskMap[workerId]) {
        workerTaskMap[workerId] = [];
      }
      workerTaskMap[workerId].push(taskId);
      const totalCompleted = Object.values(workerTaskMap).reduce((acc, arr) => acc + arr.length, 0);
      if (totalCompleted === 6) {
        // Ensure that each worker has processed at least one task.
        Object.keys(workerTaskMap).forEach((id) => {
          expect(workerTaskMap[id].length).toBeGreaterThan(0);
        });
        done();
      }
    });

    const createTask = (id, duration) => {
      return {
        taskId: id,
        priority: Math.floor(Math.random() * 5),
        deadline: Date.now() + 1000,
        execute: () => {
          return new Promise((resolve) => {
            setTimeout(resolve, duration);
          });
        }
      };
    };

    for (let i = 1; i <= 6; i++) {
      scheduler.scheduleTask(createTask(`T${i}`, 50));
    }

    scheduler.start();
  });

  test('handles a large volume of tasks', (done) => {
    let completedCount = 0;
    const totalTasks = 50;
    
    scheduler.on('taskCompleted', ({ taskId, workerId }) => {
      completedCount++;
      if (completedCount === totalTasks) {
        expect(completedCount).toEqual(totalTasks);
        done();
      }
    });

    const createTask = (id) => {
      return {
        taskId: id,
        priority: Math.floor(Math.random() * 10),
        deadline: Date.now() + Math.floor(Math.random() * 1000),
        execute: () => {
          return new Promise((resolve) => {
            setTimeout(resolve, Math.floor(Math.random() * 20));
          });
        }
      };
    };

    for (let i = 0; i < totalTasks; i++) {
      scheduler.scheduleTask(createTask(`task_${i}`));
    }

    scheduler.start();
  });
});