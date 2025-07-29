const { randomUUID } = require('crypto');

const TRANSACTION_TIMEOUT_MS = 500;

const transactions = new Map();

function begin() {
  const transactionId = randomUUID();
  transactions.set(transactionId, { services: [], data: new Map() });
  return transactionId;
}

function enlist(transactionId, serviceEndpoint) {
  if (!transactions.has(transactionId)) {
    throw new Error(`Transaction ${transactionId} does not exist`);
  }
  const txn = transactions.get(transactionId);
  txn.services.push(serviceEndpoint);
}

function setData(transactionId, serviceEndpoint, data) {
  if (!transactions.has(transactionId)) {
    throw new Error(`Transaction ${transactionId} does not exist`);
  }
  const txn = transactions.get(transactionId);
  txn.data.set(serviceEndpoint, data);
}

async function commitTransaction(transactionId) {
  if (!transactions.has(transactionId)) {
    throw new Error(`Transaction ${transactionId} does not exist`);
  }
  const txn = transactions.get(transactionId);
  const services = txn.services;
  const results = await Promise.all(services.map(async service => {
    const data = txn.data.get(service);
    return prepareWithTimeout(service, transactionId, data);
  }));

  const allPrepared = results.every(result => result === true);

  if (!allPrepared) {
    await Promise.all(services.map(async service => {
      await commitWithTimeout(service, transactionId, true);
    }));
    transactions.delete(transactionId);
    return false;
  } else {
    await Promise.all(services.map(async service => {
      await commitWithTimeout(service, transactionId);
    }));
    transactions.delete(transactionId);
    return true;
  }
}

function prepareWithTimeout(service, transactionId, data) {
  return withTimeout(
    Promise.resolve()
      .then(() => service.prepare(transactionId, data))
      .catch(() => false),
    TRANSACTION_TIMEOUT_MS,
    false
  );
}

function commitWithTimeout(service, transactionId, rollbackFlag = false) {
  const commitPromise = Promise.resolve()
    .then(() => {
      if (rollbackFlag) {
        return service.commit(transactionId, true);
      }
      return service.commit(transactionId);
    })
    .catch(err => {
      console.error(`Error during commit for transaction ${transactionId}: ${err.message}`);
    });
  return withTimeout(commitPromise, TRANSACTION_TIMEOUT_MS, undefined);
}

function withTimeout(promise, ms, timeoutValue) {
  return Promise.race([
    promise,
    new Promise(resolve => setTimeout(() => resolve(timeoutValue), ms))
  ]);
}

module.exports = {
  begin,
  enlist,
  setData,
  commitTransaction
};