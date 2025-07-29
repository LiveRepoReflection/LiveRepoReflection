const { randomUUID } = require('crypto');

class TransactionCoordinator {
  constructor() {
    // Map from transactionId to an array of operations.
    // Each operation object should contain: prepare, commit, abort, and timeout.
    this.transactions = new Map();
  }

  createTransaction() {
    const txnId = randomUUID();
    this.transactions.set(txnId, []);
    return txnId;
  }

  registerOperation(txnId, operation) {
    if (!this.transactions.has(txnId)) {
      throw new Error(`Transaction ${txnId} does not exist`);
    }
    this.transactions.get(txnId).push(operation);
  }

  async executeTransaction(txnId) {
    if (!this.transactions.has(txnId)) {
      throw new Error(`Transaction ${txnId} does not exist`);
    }

    const operations = this.transactions.get(txnId);

    // Prepare Phase: Execute all prepare operations concurrently with timeouts.
    const preparePromises = operations.map(op =>
      this._withTimeout(() => op.prepare(), op.timeout)
    );
    const prepareResults = await Promise.allSettled(preparePromises);

    const allPrepared = prepareResults.every(result => result.status === 'fulfilled');

    if (allPrepared) {
      // Commit Phase: Execute all commit operations concurrently.
      const commitPromises = operations.map(op =>
        this._withTimeout(() => op.commit(), op.timeout).catch(err => {
          // Log the error internally; in a real-world system you'd use an actual logger.
          return err;
        })
      );
      await Promise.all(commitPromises);
      this.transactions.delete(txnId);
      return 'commit';
    } else {
      // Abort Phase: Execute all abort operations concurrently.
      const abortPromises = operations.map(op =>
        this._withTimeout(() => op.abort(), op.timeout).catch(err => err)
      );
      await Promise.all(abortPromises);
      this.transactions.delete(txnId);
      return 'abort';
    }
  }

  _withTimeout(operationFn, timeout) {
    return new Promise((resolve, reject) => {
      let timedOut = false;
      const timer = setTimeout(() => {
        timedOut = true;
        reject(new Error('Operation timed out'));
      }, timeout);

      Promise.resolve()
        .then(operationFn)
        .then(result => {
          if (!timedOut) {
            clearTimeout(timer);
            resolve(result);
          }
        })
        .catch(err => {
          if (!timedOut) {
            clearTimeout(timer);
            reject(err);
          }
        });
    });
  }
}

module.exports = { TransactionCoordinator };