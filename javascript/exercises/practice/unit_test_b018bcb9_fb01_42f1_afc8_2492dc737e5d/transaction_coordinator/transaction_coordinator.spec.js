const { TransactionCoordinator } = require('./transaction_coordinator');

describe('TransactionCoordinator', () => {
  // Helper function to simulate a delayed promise.
  const delay = (ms, value, shouldReject = false) => {
    return new Promise((resolve, reject) =>
      setTimeout(() => shouldReject ? reject(value) : resolve(value), ms)
    );
  };

  test('should commit transaction when all prepare operations succeed', async () => {
    const coordinator = new TransactionCoordinator();
    const txnId = coordinator.createTransaction();
    let commitCalled1 = false;
    let commitCalled2 = false;

    coordinator.registerOperation(txnId, {
      prepare: () => delay(50, 'prepared1'),
      commit: () => {
        commitCalled1 = true;
        return delay(50, 'committed1');
      },
      abort: () => delay(50, 'aborted1'),
      timeout: 200,
    });

    coordinator.registerOperation(txnId, {
      prepare: () => delay(30, 'prepared2'),
      commit: () => {
        commitCalled2 = true;
        return delay(30, 'committed2');
      },
      abort: () => delay(30, 'aborted2'),
      timeout: 200,
    });

    const result = await coordinator.executeTransaction(txnId);
    expect(result).toBe('commit');
    expect(commitCalled1).toBe(true);
    expect(commitCalled2).toBe(true);
  });

  test('should abort transaction if any prepare operation fails', async () => {
    const coordinator = new TransactionCoordinator();
    const txnId = coordinator.createTransaction();
    let abortCalled1 = false;
    let abortCalled2 = false;

    coordinator.registerOperation(txnId, {
      prepare: () => delay(40, 'prepared1'),
      commit: () => delay(40, 'committed1'),
      abort: () => {
        abortCalled1 = true;
        return delay(40, 'aborted1');
      },
      timeout: 200,
    });

    coordinator.registerOperation(txnId, {
      prepare: () => delay(20, 'prepare_failed', true),
      commit: () => delay(20, 'committed2'),
      abort: () => {
        abortCalled2 = true;
        return delay(20, 'aborted2');
      },
      timeout: 200,
    });

    const result = await coordinator.executeTransaction(txnId);
    expect(result).toBe('abort');
    expect(abortCalled1).toBe(true);
    expect(abortCalled2).toBe(true);
  });

  test('should abort transaction if any prepare operation times out', async () => {
    const coordinator = new TransactionCoordinator();
    const txnId = coordinator.createTransaction();
    let abortCalled = false;

    // Prepare operation that never resolves in time.
    coordinator.registerOperation(txnId, {
      prepare: () => new Promise(() => {}), // never resolves
      commit: () => delay(50, 'committed'),
      abort: () => {
        abortCalled = true;
        return delay(50, 'aborted');
      },
      timeout: 100,
    });

    // Another operation with a normal prepare.
    coordinator.registerOperation(txnId, {
      prepare: () => delay(50, 'prepared'),
      commit: () => delay(50, 'committed'),
      abort: () => delay(50, 'aborted'),
      timeout: 200,
    });

    const result = await coordinator.executeTransaction(txnId);
    expect(result).toBe('abort');
    expect(abortCalled).toBe(true);
  });

  test('should execute commit phase for all operations even if one commit fails', async () => {
    const coordinator = new TransactionCoordinator();
    const txnId = coordinator.createTransaction();
    let commitCalled = 0;
    let abortCalled = 0;

    // Both operations succeed in prepare.
    coordinator.registerOperation(txnId, {
      prepare: () => delay(30, 'prepared1'),
      commit: () => {
        commitCalled++;
        return delay(30, 'committed1');
      },
      abort: () => {
        abortCalled++;
        return delay(30, 'aborted1');
      },
      timeout: 200,
    });

    coordinator.registerOperation(txnId, {
      prepare: () => delay(30, 'prepared2'),
      // This commit will fail.
      commit: () => {
        commitCalled++;
        return delay(30, 'commit_failed', true);
      },
      abort: () => {
        abortCalled++;
        return delay(30, 'aborted2');
      },
      timeout: 200,
    });

    const result = await coordinator.executeTransaction(txnId);
    // Even if one commit fails, the overall transaction should be considered committed.
    // The coordinator should log the error internally but not disrupt the commit process.
    expect(result).toBe('commit');
    expect(commitCalled).toBe(2);
  });

  test('should handle concurrent transactions independently', async () => {
    const coordinator = new TransactionCoordinator();
    const txnId1 = coordinator.createTransaction();
    const txnId2 = coordinator.createTransaction();

    // First transaction will succeed in prepare.
    let commitCalledTxn1 = false;
    coordinator.registerOperation(txnId1, {
      prepare: () => delay(30, 'txn1_prepared'),
      commit: () => {
        commitCalledTxn1 = true;
        return delay(30, 'txn1_committed');
      },
      abort: () => delay(30, 'txn1_aborted'),
      timeout: 200,
    });

    // Second transaction will fail in prepare.
    let abortCalledTxn2 = false;
    coordinator.registerOperation(txnId2, {
      prepare: () => delay(30, 'txn2_prepare_failed', true),
      commit: () => delay(30, 'txn2_committed'),
      abort: () => {
        abortCalledTxn2 = true;
        return delay(30, 'txn2_aborted');
      },
      timeout: 200,
    });

    const [result1, result2] = await Promise.all([
      coordinator.executeTransaction(txnId1),
      coordinator.executeTransaction(txnId2),
    ]);

    expect(result1).toBe('commit');
    expect(commitCalledTxn1).toBe(true);
    expect(result2).toBe('abort');
    expect(abortCalledTxn2).toBe(true);
  });

  test('should ensure idempotency for multiple calls to operations', async () => {
    const coordinator = new TransactionCoordinator();
    const txnId = coordinator.createTransaction();
    let prepareCalls = 0;
    let commitCalls = 0;
    let abortCalls = 0;

    const op = {
      prepare: () => {
        prepareCalls++;
        return delay(30, 'prepared');
      },
      commit: () => {
        commitCalls++;
        return delay(30, 'committed');
      },
      abort: () => {
        abortCalls++;
        return delay(30, 'aborted');
      },
      timeout: 200,
    };

    // Register same operation twice to simulate idempotency concerns.
    coordinator.registerOperation(txnId, op);
    coordinator.registerOperation(txnId, op);

    // Both operations will succeed.
    const result = await coordinator.executeTransaction(txnId);
    expect(result).toBe('commit');
    // Although they are the same operation, both should be called exactly once in each phase per registration.
    expect(prepareCalls).toBe(2);
    expect(commitCalls).toBe(2);
    expect(abortCalls).toBe(0);
  });

  test('should throw error when executing an unknown transaction', async () => {
    const coordinator = new TransactionCoordinator();
    await expect(coordinator.executeTransaction('non_existing_txn')).rejects.toThrow();
  });
});