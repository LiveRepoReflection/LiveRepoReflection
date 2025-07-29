const { registerParticipant, initiateTransaction, getTransactionState } = require('../transaction_coordinator');

describe('transaction coordinator', () => {
  // To ensure a clean slate for every test, we reload the module.
  beforeEach(() => {
    jest.resetModules();
  });

  test('successful transaction commit', async () => {
    let dbCommitCalled = false;
    let dbRollbackCalled = false;

    registerParticipant(
      'db1',
      async (resourceIds) => {
        dbCommitCalled = true;
        // Simulate async commit with a small delay.
        await new Promise((resolve) => setTimeout(resolve, 20));
        return true;
      },
      async (resourceIds) => {
        dbRollbackCalled = true;
        await new Promise((resolve) => setTimeout(resolve, 20));
        return true;
      }
    );

    const operations = [
      { participantId: 'db1', resourceId: 'res1', operationType: 'write', data: { value: 10 } }
    ];

    // initiateTransaction is assumed to resolve with a transactionId upon success.
    const transactionId = await initiateTransaction(operations);

    expect(dbCommitCalled).toBe(true);
    expect(dbRollbackCalled).toBe(false);
    const state = getTransactionState(transactionId);
    expect(state).toBe('committed');
  });

  test('transaction commit failure triggers rollback', async () => {
    let commitCallCount = 0;
    let rollbackCallCount = 0;
    // For testing, assume the coordinator tracks the last transaction's id in a property "lastTransactionId".
    registerParticipant(
      'db_fail',
      async (resourceIds) => {
        commitCallCount++;
        // Simulate commit failure.
        return Promise.reject(new Error('Commit failed'));
      },
      async (resourceIds) => {
        rollbackCallCount++;
        await new Promise((resolve) => setTimeout(resolve, 20));
        return true;
      }
    );

    const operations = [
      { participantId: 'db_fail', resourceId: 'res_fail', operationType: 'delete', data: null }
    ];

    await expect(initiateTransaction(operations)).rejects.toThrow('Commit failed');
    expect(rollbackCallCount).toBe(1);

    // Assuming the coordinator exposes the last generated transaction id for testing purposes.
    const transactionId = global.transactionCoordinatorLastId;
    const state = getTransactionState(transactionId);
    expect(state).toBe('rolled_back');
  });

  test('multiple participants transaction', async () => {
    let db1CommitCalled = false;
    let db2CommitCalled = false;

    registerParticipant(
      'db1',
      async (resourceIds) => {
        db1CommitCalled = true;
        await new Promise((resolve) => setTimeout(resolve, 10));
        return true;
      },
      async (resourceIds) => {
        await new Promise((resolve) => setTimeout(resolve, 10));
        return true;
      }
    );

    registerParticipant(
      'db2',
      async (resourceIds) => {
        db2CommitCalled = true;
        await new Promise((resolve) => setTimeout(resolve, 10));
        return true;
      },
      async (resourceIds) => {
        await new Promise((resolve) => setTimeout(resolve, 10));
        return true;
      }
    );

    const operations = [
      { participantId: 'db1', resourceId: 'res1', operationType: 'write', data: { value: 100 } },
      { participantId: 'db2', resourceId: 'res2', operationType: 'enqueue', data: { message: 'hello' } }
    ];

    const transactionId = await initiateTransaction(operations);
    expect(db1CommitCalled).toBe(true);
    expect(db2CommitCalled).toBe(true);
    const state = getTransactionState(transactionId);
    expect(state).toBe('committed');
  });

  test('transaction with duplicate operations', async () => {
    let commitCallCount = 0;

    registerParticipant(
      'db_dup',
      async (resourceIds) => {
        commitCallCount += resourceIds.length;
        await new Promise((resolve) => setTimeout(resolve, 10));
        return true;
      },
      async (resourceIds) => {
        await new Promise((resolve) => setTimeout(resolve, 10));
        return true;
      }
    );

    const operations = [
      { participantId: 'db_dup', resourceId: 'res_dup', operationType: 'write', data: { val: 1 } },
      { participantId: 'db_dup', resourceId: 'res_dup', operationType: 'write', data: { val: 1 } }
    ];

    const transactionId = await initiateTransaction(operations);
    // Depending on internal optimization for duplicate operations,
    // commitCallCount could vary, so we verify it is at least 1 and not excessively high.
    expect(commitCallCount).toBeGreaterThanOrEqual(1);
    expect(commitCallCount).toBeLessThanOrEqual(2);
    const state = getTransactionState(transactionId);
    expect(state).toBe('committed');
  });

  test('transaction with no operations', async () => {
    const transactionId = await initiateTransaction([]);
    const state = getTransactionState(transactionId);
    expect(state).toBe('committed');
  });

  test('getTransactionState for unknown transaction', () => {
    const state = getTransactionState('non_existent_id');
    expect(state).toBeUndefined();
  });

  test('pending state during delayed commit', async () => {
    let resolveCommit;
    const delayedCommit = new Promise((resolve) => {
      resolveCommit = resolve;
    });

    let commitCalled = false;

    registerParticipant(
      'db_delay',
      async (resourceIds) => {
        commitCalled = true;
        // Wait until the external promise is resolved.
        await delayedCommit;
        return true;
      },
      async (resourceIds) => {
        await new Promise((resolve) => setTimeout(resolve, 10));
        return true;
      }
    );

    const operations = [
      { participantId: 'db_delay', resourceId: 'res_delay', operationType: 'write', data: { value: 50 } }
    ];

    // Start the transaction initiation. Do not await its resolution immediately.
    const transactionPromise = initiateTransaction(operations);
    // Assuming the coordinator exposes the current transaction's id in a global variable for testing.
    const transactionId = global.transactionCoordinatorLastId;
    let state = getTransactionState(transactionId);
    expect(state).toBe('pending');
    expect(commitCalled).toBe(true);

    // Now resolve the delayed commit.
    resolveCommit();
    const finalTransactionId = await transactionPromise;
    state = getTransactionState(finalTransactionId);
    expect(state).toBe('committed');
  });
});