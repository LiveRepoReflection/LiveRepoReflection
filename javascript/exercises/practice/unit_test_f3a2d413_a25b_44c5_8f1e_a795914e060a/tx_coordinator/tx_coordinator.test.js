const { begin, enlist, setData, commitTransaction } = require('./tx_coordinator');

describe('Distributed Transaction Coordinator', () => {
  let transactionId;
  
  beforeEach(() => {
    transactionId = begin();
  });

  test('begin() returns a unique non-empty transaction id', () => {
    expect(typeof transactionId).toBe('string');
    expect(transactionId.length).toBeGreaterThan(0);
  });

  test('successful commit when all prepare calls succeed', async () => {
    // Create microservice endpoints that succeed on both prepare and commit.
    const service1 = {
      prepare: jest.fn((tx, data) => {
        return new Promise((resolve) => setTimeout(() => resolve(true), 100));
      }),
      commit: jest.fn((tx) => {
        return new Promise((resolve) => setTimeout(() => resolve(true), 100));
      }),
    };
    const service2 = {
      prepare: jest.fn((tx, data) => {
        return new Promise((resolve) => setTimeout(() => resolve(true), 50));
      }),
      commit: jest.fn((tx) => {
        return new Promise((resolve) => setTimeout(() => resolve(true), 50));
      }),
    };

    // Enlist services and set their corresponding data in the transaction.
    enlist(transactionId, service1);
    enlist(transactionId, service2);
    setData(transactionId, service1, { value: 123 });
    setData(transactionId, service2, { value: 456 });

    const result = await commitTransaction(transactionId);
    expect(result).toBe(true);

    // Verify that prepare was called for each service with the correct data.
    expect(service1.prepare).toHaveBeenCalledWith(transactionId, { value: 123 });
    expect(service2.prepare).toHaveBeenCalledWith(transactionId, { value: 456 });

    // Verify that commit was called for each service (commit phase).
    expect(service1.commit).toHaveBeenCalledWith(transactionId);
    expect(service2.commit).toHaveBeenCalledWith(transactionId);
  });

  test('aborts transaction if one prepare fails', async () => {
    // Create a service that succeeds and one that fails in the prepare phase.
    const service1 = {
      prepare: jest.fn((tx, data) => {
        return new Promise((resolve) => setTimeout(() => resolve(true), 100));
      }),
      commit: jest.fn((tx, rollbackFlag) => {
        return new Promise((resolve) => setTimeout(() => resolve(true), 100));
      }),
    };
    const service2 = {
      prepare: jest.fn((tx, data) => {
        return new Promise((resolve) => setTimeout(() => resolve(false), 50));
      }),
      commit: jest.fn((tx, rollbackFlag) => {
        return new Promise((resolve) => setTimeout(() => resolve(true), 50));
      }),
    };

    enlist(transactionId, service1);
    enlist(transactionId, service2);
    setData(transactionId, service1, { value: 'ok' });
    setData(transactionId, service2, { value: 'fail' });

    const result = await commitTransaction(transactionId);
    expect(result).toBe(false);

    // Both prepare functions should have been called.
    expect(service1.prepare).toHaveBeenCalledWith(transactionId, { value: 'ok' });
    expect(service2.prepare).toHaveBeenCalledWith(transactionId, { value: 'fail' });

    // Since one prepare failed, rollback should be triggered on each service.
    expect(service1.commit).toHaveBeenCalledWith(transactionId, true);
    expect(service2.commit).toHaveBeenCalledWith(transactionId, true);
  });

  test('prepare timeout leads to transaction failure', async () => {
    // Create a service where prepare exceeds the timeout threshold.
    const service = {
      prepare: jest.fn((tx, data) => {
        return new Promise((resolve) => setTimeout(() => resolve(true), 600));
      }),
      commit: jest.fn((tx, rollbackFlag) => {
        return new Promise((resolve) => setTimeout(() => resolve(true), 100));
      }),
    };

    enlist(transactionId, service);
    setData(transactionId, service, { value: 'delayed' });

    const result = await commitTransaction(transactionId);
    // Expect a failure because the prepare call times out.
    expect(result).toBe(false);

    expect(service.prepare).toHaveBeenCalledWith(transactionId, { value: 'delayed' });
    expect(service.commit).toHaveBeenCalledWith(transactionId, true);
  });

  test('commit errors are logged but transaction still succeeds if prepares succeed', async () => {
    // Create services where one service's commit call throws an error.
    const service1 = {
      prepare: jest.fn((tx, data) => {
        return new Promise((resolve) => setTimeout(() => resolve(true), 100));
      }),
      commit: jest.fn((tx) => {
        return new Promise((_, reject) => setTimeout(() => reject(new Error('Commit error')), 100));
      }),
    };
    const service2 = {
      prepare: jest.fn((tx, data) => {
        return new Promise((resolve) => setTimeout(() => resolve(true), 50));
      }),
      commit: jest.fn((tx) => {
        return new Promise((resolve) => setTimeout(() => resolve(true), 50));
      }),
    };

    enlist(transactionId, service1);
    enlist(transactionId, service2);
    setData(transactionId, service1, { value: 'commitError' });
    setData(transactionId, service2, { value: 'ok' });

    // Spy on console.error to capture error logs.
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

    const result = await commitTransaction(transactionId);
    // Even though one commit failed, the transaction should commit successfully.
    expect(result).toBe(true);

    expect(service1.prepare).toHaveBeenCalledWith(transactionId, { value: 'commitError' });
    expect(service2.prepare).toHaveBeenCalledWith(transactionId, { value: 'ok' });
    expect(service1.commit).toHaveBeenCalledWith(transactionId);
    expect(service2.commit).toHaveBeenCalledWith(transactionId);
    expect(consoleSpy).toHaveBeenCalled();

    consoleSpy.mockRestore();
  });

  test('ensures atomicity by verifying all services receive the correct commit or rollback calls', async () => {
    // Setup several services where one of them fails prepare to trigger rollback.
    const service1 = {
      prepare: jest.fn((tx, data) => Promise.resolve(true)),
      commit: jest.fn((tx, flag) => Promise.resolve(true)),
    };
    const service2 = {
      prepare: jest.fn((tx, data) => Promise.resolve(true)),
      commit: jest.fn((tx, flag) => Promise.resolve(true)),
    };
    const service3 = {
      prepare: jest.fn((tx, data) => Promise.resolve(false)),
      commit: jest.fn((tx, flag) => Promise.resolve(true)),
    };

    enlist(transactionId, service1);
    enlist(transactionId, service2);
    enlist(transactionId, service3);
    setData(transactionId, service1, { info: 1 });
    setData(transactionId, service2, { info: 2 });
    setData(transactionId, service3, { info: 3 });

    const result = await commitTransaction(transactionId);
    expect(result).toBe(false);

    // Verify each service's prepare was invoked.
    expect(service1.prepare).toHaveBeenCalledWith(transactionId, { info: 1 });
    expect(service2.prepare).toHaveBeenCalledWith(transactionId, { info: 2 });
    expect(service3.prepare).toHaveBeenCalledWith(transactionId, { info: 3 });

    // Verify that all services received a rollback commit call.
    expect(service1.commit).toHaveBeenCalledWith(transactionId, true);
    expect(service2.commit).toHaveBeenCalledWith(transactionId, true);
    expect(service3.commit).toHaveBeenCalledWith(transactionId, true);
  });
});