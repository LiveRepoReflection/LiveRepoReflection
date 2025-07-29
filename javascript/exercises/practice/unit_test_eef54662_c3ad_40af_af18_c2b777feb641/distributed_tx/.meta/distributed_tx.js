class TransactionOrchestrator {
  constructor() {
    this.transactions = new Map();
    this.txCounter = 0;
  }

  /**
   * Begins a new transaction.
   * @param {Array} services - Array of service objects each with process and compensate methods.
   * @param {Object} transactionData - Data specific to the transaction.
   * @returns {string} transactionId
   */
  beginTransaction(services, transactionData) {
    const transactionId = `tx_${++this.txCounter}`;
    const transaction = {
      id: transactionId,
      services,
      transactionData,
      state: 'PENDING',
      processedServices: []
    };
    this.transactions.set(transactionId, transaction);
    return transactionId;
  }

  /**
   * Executes the transaction across all services in predefined sequence.
   * On failure, triggers rollback operation.
   *
   * @param {string} transactionId
   * @returns {Promise<void>}
   */
  async executeTransaction(transactionId) {
    if (!this.transactions.has(transactionId)) {
      throw new Error("Transaction id not found");
    }
    const transaction = this.transactions.get(transactionId);
    const { services, transactionData } = transaction;

    try {
      // Process each service in order.
      for (let i = 0; i < services.length; i++) {
        const service = services[i];
        // Call the process method and await its result.
        await service.process(transactionId, transactionData);
        transaction.processedServices.push(service);
      }
      transaction.state = 'COMMITTED';
    } catch (error) {
      // On failure, rollback previously processed services in reverse order.
      await this.rollback(transaction);
      throw error;
    }
  }

  /**
   * Rolls back the transaction by compensating all successfully processed services in reverse order.
   * @param {Object} transaction
   * @returns {Promise<void>}
   */
  async rollback(transaction) {
    const { processedServices, id, transactionData } = transaction;
    for (let i = processedServices.length - 1; i >= 0; i--) {
      const service = processedServices[i];
      await this.callCompensateWithRetry(service, id, transactionData);
    }
    transaction.state = 'ROLLED_BACK';
  }

  /**
   * Attempts to call the compensate method on a service with retry logic.
   * Retries up to 3 times with exponential backoff (delay doubling each retry starting at 100ms).
   *
   * @param {Object} service
   * @param {string} transactionId
   * @param {Object} transactionData
   * @returns {Promise<void>}
   */
  async callCompensateWithRetry(service, transactionId, transactionData) {
    const maxAttempts = 3;
    let attempts = 0;
    let delayTime = 100;

    while (attempts < maxAttempts) {
      try {
        await service.compensate(transactionId, transactionData);
        return;
      } catch (error) {
        attempts++;
        if (attempts >= maxAttempts) {
          console.error(`Compensation failed for a service after ${attempts} attempts: ${error.message}`);
          break;
        }
        await this.sleep(delayTime);
        delayTime *= 2;
      }
    }
  }

  /**
   * Utility function to simulate a delay.
   * @param {number} ms
   * @returns {Promise<void>}
   */
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Retrieves the current state of a transaction.
   *
   * @param {string} transactionId
   * @returns {string} - 'PENDING', 'COMMITTED', or 'ROLLED_BACK'
   */
  getTransactionState(transactionId) {
    if (!this.transactions.has(transactionId)) {
      throw new Error("Transaction id not found");
    }
    return this.transactions.get(transactionId).state;
  }
}

module.exports = {
  TransactionOrchestrator
};