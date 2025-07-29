const { coordinateTransaction } = require('../atomic_tx');

describe('coordinateTransaction', () => {
  // Helper to create a delayed promise
  const delay = (ms, value, shouldReject = false) =>
    new Promise((resolve, reject) => {
      setTimeout(() => {
        if (shouldReject) {
          reject(new Error('Execution failed'));
        } else {
          resolve(value);
        }
      }, ms);
    });

  test('should commit all operations successfully', async () => {
    const op1 = {
      serviceId: 'service1',
      type: 'commit',
      data: { key: 'value1' },
      prepare: async (data) => true,
      execute: async (data) => {}
    };

    const op2 = {
      serviceId: 'service2',
      type: 'commit',
      data: { key: 'value2' },
      prepare: async (data) => true,
      execute: async (data) => {}
    };

    const result = await coordinateTransaction([op1, op2]);
    expect(result).toBe(true);
  });

  test('should rollback if any operation fails during prepare', async () => {
    const op1 = {
      serviceId: 'service1',
      type: 'commit',
      data: { key: 'value1' },
      prepare: async (data) => true,
      execute: async (data) => {}
    };

    const op2 = {
      serviceId: 'service2',
      type: 'commit',
      data: { key: 'value2' },
      prepare: async (data) => false, // simulate failure in prepare phase
      execute: async (data) => {}
    };

    const result = await coordinateTransaction([op1, op2]);
    expect(result).toBe(false);
  });

  test('should rollback if any operation fails during execute', async () => {
    const op1 = {
      serviceId: 'service1',
      type: 'commit',
      data: { key: 'value1' },
      prepare: async (data) => true,
      execute: async (data) => {}
    };

    const op2 = {
      serviceId: 'service2',
      type: 'commit',
      data: { key: 'value2' },
      prepare: async (data) => true,
      execute: async (data) => { throw new Error('Execution failed'); } // simulate failure in execution phase
    };

    const result = await coordinateTransaction([op1, op2]);
    expect(result).toBe(false);
  });

  test('should rollback if global timeout is reached', async () => {
    jest.useFakeTimers();
    const op1 = {
      serviceId: 'slow-service',
      type: 'commit',
      data: { key: 'value' },
      prepare: async (data) => delay(31000, true),
      execute: async (data) => {}
    };

    const op2 = {
      serviceId: 'normal-service',
      type: 'commit',
      data: { key: 'value' },
      prepare: async (data) => true,
      execute: async (data) => {}
    };

    const transactionPromise = coordinateTransaction([op1, op2]);

    // Fast-forward time beyond the timeout (assumed 30 seconds)
    jest.advanceTimersByTime(31000);

    // Allow any pending promises to resolve
    await Promise.resolve();
    await Promise.resolve();

    const result = await transactionPromise;
    expect(result).toBe(false);
    jest.useRealTimers();
  });

  test('should handle multiple operations with mixed delays', async () => {
    const op1 = {
      serviceId: 'service1',
      type: 'commit',
      data: { key: 'value1' },
      prepare: async (data) => delay(10, true),
      execute: async (data) => delay(10, undefined)
    };

    const op2 = {
      serviceId: 'service2',
      type: 'commit',
      data: { key: 'value2' },
      prepare: async (data) => delay(20, true),
      execute: async (data) => delay(20, undefined)
    };

    const op3 = {
      serviceId: 'service3',
      type: 'commit',
      data: { key: 'value3' },
      prepare: async (data) => delay(30, true),
      execute: async (data) => delay(30, undefined)
    };

    const result = await coordinateTransaction([op1, op2, op3]);
    expect(result).toBe(true);
  });
});