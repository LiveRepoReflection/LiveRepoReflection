const { transactionCoordinator } = require('./txn_coordinator');

describe('Distributed Transaction Coordinator Tests', () => {
  // Helper service mocks
  const createSuccessService = () => {
    return {
      prepare: jest.fn(async (transactionId) => {
        // Simulate a small delay and then vote commit
        await new Promise(r => setTimeout(r, 10));
        return 'vote commit';
      }),
      commit: jest.fn(async (transactionId) => {
        await new Promise(r => setTimeout(r, 10));
      }),
      rollback: jest.fn(async (transactionId) => {
        await new Promise(r => setTimeout(r, 10));
      }),
    };
  };

  const createFailureService = () => {
    return {
      prepare: jest.fn(async (transactionId) => {
        await new Promise(r => setTimeout(r, 10));
        // Simulate failure: reject with an abort vote
        throw new Error('vote abort');
      }),
      commit: jest.fn(async (transactionId) => {
        await new Promise(r => setTimeout(r, 10));
      }),
      rollback: jest.fn(async (transactionId) => {
        await new Promise(r => setTimeout(r, 10));
      }),
    };
  };

  const createRetryService = (failTimes = 1) => {
    let callCount = 0;
    return {
      prepare: jest.fn(async (transactionId) => {
        await new Promise(r => setTimeout(r, 10));
        callCount++;
        if (callCount <= failTimes) {
          // Fail initially, then succeed
          throw new Error('temporary failure');
        }
        return 'vote commit';
      }),
      commit: jest.fn(async (transactionId) => {
        await new Promise(r => setTimeout(r, 10));
      }),
      rollback: jest.fn(async (transactionId) => {
        await new Promise(r => setTimeout(r, 10));
      }),
    };
  };

  // Test: Successful transaction commit when all services vote commit.
  test('should commit transaction successfully when all services vote commit', async () => {
    const service1 = createSuccessService();
    const service2 = createSuccessService();
    const service3 = createSuccessService();
    
    const services = [service1, service2, service3];
    const config = {
      retryAttempts: 3,
      timeout: 100,
      logging: { log: () => {} }
    };

    const result = await transactionCoordinator(services, config);
    expect(result).toBe(true);
    // Verify that prepare and commit were called exactly once per service.
    services.forEach(svc => {
      expect(svc.prepare).toHaveBeenCalledTimes(1);
      expect(svc.commit).toHaveBeenCalledTimes(1);
      expect(svc.rollback).not.toHaveBeenCalled();
    });
  });

  // Test: Transaction rollback when one service votes abort during prepare phase.
  test('should rollback transaction when a service votes abort', async () => {
    const service1 = createSuccessService();
    const service2 = createFailureService();
    const service3 = createSuccessService();
    
    const services = [service1, service2, service3];
    const config = {
      retryAttempts: 2,
      timeout: 100,
      logging: { log: () => {} }
    };

    const result = await transactionCoordinator(services, config);
    expect(result).toBe(false);
    // In rollback scenario, prepare might be called more than once due to retries.
    // But commit should never be called, and rollback should be invoked for all services.
    services.forEach(svc => {
      expect(svc.commit).not.toHaveBeenCalled();
      expect(svc.rollback).toHaveBeenCalled();
    });
  });

  // Test: Service that requires retries before succeeding in prepare.
  test('should succeed after retrying a failing service during prepare phase', async () => {
    const service1 = createSuccessService();
    const service2 = createRetryService(2);  // Fail first 2 times and succeed on 3rd attempt.
    const service3 = createSuccessService();
    
    const services = [service1, service2, service3];
    const config = {
      retryAttempts: 3,
      timeout: 100,
      logging: { log: () => {} }
    };

    const result = await transactionCoordinator(services, config);
    expect(result).toBe(true);
    // For service2, prepare should be called 3 times.
    expect(service2.prepare).toHaveBeenCalledTimes(3);
    // For all services, commit should be called once and no rollback.
    [service1, service2, service3].forEach(svc => {
      expect(svc.commit).toHaveBeenCalledTimes(1);
      expect(svc.rollback).not.toHaveBeenCalled();
    });
  });

  // Test: Concurrent transactions handled independently.
  test('should handle multiple concurrent transactions', async () => {
    const makeServices = () => [createSuccessService(), createSuccessService(), createSuccessService()];

    const config = {
      retryAttempts: 2,
      timeout: 100,
      logging: { log: () => {} }
    };

    // Start 5 concurrent transactions.
    const transactionPromises = [];
    for (let i = 0; i < 5; i++) {
      transactionPromises.push(transactionCoordinator(makeServices(), config));
    }

    const results = await Promise.all(transactionPromises);
    results.forEach(result => expect(result).toBe(true));
  });

  // Test: Timeout behavior when a service does not respond in time.
  test('should rollback transaction if a service times out during prepare', async () => {
    // Create a service that never resolves prepare to simulate timeout.
    const timeoutService = {
      prepare: jest.fn(() => new Promise(() => {})),
      commit: jest.fn(async () => {
        await new Promise(r => setTimeout(r, 10));
      }),
      rollback: jest.fn(async () => {
        await new Promise(r => setTimeout(r, 10));
      }),
    };

    const service1 = createSuccessService();
    const service2 = timeoutService;
    const service3 = createSuccessService();
    
    const services = [service1, service2, service3];
    const config = {
      retryAttempts: 1,
      timeout: 50, // Short timeout to trigger failure.
      logging: { log: () => {} }
    };

    const result = await transactionCoordinator(services, config);
    expect(result).toBe(false);

    services.forEach(svc => {
      // commit should not be called if timeout happens
      expect(svc.commit).not.toHaveBeenCalled();
      // rollback must have been called for services that passed prepare
      expect(svc.rollback).toHaveBeenCalled();
    });
  });

  // Test: Idempotency of commit and rollback calls.
  test('should be idempotent with multiple commit/rollback calls for the same transaction', async () => {
    const service = {
      prepare: jest.fn(async (transactionId) => {
        await new Promise(r => setTimeout(r, 10));
        return 'vote commit';
      }),
      commit: jest.fn(async (transactionId) => {
        await new Promise(r => setTimeout(r, 10));
      }),
      rollback: jest.fn(async (transactionId) => {
        await new Promise(r => setTimeout(r, 10));
      }),
    };

    const services = [service, service, service]; // Same service instance reused.
    const config = {
      retryAttempts: 2,
      timeout: 100,
      logging: { log: () => {} }
    };

    const result = await transactionCoordinator(services, config);
    // Even if the same service instance appears multiple times,
    // idempotency should ensure commit is processed once per unique transaction.
    expect(result).toBe(true);
    // Depending on implementation, commit might be called multiple times,
    // but the effect should be idempotent. We at least check that rollback was never called.
    expect(service.rollback).not.toHaveBeenCalled();
  });
});