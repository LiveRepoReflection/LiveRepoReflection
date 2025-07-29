const { TransactionCoordinator } = require('../tx_coordinator');

describe('TransactionCoordinator', () => {
  let coordinator;

  beforeEach(() => {
    coordinator = new TransactionCoordinator();
  });

  test('should commit transaction successfully when all commit functions succeed', async () => {
    const events = [];
    const tx = coordinator.registerTransaction();

    tx.addParticipant(
      () => {
        events.push('commit1');
        return Promise.resolve('commit1 success');
      },
      () => {
        events.push('rollback1');
        return Promise.resolve('rollback1 success');
      }
    );

    tx.addParticipant(
      () => {
        events.push('commit2');
        return Promise.resolve('commit2 success');
      },
      () => {
        events.push('rollback2');
        return Promise.resolve('rollback2 success');
      }
    );

    await expect(tx.commitTransaction()).resolves.toBeUndefined();
    // Ensure all commit functions were called exactly once and rollback was not invoked
    expect(events).toEqual(['commit1', 'commit2']);
  });

  test('should rollback transaction when any commit fails and aggregate errors from commit and rollback', async () => {
    const events = [];
    const tx = coordinator.registerTransaction();

    // Participant 1: commit succeeds, rollback succeeds.
    tx.addParticipant(
      () => {
        events.push('commit1');
        return Promise.resolve('commit1 success');
      },
      () => {
        events.push('rollback1');
        return Promise.resolve('rollback1 success');
      }
    );

    // Participant 2: commit fails.
    tx.addParticipant(
      () => {
        events.push('commit2');
        return Promise.reject(new Error('commit2 error'));
      },
      () => {
        events.push('rollback2');
        // Simulate a rollback error.
        return Promise.reject(new Error('rollback2 error'));
      }
    );

    // Participant 3: commit succeeds, rollback succeeds.
    tx.addParticipant(
      () => {
        events.push('commit3');
        return Promise.resolve('commit3 success');
      },
      () => {
        events.push('rollback3');
        return Promise.resolve('rollback3 success');
      }
    );

    try {
      await tx.commitTransaction();
      // If commitTransaction does not throw, force a failure.
      throw new Error('commitTransaction should have failed');
    } catch (err) {
      // Expect an aggregated error containing both commit and rollback errors.
      expect(err).toBeInstanceOf(Error);
      // It is expected that the aggregated error has a property errors which is an array
      expect(Array.isArray(err.errors)).toBe(true);
      // Should at least have the commit error from participant 2 and rollback error from participant 2.
      const messages = err.errors.map(e => e.message);
      expect(messages).toEqual(
        expect.arrayContaining(['commit2 error', 'rollback2 error'])
      );
    }

    // Verify that all rollback functions were called even though one of them failed.
    // The order may vary as commit functions run concurrently.
    expect(events).toEqual(
      expect.arrayContaining(['commit1', 'commit2', 'commit3', 'rollback1', 'rollback2', 'rollback3'])
    );
  });

  test('should throw error when adding participant with invalid commit/rollback functions', () => {
    const tx = coordinator.registerTransaction();
    expect(() => {
      tx.addParticipant(null, () => Promise.resolve());
    }).toThrow();

    expect(() => {
      tx.addParticipant(() => Promise.resolve(), "not a function");
    }).toThrow();
  });

  test('should ensure commit and rollback functions are idempotent', async () => {
    let commitCount = 0;
    let rollbackCount = 0;
    const tx = coordinator.registerTransaction();

    tx.addParticipant(
      () => {
        commitCount++;
        return Promise.resolve();
      },
      () => {
        rollbackCount++;
        return Promise.resolve();
      }
    );

    // First commit attempt.
    await expect(tx.commitTransaction()).resolves.toBeUndefined();
    expect(commitCount).toBe(1);

    // Subsequent commit attempts should not invoke new commit executions.
    await expect(tx.commitTransaction()).resolves.toBeUndefined();
    expect(commitCount).toBe(1);
  });

  test('should support concurrent transactions without interference', async () => {
    const tx1 = coordinator.registerTransaction();
    const tx2 = coordinator.registerTransaction();
    const eventsTx1 = [];
    const eventsTx2 = [];

    tx1.addParticipant(
      () => {
        eventsTx1.push('tx1_commit1');
        return Promise.resolve();
      },
      () => {
        eventsTx1.push('tx1_rollback1');
        return Promise.resolve();
      }
    );

    tx1.addParticipant(
      () => {
        eventsTx1.push('tx1_commit2');
        return Promise.resolve();
      },
      () => {
        eventsTx1.push('tx1_rollback2');
        return Promise.resolve();
      }
    );

    tx2.addParticipant(
      () => {
        eventsTx2.push('tx2_commit1');
        return Promise.resolve();
      },
      () => {
        eventsTx2.push('tx2_rollback1');
        return Promise.resolve();
      }
    );

    tx2.addParticipant(
      () => {
        eventsTx2.push('tx2_commit2');
        return Promise.resolve();
      },
      () => {
        eventsTx2.push('tx2_rollback2');
        return Promise.resolve();
      }
    );

    // Commit both transactions concurrently
    const [res1, res2] = await Promise.all([
      tx1.commitTransaction(),
      tx2.commitTransaction()
    ]);

    expect(res1).toBeUndefined();
    expect(res2).toBeUndefined();
    expect(eventsTx1).toEqual(expect.arrayContaining(['tx1_commit1', 'tx1_commit2']));
    expect(eventsTx2).toEqual(expect.arrayContaining(['tx2_commit1', 'tx2_commit2']));
  });
});