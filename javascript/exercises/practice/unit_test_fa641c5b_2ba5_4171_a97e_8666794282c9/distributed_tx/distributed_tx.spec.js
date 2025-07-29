const { runTransaction, recoverTransaction } = require('./distributed_tx');

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

describe('Distributed Transaction Coordinator', () => {
  test('all participants commit successfully', async () => {
    let invCommitCalled = 0;
    let payCommitCalled = 0;
    let orderCommitCalled = 0;
    
    const participants = [
      {
        id: 'inventory',
        prepare: async () => 'vote_commit',
        commit: async () => { invCommitCalled++; },
        rollback: async () => {}
      },
      {
        id: 'payment',
        prepare: async () => 'vote_commit',
        commit: async () => { payCommitCalled++; },
        rollback: async () => {}
      },
      {
        id: 'order',
        prepare: async () => 'vote_commit',
        commit: async () => { orderCommitCalled++; },
        rollback: async () => {}
      }
    ];

    const result = await runTransaction('tx1', participants, { timeout: 200 });
    expect(result).toBe(true);
    expect(invCommitCalled).toBe(1);
    expect(payCommitCalled).toBe(1);
    expect(orderCommitCalled).toBe(1);
  });

  test('if one participant votes abort, transaction is rolled back', async () => {
    let invRollbackCalled = 0;
    let payRollbackCalled = 0;
    let orderRollbackCalled = 0;

    const participants = [
      {
        id: 'inventory',
        prepare: async () => 'vote_commit',
        commit: async () => {},
        rollback: async () => { invRollbackCalled++; }
      },
      {
        id: 'payment',
        prepare: async () => 'vote_abort',
        commit: async () => {},
        rollback: async () => { payRollbackCalled++; }
      },
      {
        id: 'order',
        prepare: async () => 'vote_commit',
        commit: async () => {},
        rollback: async () => { orderRollbackCalled++; }
      }
    ];

    const result = await runTransaction('tx2', participants, { timeout: 200 });
    expect(result).toBe(false);
    expect(invRollbackCalled).toBe(1);
    expect(payRollbackCalled).toBe(1);
    expect(orderRollbackCalled).toBe(1);
  });

  test('participant timeout in prepare phase triggers rollback', async () => {
    let invRollbackCalled = 0;

    const participants = [
      {
        id: 'inventory',
        prepare: async () => {
          // simulate delay beyond the allowed timeout
          await sleep(300);
          return 'vote_commit';
        },
        commit: async () => {},
        rollback: async () => { invRollbackCalled++; }
      },
      {
        id: 'payment',
        prepare: async () => 'vote_commit',
        commit: async () => {},
        rollback: async () => {}
      }
    ];

    // Set timeout lower than delay in participant prepare
    const result = await runTransaction('tx3', participants, { timeout: 100 });
    expect(result).toBe(false);
    expect(invRollbackCalled).toBe(1);
  });

  test('concurrent transactions are handled correctly', async () => {
    const createParticipants = (suffix) => ([
      {
        id: 'inventory' + suffix,
        prepare: async () => 'vote_commit',
        commit: async () => {},
        rollback: async () => {}
      },
      {
        id: 'payment' + suffix,
        prepare: async () => 'vote_commit',
        commit: async () => {},
        rollback: async () => {}
      },
      {
        id: 'order' + suffix,
        prepare: async () => 'vote_commit',
        commit: async () => {},
        rollback: async () => {}
      }
    ]);

    const tx1 = runTransaction('tx_concurrent1', createParticipants('1'), { timeout: 200 });
    const tx2 = runTransaction('tx_concurrent2', createParticipants('2'), { timeout: 200 });
    const results = await Promise.all([tx1, tx2]);

    expect(results[0]).toBe(true);
    expect(results[1]).toBe(true);
  });

  test('participant commit and rollback functions are idempotent', async () => {
    let commitCallCount = 0;
    let rollbackCallCount = 0;
    
    const participant = {
      id: 'unique',
      prepare: async () => 'vote_commit',
      commit: async () => {
        // Only allow one commit operation.
        if (commitCallCount === 0) {
          commitCallCount++;
        }
      },
      rollback: async () => {
        // Only allow one rollback operation.
        if (rollbackCallCount === 0) {
          rollbackCallCount++;
        }
      }
    };

    // Simulate a successful transaction
    let result = await runTransaction('tx_idem', [participant], { timeout: 200 });
    expect(result).toBe(true);
    expect(commitCallCount).toBe(1);

    // Simulate a scenario where the transaction must rollback.
    // Forcing abort by modifying the participant's prepare function.
    const abortParticipant = {
      ...participant,
      prepare: async () => 'vote_abort'
    };

    result = await runTransaction('tx_idem_abort', [abortParticipant], { timeout: 200 });
    expect(result).toBe(false);
    expect(rollbackCallCount).toBe(1);
  });

  test('retry mechanism works on transient failures in prepare', async () => {
    let prepareAttempts = 0;
    
    const flakyParticipant = {
      id: 'flaky',
      prepare: async () => {
        prepareAttempts++;
        // Fail the first attempt and succeed on subsequent calls.
        if (prepareAttempts < 2) {
          throw new Error('Transient failure');
        }
        return 'vote_commit';
      },
      commit: async () => {},
      rollback: async () => {}
    };

    const participants = [
      {
        id: 'stable',
        prepare: async () => 'vote_commit',
        commit: async () => {},
        rollback: async () => {}
      },
      flakyParticipant
    ];

    const result = await runTransaction('tx_retry', participants, { timeout: 300 });
    expect(result).toBe(true);
    expect(prepareAttempts).toBeGreaterThanOrEqual(2);
  });

  test('recovery mechanism restores incomplete transaction state', async () => {
    // Assume that running runTransaction initiates logging.
    // Simulate a scenario where the process crashes after prepare, and recovery is needed.
    const participants = [
      {
        id: 'inventory',
        prepare: async () => 'vote_commit',
        commit: async () => {},
        rollback: async () => {}
      },
      {
        id: 'payment',
        prepare: async () => 'vote_commit',
        commit: async () => {},
        rollback: async () => {}
      }
    ];

    // Start a transaction and simulate crash by not completing commit/rollback.
    try {
      await runTransaction('tx_recover', participants, { timeout: 200, simulateCrash: true });
    } catch (e) {
      // Expected crash simulation.
    }

    // Now, attempt recovery. The recoverTransaction function should
    // check the log and complete the pending transaction.
    const recoveredResult = await recoverTransaction('tx_recover');
    // For this test, we assume that recovery commits if all votes were commit.
    expect(recoveredResult).toBe(true);
  });
});