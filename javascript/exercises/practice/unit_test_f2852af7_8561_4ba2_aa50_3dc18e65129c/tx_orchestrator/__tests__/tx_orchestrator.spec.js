const { executeTransaction } = require('../tx_orchestrator');

describe('executeTransaction', () => {
  // Helper function to create a service with recorded commit and rollback calls.
  const createService = (name, { commitBehaviour, rollbackBehaviour } = {}) => {
    const calls = { commit: [], rollback: [] };
    return {
      name,
      commit: jest.fn((data) => {
        calls.commit.push(data);
        if (commitBehaviour) {
          return commitBehaviour(data);
        }
        return Promise.resolve();
      }),
      rollback: jest.fn((data) => {
        calls.rollback.push(data);
        if (rollbackBehaviour) {
          return rollbackBehaviour(data);
        }
        return Promise.resolve();
      }),
      calls
    };
  };

  test('should commit transaction successfully when all commits succeed', async () => {
    const service1 = createService('service1');
    const service2 = createService('service2');
    const service3 = createService('service3');

    const transaction = [
      { service: service1, data: 'data1' },
      { service: service2, data: 'data2' },
      { service: service3, data: 'data3' }
    ];

    await expect(executeTransaction(transaction)).resolves.toBeUndefined();

    // Ensure commits were called in order.
    expect(service1.commit).toHaveBeenCalledWith('data1');
    expect(service2.commit).toHaveBeenCalledWith('data2');
    expect(service3.commit).toHaveBeenCalledWith('data3');
    // No rollbacks should be triggered.
    expect(service1.rollback).not.toHaveBeenCalled();
    expect(service2.rollback).not.toHaveBeenCalled();
    expect(service3.rollback).not.toHaveBeenCalled();
  });

  test('should trigger rollback when a commit fails', async () => {
    const service1 = createService('service1');
    // service2 fails commit.
    const service2 = createService('service2', {
      commitBehaviour: () => Promise.reject(new Error('Commit failed at service2'))
    });
    const service3 = createService('service3');

    const transaction = [
      { service: service1, data: 'data1' },
      { service: service2, data: 'data2' },
      { service: service3, data: 'data3' }
    ];

    await expect(executeTransaction(transaction)).rejects.toThrow(/service2/);

    // service1 should have committed and then rolled back.
    expect(service1.commit).toHaveBeenCalledWith('data1');
    expect(service1.rollback).toHaveBeenCalledWith('data1');
    // service2 failed before commit, so rollback is not called.
    expect(service2.commit).toHaveBeenCalledWith('data2');
    expect(service2.rollback).not.toHaveBeenCalled();
    // service3 commit should never be attempted.
    expect(service3.commit).not.toHaveBeenCalled();
  });

  test('should retry rollback until it succeeds', async () => {
    // This test simulates a transient rollback failure.
    let rollbackAttempts = 0;
    const transientRollback = (data) => {
      return new Promise((resolve, reject) => {
        rollbackAttempts++;
        if (rollbackAttempts < 3) {
          reject(new Error('Transient rollback failure'));
        } else {
          resolve();
        }
      });
    };

    const service1 = createService('service1', { rollbackBehaviour: transientRollback });
    // service2 fails commit.
    const service2 = createService('service2', {
      commitBehaviour: () => Promise.reject(new Error('Commit failed at service2'))
    });

    const transaction = [
      { service: service1, data: 'data1' },
      { service: service2, data: 'data2' }
    ];

    await expect(executeTransaction(transaction)).rejects.toThrow(/service2/);

    // service1 commit and then multiple attempts on rollback.
    expect(service1.commit).toHaveBeenCalledWith('data1');
    expect(service1.rollback).toHaveBeenCalledWith('data1');
    expect(rollbackAttempts).toBeGreaterThanOrEqual(3);
  });

  test('should process concurrent transactions without interference', async () => {
    // Create two sets of services.
    const serviceA1 = createService('serviceA1');
    const serviceA2 = createService('serviceA2');

    const serviceB1 = createService('serviceB1');
    const serviceB2 = createService('serviceB2');

    const transactionA = [
      { service: serviceA1, data: 'A1' },
      { service: serviceA2, data: 'A2' }
    ];
    const transactionB = [
      { service: serviceB1, data: 'B1' },
      { service: serviceB2, data: 'B2' }
    ];

    // Execute both transactions concurrently.
    const promiseA = executeTransaction(transactionA);
    const promiseB = executeTransaction(transactionB);

    await expect(Promise.all([promiseA, promiseB])).resolves.toEqual([undefined, undefined]);

    // Verify that each service received the correct commit calls.
    expect(serviceA1.commit).toHaveBeenCalledWith('A1');
    expect(serviceA2.commit).toHaveBeenCalledWith('A2');
    expect(serviceB1.commit).toHaveBeenCalledWith('B1');
    expect(serviceB2.commit).toHaveBeenCalledWith('B2');
  });

  test('should handle empty transaction array gracefully', async () => {
    const transaction = [];
    await expect(executeTransaction(transaction)).resolves.toBeUndefined();
  });
});