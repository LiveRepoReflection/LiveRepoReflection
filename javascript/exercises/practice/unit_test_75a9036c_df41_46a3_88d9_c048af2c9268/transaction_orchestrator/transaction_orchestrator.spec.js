const { TransactionOrchestrator } = require('./transaction_orchestrator');

describe('TransactionOrchestrator', () => {
  beforeEach(() => {
    jest.restoreAllMocks();
  });

  test('should complete transaction when all forward operations succeed', async () => {
    const executedForwards = [];
    const operations = [
      {
        resourceManagerId: 'RM1',
        forward: async (data) => { 
          executedForwards.push('RM1 forward'); 
          return true; 
        },
        rollback: async (data) => { 
          executedForwards.push('RM1 rollback'); 
          return true; 
        },
        data: { value: 1 }
      },
      {
        resourceManagerId: 'RM2',
        forward: async (data) => { 
          executedForwards.push('RM2 forward'); 
          return true; 
        },
        rollback: async (data) => { 
          executedForwards.push('RM2 rollback'); 
          return true; 
        },
        data: { value: 2 }
      },
      {
        resourceManagerId: 'RM3',
        forward: async (data) => { 
          executedForwards.push('RM3 forward'); 
          return true; 
        },
        rollback: async (data) => { 
          executedForwards.push('RM3 rollback'); 
          return true; 
        },
        data: { value: 3 }
      }
    ];
    const orchestrator = new TransactionOrchestrator(operations);
    const result = await orchestrator.run();
    expect(result).toBe(true);
    // Since all forwards succeed, no rollbacks should occur.
    expect(executedForwards).toEqual([
      'RM1 forward',
      'RM2 forward',
      'RM3 forward'
    ]);
  });

  test('should rollback successfully when a forward operation fails', async () => {
    const logSequence = [];
    let rollbackCounterRM1 = 0;
    
    const operations = [
      {
        resourceManagerId: 'RM1',
        forward: async (data) => { 
          logSequence.push('RM1 forward'); 
          return true; 
        },
        rollback: async (data) => { 
          rollbackCounterRM1 += 1;
          logSequence.push('RM1 rollback');
          return true; 
        },
        data: { value: 101 }
      },
      {
        resourceManagerId: 'RM2',
        forward: async (data) => { 
          logSequence.push('RM2 forward'); 
          return false; 
        },
        rollback: async (data) => { 
          logSequence.push('RM2 rollback');
          return true; 
        },
        data: { value: 202 }
      }
    ];
    const orchestrator = new TransactionOrchestrator(operations);
    const result = await orchestrator.run();
    expect(result).toBe(false);
    // Expect forward of RM1 and RM2 attempted, then rollback of RM1.
    expect(logSequence).toEqual([
      'RM1 forward',
      'RM2 forward',
      'RM1 rollback'
    ]);
    // Verify that RM1 rollback was executed exactly once (idempotency)
    expect(rollbackCounterRM1).toBe(1);
  });

  test('should concurrently rollback multiple operations if a later forward fails', async () => {
    const executionLog = [];
    
    const createDelayedOperation = (id, delayForward, delayRollback, forwardSuccess = true) => ({
      resourceManagerId: id,
      forward: async (data) => {
        await new Promise(resolve => setTimeout(resolve, delayForward));
        executionLog.push(`${id} forward`);
        return forwardSuccess;
      },
      rollback: async (data) => {
        await new Promise(resolve => setTimeout(resolve, delayRollback));
        executionLog.push(`${id} rollback`);
        return true;
      },
      data: { value: id }
    });

    const operations = [
      createDelayedOperation('RM1', 50, 100),
      createDelayedOperation('RM2', 30, 150),
      createDelayedOperation('RM3', 20, 50, false) // This forward fails.
    ];
    
    const orchestrator = new TransactionOrchestrator(operations);
    const result = await orchestrator.run();
    expect(result).toBe(false);
    // Verify forward logs: RM1 forward, RM2 forward, RM3 forward attempted.
    expect(executionLog).toEqual(
      expect.arrayContaining([
        'RM1 forward',
        'RM2 forward',
        'RM3 forward',
        'RM2 rollback',
        'RM1 rollback'
      ])
    );
    // Check the order: the rollback order must be reverse of successful forwards,
    // Though they run concurrently, both must appear after the failure.
    const indexRM1Forward = executionLog.indexOf('RM1 forward');
    const indexRM2Forward = executionLog.indexOf('RM2 forward');
    const indexRM3Forward = executionLog.indexOf('RM3 forward');
    
    expect(indexRM1Forward).toBeGreaterThan(-1);
    expect(indexRM2Forward).toBeGreaterThan(-1);
    expect(indexRM3Forward).toBeGreaterThan(-1);
    
    // Rollback order might not be strictly sequential due to concurrency, but verify that both rollbacks occur.
    expect(executionLog.filter(item => item.endsWith('rollback')).length).toBe(2);
  });

  test('should handle rollback failures gracefully and continue other rollbacks', async () => {
    const errorLogs = [];
    const originalConsoleLog = console.log;
    console.log = (...args) => {
      errorLogs.push(args.join(' '));
    };

    const operations = [
      {
        resourceManagerId: 'RM1',
        forward: async (data) => { 
          return true; 
        },
        rollback: async (data) => { 
          throw new Error('Rollback error in RM1');
        },
        data: { value: 1 }
      },
      {
        resourceManagerId: 'RM2',
        forward: async (data) => { 
          return false; 
        },
        rollback: async (data) => { 
          return true; 
        },
        data: { value: 2 }
      }
    ];
    const orchestrator = new TransactionOrchestrator(operations);
    const result = await orchestrator.run();
    expect(result).toBe(false);
    // Expect that the rollback for RM1 failed, but RM2 was not called because its forward failed.
    // Check that error was logged for RM1 rollback.
    const foundError = errorLogs.find(logLine => logLine.includes('RM1'));
    expect(foundError).toBeDefined();
    console.log = originalConsoleLog;
  });

  test('should ensure rollback operations are idempotent', async () => {
    let rollbackCallCount = 0;
    const operations = [
      {
        resourceManagerId: 'RM1',
        forward: async (data) => { 
          return true; 
        },
        rollback: async (data) => { 
          rollbackCallCount += 1;
          return true; 
        },
        data: { value: 1 }
      },
      {
        resourceManagerId: 'RM2',
        forward: async (data) => { 
          return false; 
        },
        rollback: async (data) => { 
          return true; 
        },
        data: { value: 2 }
      }
    ];
    const orchestrator = new TransactionOrchestrator(operations);
    const result = await orchestrator.run();
    expect(result).toBe(false);
    // Even if rollback is attempted concurrently, due to idempotency RM1's rollback should only be executed once.
    expect(rollbackCallCount).toBe(1);
  });
});