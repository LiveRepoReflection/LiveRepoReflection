const { TransactionCoordinator } = require('./tx_coordinator');

describe('TransactionCoordinator', () => {
  // Helper function: returns a promise that resolves/rejects after ms milliseconds.
  const wait = (ms, value, fail = false) =>
    new Promise((resolve, reject) => {
      setTimeout(() => {
        if (fail) {
          reject(new Error(value));
        } else {
          resolve(value);
        }
      }, ms);
    });

  test('Empty transaction should resolve to true', async () => {
    const coordinator = new TransactionCoordinator();
    const result = await coordinator.run();
    expect(result).toBe(true);
  });

  test('All actions succeed', async () => {
    let rollbackLog = [];
    const coordinator = new TransactionCoordinator();

    coordinator.addAction(
      () => wait(50, 'action1'),
      () => {
        rollbackLog.push('rollback1');
        return wait(10, 'rollback1');
      }
    );
    coordinator.addAction(
      () => wait(30, 'action2'),
      () => {
        rollbackLog.push('rollback2');
        return wait(10, 'rollback2');
      }
    );
    coordinator.addAction(
      () => wait(20, 'action3'),
      () => {
        rollbackLog.push('rollback3');
        return wait(10, 'rollback3');
      }
    );

    const result = await coordinator.run();
    expect(result).toBe(true);
    // No rollbacks should have been executed.
    expect(rollbackLog).toEqual([]);
  });

  test('First action fails without triggering any rollback', async () => {
    let rollbackCalled = false;
    const coordinator = new TransactionCoordinator();

    coordinator.addAction(
      () => wait(20, 'fail_action', true),
      () => {
        rollbackCalled = true;
        return wait(10, 'rollback');
      }
    );
    coordinator.addAction(
      () => wait(20, 'action2'),
      () => {
        rollbackCalled = true;
        return wait(10, 'rollback2');
      }
    );

    const result = await coordinator.run();
    expect(result).toBe(false);
    // No compensating actions should be called because no action succeeded before failure.
    expect(rollbackCalled).toBe(false);
  });

  test('Last action fails and triggers rollback in reverse order', async () => {
    let rollbackOrder = [];
    const coordinator = new TransactionCoordinator();

    coordinator.addAction(
      () => wait(20, 'action1'),
      () => {
        rollbackOrder.push('rollback1');
        return wait(10, 'rollback1');
      }
    );
    coordinator.addAction(
      () => wait(20, 'action2'),
      () => {
        rollbackOrder.push('rollback2');
        return wait(10, 'rollback2');
      }
    );
    coordinator.addAction(
      () => wait(20, 'fail_action', true),
      () => {
        rollbackOrder.push('rollback3');
        return wait(10, 'rollback3');
      }
    );

    const result = await coordinator.run();
    expect(result).toBe(false);
    // Rollback should be executed for action2 and action1 in that order.
    expect(rollbackOrder).toEqual(['rollback2', 'rollback1']);
  });

  test('Intermediate action fails triggering rollback for previous actions only', async () => {
    let rollbackOrder = [];
    const coordinator = new TransactionCoordinator();

    coordinator.addAction(
      () => wait(20, 'action1'),
      () => {
        rollbackOrder.push('rollback1');
        return wait(10, 'rollback1');
      }
    );
    // This action fails.
    coordinator.addAction(
      () => wait(20, 'fail_action', true),
      () => {
        rollbackOrder.push('rollback2');
        return wait(10, 'rollback2');
      }
    );
    // This action should not be executed.
    coordinator.addAction(
      () => wait(20, 'action3'),
      () => {
        rollbackOrder.push('rollback3');
        return wait(10, 'rollback3');
      }
    );

    const result = await coordinator.run();
    expect(result).toBe(false);
    // Only action1's compensation should be executed.
    expect(rollbackOrder).toEqual(['rollback1']);
  });

  test('Compensating action failure does not disrupt overall rollback process', async () => {
    let rollbackOrder = [];
    const originalConsoleError = console.error;
    const errorLogs = [];
    console.error = (msg) => {
      errorLogs.push(msg);
    };

    const coordinator = new TransactionCoordinator();

    coordinator.addAction(
      () => wait(20, 'action1'),
      () => {
        rollbackOrder.push('rollback1');
        // This compensation fails.
        return wait(10, 'rollback1_failed', true);
      }
    );
    // This action fails.
    coordinator.addAction(
      () => wait(20, 'fail_action', true),
      () => {
        rollbackOrder.push('rollback2');
        return wait(10, 'rollback2');
      }
    );
    // This action should not be executed.
    coordinator.addAction(
      () => wait(20, 'action3'),
      () => {
        rollbackOrder.push('rollback3');
        return wait(10, 'rollback3');
      }
    );

    const result = await coordinator.run();
    expect(result).toBe(false);
    // Only the rollback for action1 should be attempted.
    expect(rollbackOrder).toEqual(['rollback1']);
    // Compensation failure should log an error.
    expect(errorLogs.length).toBeGreaterThan(0);

    console.error = originalConsoleError;
  });

  test('Actions and compensations with varying execution times', async () => {
    let rollbackOrder = [];
    let actionLog = [];
    const coordinator = new TransactionCoordinator();

    // Action1 with longer delay.
    coordinator.addAction(
      () => wait(100, 'action1').then((val) => {
        actionLog.push(val);
        return val;
      }),
      () => {
        rollbackOrder.push('rollback1');
        return wait(50, 'rollback1');
      }
    );
    // Action2 with shorter delay.
    coordinator.addAction(
      () => wait(50, 'action2').then((val) => {
        actionLog.push(val);
        return val;
      }),
      () => {
        rollbackOrder.push('rollback2');
        return wait(50, 'rollback2');
      }
    );
    // Action3 fails after moderate delay.
    coordinator.addAction(
      () => wait(70, 'fail_action', true).then((val) => {
        actionLog.push(val);
        return val;
      }),
      () => {
        rollbackOrder.push('rollback3');
        return wait(50, 'rollback3');
      }
    );

    const result = await coordinator.run();
    expect(result).toBe(false);
    // Expect that only action1 and action2 executed successfully.
    expect(actionLog).toEqual(['action1', 'action2']);
    // Rollback should occur in reverse order: rollback for action2 then action1.
    expect(rollbackOrder).toEqual(['rollback2', 'rollback1']);
  });
});