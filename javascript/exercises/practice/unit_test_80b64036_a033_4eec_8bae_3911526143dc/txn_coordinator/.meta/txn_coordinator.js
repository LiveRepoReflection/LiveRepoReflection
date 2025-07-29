const crypto = require('crypto');

function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function callWithTimeout(promise, timeout) {
  return Promise.race([
    promise,
    new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), timeout))
  ]);
}

async function attemptPrepare(service, transactionId, config) {
  let attempts = config.retryAttempts || 1;
  let backoff = 10;
  let currentAttempt = 0;
  while (currentAttempt < attempts) {
    try {
      if (config.logging) {
        config.logging.log(`Service prepare attempt ${currentAttempt + 1} for transaction ${transactionId}`);
      }
      const result = await callWithTimeout(service.prepare(transactionId), config.timeout || 1000);
      if (result === 'vote commit') {
        return;
      } else {
        throw new Error('vote abort');
      }
    } catch (err) {
      currentAttempt++;
      if (currentAttempt < attempts) {
        if (config.logging) {
          config.logging.log(`Service prepare failed on attempt ${currentAttempt} for transaction ${transactionId}, retrying...`);
        }
        await delay(backoff);
        backoff *= 2;
      } else {
        if (config.logging) {
          config.logging.log(`Service prepare failed after ${attempts} attempts for transaction ${transactionId}`);
        }
        throw err;
      }
    }
  }
}

async function transactionCoordinator(services, config = {}) {
  let transactionId;
  if (crypto.randomUUID) {
    transactionId = crypto.randomUUID();
  } else {
    transactionId = `${Date.now()}_${Math.random().toString(36).substring(2, 10)}`;
  }
  if (config.logging) {
    config.logging.log(`Transaction ${transactionId} started.`);
  }
  try {
    await Promise.all(services.map(service => attemptPrepare(service, transactionId, config)));
  } catch (prepareError) {
    if (config.logging) {
      config.logging.log(`Prepare phase failed for transaction ${transactionId}: ${prepareError.message}`);
    }
    await Promise.all(services.map(service => {
      return service.rollback(transactionId).catch(() => {});
    }));
    if (config.logging) {
      config.logging.log(`Transaction ${transactionId} rolled back.`);
    }
    return false;
  }
  try {
    await Promise.all(services.map(service => service.commit(transactionId)));
  } catch (commitError) {
    if (config.logging) {
      config.logging.log(`Commit phase encountered error for transaction ${transactionId}: ${commitError.message}`);
    }
    await Promise.all(services.map(service => {
      return service.rollback(transactionId).catch(() => {});
    }));
    if (config.logging) {
      config.logging.log(`Transaction ${transactionId} rolled back due to commit failure.`);
    }
    return false;
  }
  if (config.logging) {
    config.logging.log(`Transaction ${transactionId} committed successfully.`);
  }
  return true;
}

module.exports = { transactionCoordinator };