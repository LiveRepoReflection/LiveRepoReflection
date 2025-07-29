'use strict';

const GLOBAL_TIMEOUT = 30000; // 30 seconds global timeout

async function coordinateTransaction(operations) {
  // Helper promise for global timeout
  const timeoutPromise = new Promise((resolve) => {
    setTimeout(() => {
      resolve('timeout');
    }, GLOBAL_TIMEOUT);
  });

  // Main transaction process
  const transactionPromise = (async () => {
    // Preparation Phase: Execute prepare for each operation sequentially
    for (const op of operations) {
      try {
        const prepared = await op.prepare(op.data);
        if (!prepared) {
          // If any preparation returns false, rollback all and fail
          await rollbackOperations(operations);
          return false;
        }
      } catch (error) {
        // On error during prepare phase, rollback all and fail
        await rollbackOperations(operations);
        return false;
      }
    }

    // Commit Phase: Execute commit concurrently
    try {
      await Promise.all(operations.map((op) => op.execute(op.data)));
      return true;
    } catch (error) {
      // If any commit execution fails, rollback previously executed operations
      await rollbackOperations(operations);
      return false;
    }
  })();

  // Race between the transaction and the global timeout
  const result = await Promise.race([transactionPromise, timeoutPromise]);

  if (result === 'timeout') {
    // Global timeout reached, perform rollback on all operations
    await rollbackOperations(operations);
    return false;
  }

  return result;
}

// Helper function to rollback all operations concurrently.
// Assumes that each operation’s execute function is idempotent.
async function rollbackOperations(operations) {
  const rollbackPromises = operations.map((op) =>
    op.execute(op.data).catch(() => {
      // Ignore individual rollback errors
    })
  );
  await Promise.all(rollbackPromises);
}

module.exports = { coordinateTransaction };