class TransactionOrchestrator {
  constructor(operations) {
    this.operations = operations;
    // Map to track executed rollback operations for idempotency.
    this.rollbackTracker = new Map();
  }

  async run() {
    const successfulOps = [];
    for (const op of this.operations) {
      try {
        const success = await op.forward(op.data);
        console.log(`${op.resourceManagerId} forward`);
        if (!success) {
          console.log(`${op.resourceManagerId} forward failed`);
          await this.rollback(successfulOps);
          return false;
        }
        successfulOps.push(op);
      } catch (err) {
        console.log(`${op.resourceManagerId} forward error: ${err.message}`);
        await this.rollback(successfulOps);
        return false;
      }
    }
    return true;
  }

  async rollback(successfulOps) {
    // Rollback in the reverse order concurrently.
    const reversedOps = successfulOps.slice().reverse();
    const rollbackPromises = [];
    for (const op of reversedOps) {
      rollbackPromises.push(this.safeRollback(op));
    }
    await Promise.all(rollbackPromises);
  }

  async safeRollback(op) {
    // Check idempotency: if rollback already executed for this resourceManagerId, skip.
    if (this.rollbackTracker.has(op.resourceManagerId)) {
      return this.rollbackTracker.get(op.resourceManagerId);
    }
    const rollbackPromise = (async () => {
      try {
        console.log(`${op.resourceManagerId} rollback`);
        await op.rollback(op.data);
      } catch (err) {
        console.log(`Error during rollback for ${op.resourceManagerId}: ${err.message}`);
      }
    })();
    this.rollbackTracker.set(op.resourceManagerId, rollbackPromise);
    return rollbackPromise;
  }
}

module.exports = { TransactionOrchestrator };