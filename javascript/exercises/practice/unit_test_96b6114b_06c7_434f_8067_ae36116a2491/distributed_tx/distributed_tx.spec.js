const { transfer } = require('./distributed_tx');

beforeEach(() => {
  // Reset all mock functions before each test
  jest.resetAllMocks();

  global.getShard = jest.fn((accountId) => {
    // Simple deterministic shard mapping:
    // If accountId starts with 'A' return shard 1, if 'B' return shard 2, otherwise shard 3.
    if (accountId.startsWith('A')) return 1;
    if (accountId.startsWith('B')) return 2;
    return 3;
  });

  global.sendPrepare = jest.fn();
  global.sendCommit = jest.fn();
  global.sendRollback = jest.fn();
});

describe('Distributed Transaction Coordinator - transfer', () => {
  test('should successfully commit a transaction across multiple shards', async () => {
    // Arrange: simulate two shards involved.
    // For both shards, prepare and commit succeed.
    global.sendPrepare.mockImplementation((shardId, transactionId, operations) => {
      return Promise.resolve(true);
    });
    global.sendCommit.mockImplementation((shardId, transactionId) => {
      return Promise.resolve();
    });

    // Act
    const result = await transfer('A_account', 'B_account', 100);

    // Assert: Check that sendPrepare and sendCommit were called for both shards.
    expect(global.getShard).toHaveBeenCalledWith('A_account');
    expect(global.getShard).toHaveBeenCalledWith('B_account');
    expect(global.sendPrepare).toHaveBeenCalledTimes(2);
    expect(global.sendCommit).toHaveBeenCalledTimes(2);
    // Expect the result to contain a transactionId and a committed status.
    expect(result).toHaveProperty('transactionId');
    expect(result).toHaveProperty('status', 'committed');
  });

  test('should rollback if one shard fails during the prepare phase', async () => {
    // Arrange: simulate first shard returns true while second shard fails prepare.
    global.sendPrepare.mockImplementation((shardId, transactionId, operations) => {
      if (shardId === 1) return Promise.resolve(true);
      if (shardId === 2) return Promise.resolve(false);
      return Promise.resolve(true);
    });
    // Rollback should always succeed.
    global.sendRollback.mockImplementation((shardId, transactionId) => {
      return Promise.resolve();
    });

    // Act & Assert
    await expect(transfer('A_account', 'B_account', 50)).rejects.toThrow();

    // Prepare should be attempted on both shards.
    expect(global.sendPrepare).toHaveBeenCalledTimes(2);
    // Only the shard that prepared successfully (shard 1) should get a rollback.
    expect(global.sendRollback).toHaveBeenCalledTimes(1);
    expect(global.sendRollback).toHaveBeenCalledWith(1, expect.any(String));
  });

  test('should rollback if a shard fails during the commit phase', async () => {
    // Arrange: simulate prepare succeeds for both shards.
    global.sendPrepare.mockImplementation((shardId, transactionId, operations) => {
      return Promise.resolve(true);
    });
    // Simulate commit: first shard succeeds, second shard fails.
    global.sendCommit.mockImplementation((shardId, transactionId) => {
      if (shardId === 2) return Promise.reject(new Error('Commit failure'));
      return Promise.resolve();
    });
    global.sendRollback.mockImplementation((shardId, transactionId) => {
      return Promise.resolve();
    });

    // Act & Assert
    await expect(transfer('A_account', 'B_account', 75)).rejects.toThrow('Commit failure');

    // Check that prepare was called for both shards.
    expect(global.sendPrepare).toHaveBeenCalledTimes(2);
    // Commit should have been attempted for both shards.
    expect(global.sendCommit).toHaveBeenCalledTimes(2);
    // Since commit failed on shard 2, a rollback should have been issued for both shards.
    // Some implementations may rollback only after commit failure detection.
    expect(global.sendRollback).toHaveBeenCalledTimes(2);
    expect(global.sendRollback).toHaveBeenCalledWith(1, expect.any(String));
    expect(global.sendRollback).toHaveBeenCalledWith(2, expect.any(String));
  });

  test('should return the same result for duplicate (idempotent) requests', async () => {
    // Arrange: simulate success for first transaction.
    global.sendPrepare.mockImplementation((shardId, transactionId, operations) => {
      return Promise.resolve(true);
    });
    global.sendCommit.mockImplementation((shardId, transactionId) => {
      return Promise.resolve();
    });

    // Act: call transfer the first time.
    const firstResult = await transfer('A_account', 'B_account', 100);

    // Record call counts after first call.
    const prepareCallCountAfterFirst = global.sendPrepare.mock.calls.length;
    const commitCallCountAfterFirst = global.sendCommit.mock.calls.length;

    // Act: call transfer with the same parameters again (simulate duplicate request).
    const secondResult = await transfer('A_account', 'B_account', 100);

    // Assert: the results should be identical.
    expect(secondResult).toEqual(firstResult);
    // And the underlying shard functions should NOT be called again.
    expect(global.sendPrepare.mock.calls.length).toBe(prepareCallCountAfterFirst);
    expect(global.sendCommit.mock.calls.length).toBe(commitCallCountAfterFirst);
  });

  test('should handle concurrent transactions successfully', async () => {
    // Arrange: For concurrent transactions, simulate success.
    global.sendPrepare.mockImplementation((shardId, transactionId, operations) => {
      return Promise.resolve(true);
    });
    global.sendCommit.mockImplementation((shardId, transactionId) => {
      return Promise.resolve();
    });

    // Act: execute two transfers concurrently with different parameters.
    const transfers = [
      transfer('A_account1', 'B_account1', 100),
      transfer('A_account2', 'B_account2', 200)
    ];

    const results = await Promise.all(transfers);

    // Assert: both transactions should complete with a committed status and unique transaction IDs.
    expect(results[0]).toHaveProperty('status', 'committed');
    expect(results[1]).toHaveProperty('status', 'committed');
    expect(results[0].transactionId).not.toEqual(results[1].transactionId);

    // For each transaction, two shards should have been contacted.
    expect(global.sendPrepare.mock.calls.length).toBe(4);
    expect(global.sendCommit.mock.calls.length).toBe(4);
  });
});