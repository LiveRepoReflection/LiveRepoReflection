const TransactionCoordinator = require('../tx_coordinator');
const { Service } = require('../service');

describe('TransactionCoordinator', () => {
  let coordinator;
  let service1;
  let service2;

  beforeEach(() => {
    service1 = new Service('Service1', 1); // Always succeeds.
    service2 = new Service('Service2', 1); // Always succeeds.
    // Create a coordinator with a timeout of 200ms.
    coordinator = new TransactionCoordinator([service1, service2], 200);
  });

  test('should commit transaction successfully when all services succeed', async () => {
    const txid = coordinator.startTransaction();
    const data = { key: 'value' };
    await expect(coordinator.executeTransaction(txid, data)).resolves.toBeUndefined();
  });

  test('should abort transaction if one service fails to prepare', async () => {
    // Create a service that always fails during preparation.
    const failingService = new Service('FailingService', 0);
    coordinator = new TransactionCoordinator([service1, failingService], 200);
    const txid = coordinator.startTransaction();
    const data = { key: 'value' };
    await expect(coordinator.executeTransaction(txid, data)).rejects.toThrow();
  });

  test('should abort transaction if service times out during prepare', async () => {
    // Create a service that delays its response beyond the coordinator timeout.
    const slowService = new Service('SlowService', 1);
    slowService.prepare = function(txid, data) {
      return new Promise((resolve, reject) => {
        setTimeout(() => {
          this.stagingArea = { ...data };
          console.log(`${this.name}: Prepared transaction ${txid} (slow)`);
          resolve(true);
        }, 500); // Delay exceeds the coordinator's timeout of 200ms.
      });
    };

    coordinator = new TransactionCoordinator([service1, slowService], 200);
    const txid = coordinator.startTransaction();
    const data = { key: 'value' };
    await expect(coordinator.executeTransaction(txid, data)).rejects.toThrow();
  });

  test('should handle multiple concurrent transactions successfully', async () => {
    const transactions = [];
    // Launch 5 concurrent transactions.
    for (let i = 0; i < 5; i++) {
      const txid = coordinator.startTransaction();
      transactions.push(coordinator.executeTransaction(txid, { transaction: i }));
    }
    // All transactions should commit successfully.
    await expect(Promise.all(transactions)).resolves.toEqual(expect.arrayContaining(new Array(5).fill(undefined)));
  });

  test('should abort transaction if a service fails during commit phase', async () => {
    // Override commit to simulate a failure within a service.
    const unreliableService = new Service('UnreliableService', 1);
    unreliableService.commit = function(txid) {
      return new Promise((resolve, reject) => {
        setTimeout(() => {
          console.error(`${this.name}: Simulated commit failure for transaction ${txid}`);
          reject(new Error(`${this.name}: Commit failed`));
        }, 100);
      });
    };

    coordinator = new TransactionCoordinator([service1, unreliableService], 200);
    const txid = coordinator.startTransaction();
    const data = { key: 'value' };
    await expect(coordinator.executeTransaction(txid, data)).rejects.toThrow();
  });
});