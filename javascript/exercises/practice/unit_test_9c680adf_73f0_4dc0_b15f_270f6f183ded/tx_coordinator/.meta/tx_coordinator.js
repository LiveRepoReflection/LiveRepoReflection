const { Service } = require('./service');

class TransactionCoordinator {
  constructor(services, timeout) {
    this.services = services;
    this.timeout = timeout; // Timeout in milliseconds for each operation
    this.txCounter = 0; // To generate unique transaction IDs
  }

  // Generate and return a unique transaction ID.
  startTransaction() {
    this.txCounter += 1;
    return `tx-${this.txCounter}-${Date.now()}`;
  }

  // Utility method to add a timeout to a promise.
  callWithTimeout(promise, timeout, errorMessage) {
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        reject(new Error(errorMessage));
      }, timeout);
      promise
        .then((result) => {
          clearTimeout(timer);
          resolve(result);
        })
        .catch((err) => {
          clearTimeout(timer);
          reject(err);
        });
    });
  }

  // Execute the transaction across all services.
  async executeTransaction(txid, data) {
    // Phase 1: Prepare
    try {
      const preparePromises = this.services.map((service) => {
        return this.callWithTimeout(
          service.prepare(txid, data),
          this.timeout,
          `${service.name}: Prepare timed out for transaction ${txid}`
        );
      });
      // Wait for all services to complete prepare.
      await Promise.all(preparePromises);
    } catch (err) {
      // If any service fails in prepare phase, abort the transaction.
      await this.abortAll(txid);
      throw new Error(`Transaction ${txid} aborted during prepare phase: ${err.message}`);
    }

    // Phase 2: Commit
    try {
      const commitPromises = this.services.map((service) => {
        return this.callWithTimeout(
          service.commit(txid),
          this.timeout,
          `${service.name}: Commit timed out for transaction ${txid}`
        );
      });
      await Promise.all(commitPromises);
    } catch (err) {
      // If commit fails for any service, attempt to abort.
      await this.abortAll(txid);
      throw new Error(`Transaction ${txid} aborted during commit phase: ${err.message}`);
    }
  }

  // Abort the transaction in all services.
  async abortAll(txid) {
    const abortPromises = this.services.map((service) => {
      return this.callWithTimeout(
        service.abort(txid),
        this.timeout,
        `${service.name}: Abort timed out for transaction ${txid}`
      ).catch((err) => {
        // Even if abort fails, log and continue.
        console.error(`${service.name}: Error during abort: ${err.message}`);
      });
    });
    await Promise.all(abortPromises);
  }
}

module.exports = TransactionCoordinator;