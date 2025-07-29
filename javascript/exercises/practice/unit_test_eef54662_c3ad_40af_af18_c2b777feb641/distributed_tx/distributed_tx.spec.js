const { TransactionOrchestrator } = require('./distributed_tx');

jest.setTimeout(10000); // Increase timeout for async retries if necessary

// Helper function to create a mock service
function createMockService(name, options = {}) {
  let processCallCount = 0;
  let compensateCallCount = 0;
  return {
    process: jest.fn((transactionId, data) => {
      processCallCount++;
      return new Promise((resolve, reject) => {
        setTimeout(() => {
          if (options.failProcess && processCallCount === options.failProcessCallAttempt) {
            return reject(new Error(`${name} process failed`));
          }
          resolve(`${name} processed`);
        }, options.delay || 10);
      });
    }),
    compensate: jest.fn((transactionId, data) => {
      compensateCallCount++;
      return new Promise((resolve, reject) => {
        setTimeout(() => {
          if (options.failCompensate && compensateCallCount <= (options.failCompensateTimes || 1)) {
            return reject(new Error(`${name} compensate failed`));
          }
          resolve(`${name} compensated`);
        }, options.delay || 10);
      });
    }),
    getProcessCallCount: () => processCallCount,
    getCompensateCallCount: () => compensateCallCount,
  };
}

describe('TransactionOrchestrator', () => {
  test('should commit transaction if all services process successfully', async () => {
    const accountService = createMockService('account');
    const orderService = createMockService('order');
    const inventoryService = createMockService('inventory');

    const services = [accountService, orderService, inventoryService];
    const transactionData = { userId: 1, orderId: 101 };

    const orchestrator = new TransactionOrchestrator();
    const transactionId = orchestrator.beginTransaction(services, transactionData);
    await orchestrator.executeTransaction(transactionId);

    const state = orchestrator.getTransactionState(transactionId);
    expect(state).toEqual('COMMITTED');

    // Verify that process was called once per service
    services.forEach(service => {
      expect(service.process).toHaveBeenCalledTimes(1);
      expect(service.compensate).not.toHaveBeenCalled();
    });
  });

  test('should rollback transaction if a service process fails', async () => {
    // accountService will process successfully
    const accountService = createMockService('account');
    // orderService will fail on its first process attempt
    const orderService = createMockService('order', { failProcess: true, failProcessCallAttempt: 1 });
    // inventoryService should not even be called because order fails
    const inventoryService = createMockService('inventory');

    const services = [accountService, orderService, inventoryService];
    const transactionData = { userId: 2, orderId: 202 };

    const orchestrator = new TransactionOrchestrator();
    const transactionId = orchestrator.beginTransaction(services, transactionData);
    try {
      await orchestrator.executeTransaction(transactionId);
    } catch (error) {
      // Expected error, do nothing
    }
    const state = orchestrator.getTransactionState(transactionId);
    expect(state).toEqual('ROLLED_BACK');

    // accountService should have been processed and then compensated
    expect(accountService.process).toHaveBeenCalledTimes(1);
    expect(accountService.compensate).toHaveBeenCalledTimes(1);

    // orderService failed, so no compensation is needed for it (depending on design, might be skipped)
    expect(orderService.process).toHaveBeenCalledTimes(1);
    expect(orderService.compensate).not.toHaveBeenCalled();

    // inventoryService should not have been processed at all
    expect(inventoryService.process).not.toHaveBeenCalled();
    expect(inventoryService.compensate).not.toHaveBeenCalled();
  });

  test('should retry compensation if a service\'s compensate method fails initially', async () => {
    // accountService will process successfully but its compensate will fail twice then succeed
    const accountService = createMockService('account', { failCompensate: true, failCompensateTimes: 2 });
    // orderService will fail on process to trigger rollback
    const orderService = createMockService('order', { failProcess: true, failProcessCallAttempt: 1 });
    const services = [accountService, orderService];
    const transactionData = { userId: 3, orderId: 303 };

    const orchestrator = new TransactionOrchestrator();
    const transactionId = orchestrator.beginTransaction(services, transactionData);
    try {
      await orchestrator.executeTransaction(transactionId);
    } catch (error) {
      // Expected error
    }
    const state = orchestrator.getTransactionState(transactionId);
    expect(state).toEqual('ROLLED_BACK');

    // accountService should have been processed and then compensated with retries
    expect(accountService.process).toHaveBeenCalledTimes(1);
    // Ensure that the compensate was retried at least twice; exact count depends on implementation.
    expect(accountService.compensate.mock.calls.length).toBeGreaterThanOrEqual(2);

    // orderService fails so no compensation call is expected for it.
    expect(orderService.process).toHaveBeenCalledTimes(1);
    expect(orderService.compensate).not.toHaveBeenCalled();
  });

  test('should handle multiple concurrent transactions without interference', async () => {
    const createServicesForTransaction = (userId, orderId) => {
      return [
        createMockService('account', { delay: 30 }),
        createMockService('order', { delay: 30 }),
        createMockService('inventory', { delay: 30 })
      ];
    };

    const orchestrator = new TransactionOrchestrator();
    const txData1 = { userId: 4, orderId: 404 };
    const txData2 = { userId: 5, orderId: 505 };

    const services1 = createServicesForTransaction(4, 404);
    const services2 = createServicesForTransaction(5, 505);

    const txId1 = orchestrator.beginTransaction(services1, txData1);
    const txId2 = orchestrator.beginTransaction(services2, txData2);

    const exec1 = orchestrator.executeTransaction(txId1);
    const exec2 = orchestrator.executeTransaction(txId2);

    await Promise.all([exec1, exec2]);

    const state1 = orchestrator.getTransactionState(txId1);
    const state2 = orchestrator.getTransactionState(txId2);
    expect(state1).toEqual('COMMITTED');
    expect(state2).toEqual('COMMITTED');

    services1.forEach(service => {
      expect(service.process).toHaveBeenCalledTimes(1);
      expect(service.compensate).not.toHaveBeenCalled();
    });
    services2.forEach(service => {
      expect(service.process).toHaveBeenCalledTimes(1);
      expect(service.compensate).not.toHaveBeenCalled();
    });
  });
});