class TransactionCoordinator {
  constructor() {
    this.actions = [];
  }

  addAction(action, compensate) {
    this.actions.push({ action, compensate });
  }

  async run() {
    // If no actions are added, return true immediately.
    if (this.actions.length === 0) return true;

    // Track compensating actions for successfully executed actions.
    const executedCompensations = [];

    try {
      for (let i = 0; i < this.actions.length; i++) {
        const { action, compensate } = this.actions[i];
        // Execute the current action.
        await action();
        // Record its compensation function for potential rollback.
        executedCompensations.push(compensate);
      }
      // All actions succeeded.
      return true;
    } catch (actionError) {
      // An action failed; start rollback in reverse order.
      for (let i = executedCompensations.length - 1; i >= 0; i--) {
        try {
          await executedCompensations[i]();
        } catch (compError) {
          console.error(compError.message);
        }
      }
      return false;
    }
  }
}

module.exports = { TransactionCoordinator };