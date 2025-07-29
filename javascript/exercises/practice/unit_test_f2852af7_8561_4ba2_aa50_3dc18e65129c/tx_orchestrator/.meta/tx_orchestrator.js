const MAX_RETRIES = 5;
const RETRY_DELAY = 50;

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function attemptRollback(service, data, serviceName) {
  let attempts = 0;
  while (attempts < MAX_RETRIES) {
    try {
      await service.rollback(data);
      return;
    } catch (error) {
      attempts++;
      if (attempts >= MAX_RETRIES) {
        throw new Error(
          `Rollback failed for ${serviceName} after ${MAX_RETRIES} attempts: ${error.message}`
        );
      }
      await sleep(RETRY_DELAY);
    }
  }
}

async function executeTransaction(transaction) {
  if (!Array.isArray(transaction)) {
    return Promise.reject(
      new Error("Transaction must be an array of operations")
    );
  }
  
  const commitHistory = [];
  try {
    for (let i = 0; i < transaction.length; i++) {
      const { service, data } = transaction[i];
      if (
        !service ||
        typeof service.commit !== "function" ||
        typeof service.rollback !== "function"
      ) {
        throw new Error(`Invalid service in transaction at index ${i}`);
      }
      await service.commit(data);
      commitHistory.push({ service, data, name: service.name || `Service at index ${i}` });
    }
    return;
  } catch (commitError) {
    const failedOperation = transaction[commitHistory.length];
    const failedServiceName =
      failedOperation && failedOperation.service && failedOperation.service.name
        ? failedOperation.service.name
        : `Unknown Service at index ${commitHistory.length}`;
    for (let j = commitHistory.length - 1; j >= 0; j--) {
      const { service, data, name } = commitHistory[j];
      try {
        await attemptRollback(service, data, name);
      } catch (rollbackError) {
        throw new Error(
          `Transaction aborted due to commit failure at ${failedServiceName}. Additionally, rollback failed for ${name}: ${rollbackError.message}`
        );
      }
    }
    throw new Error(`Transaction aborted due to commit failure at ${failedServiceName}: ${commitError.message}`);
  }
}

module.exports = { executeTransaction };