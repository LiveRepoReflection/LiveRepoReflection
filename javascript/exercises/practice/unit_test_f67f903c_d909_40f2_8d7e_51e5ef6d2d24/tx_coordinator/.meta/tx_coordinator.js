'use strict';
const { randomUUID } = require('crypto');

class TransactionCoordinator {
  registerTransaction() {
    return new Transaction(randomUUID());
  }
}

class Transaction {
  constructor(id) {
    this.id = id;
    this.participants = [];
    this.state = 'pending'; // possible states: pending, committed, rolledback
    this.commitPromise = null;
  }

  addParticipant(commit, rollback) {
    if (typeof commit !== 'function' || typeof rollback !== 'function') {
      throw new Error('Commit and rollback must be functions');
    }
    this.participants.push({
      commitExecuted: false,
      rollbackExecuted: false,
      commit,
      rollback
    });
  }

  async commitTransaction() {
    if (this.commitPromise) {
      return this.commitPromise;
    }
    this.commitPromise = (async () => {
      // If already committed, return immediately.
      if (this.state === 'committed') {
        return;
      }
      // If already rolled back then throw
      if (this.state === 'rolledback') {
        throw new Error('Transaction already rolled back');
      }

      // Execute commit functions concurrently
      const commitPromises = this.participants.map(async (p) => {
        if (!p.commitExecuted) {
          p.commitExecuted = true;
          try {
            return await p.commit();
          } catch (error) {
            throw { participant: p, error };
          }
        }
      });

      const commitResults = await Promise.allSettled(commitPromises);
      const commitErrors = [];
      commitResults.forEach((result) => {
        if (result.status === 'rejected') {
          commitErrors.push(result.reason.error || result.reason);
        }
      });

      // If all commit functions succeeded, mark as committed and finish.
      if (commitErrors.length === 0) {
        this.state = 'committed';
        return;
      } else {
        // If any commit function failed, execute rollback functions concurrently.
        const rollbackPromises = this.participants.map(async (p) => {
          if (!p.rollbackExecuted) {
            p.rollbackExecuted = true;
            try {
              return await p.rollback();
            } catch (error) {
              throw error;
            }
          }
        });
        const rollbackResults = await Promise.allSettled(rollbackPromises);
        const rollbackErrors = [];
        rollbackResults.forEach((result) => {
          if (result.status === 'rejected') {
            rollbackErrors.push(result.reason);
          }
        });
        this.state = 'rolledback';
        const aggregateError = new Error('Transaction failed. See errors property for details.');
        aggregateError.errors = [...commitErrors, ...rollbackErrors];
        throw aggregateError;
      }
    })();
    return this.commitPromise;
  }
}

module.exports = { TransactionCoordinator };