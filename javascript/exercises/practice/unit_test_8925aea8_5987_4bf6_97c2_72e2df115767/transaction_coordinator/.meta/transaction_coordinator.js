const participants = {};
const transactions = {};
let transactionCounter = 0;

function registerParticipant(participantId, commitFunction, rollbackFunction) {
  if (!participantId || typeof commitFunction !== 'function' || typeof rollbackFunction !== 'function') {
    throw new Error('Invalid participant registration');
  }
  participants[participantId] = {
    commit: commitFunction,
    rollback: rollbackFunction,
  };
}

async function initiateTransaction(operations) {
  const transactionId = 'tx-' + (++transactionCounter);
  global.transactionCoordinatorLastId = transactionId;
  transactions[transactionId] = 'pending';

  if (!operations || operations.length === 0) {
    transactions[transactionId] = 'committed';
    return transactionId;
  }

  const opsByParticipant = {};
  for (const op of operations) {
    const { participantId, resourceId } = op;
    if (!participants[participantId]) {
      transactions[transactionId] = 'rolled_back';
      throw new Error(`Participant ${participantId} not registered`);
    }
    if (!opsByParticipant[participantId]) {
      opsByParticipant[participantId] = new Set();
    }
    opsByParticipant[participantId].add(resourceId);
  }

  const commitPromises = [];
  for (const participantId in opsByParticipant) {
    const resourceIds = Array.from(opsByParticipant[participantId]);
    const p = participants[participantId]
      .commit(resourceIds)
      .then(() => ({ participantId, success: true }))
      .catch(error => ({ participantId, success: false, error, resourceIds }));
    commitPromises.push(p);
  }

  const commitResults = await Promise.all(commitPromises);
  const commitFailure = commitResults.find(result => result.success === false);

  if (!commitFailure) {
    transactions[transactionId] = 'committed';
    return transactionId;
  } else {
    const rollbackPromises = [];
    for (const participantId in opsByParticipant) {
      const resourceIds = Array.from(opsByParticipant[participantId]);
      const p = participants[participantId]
        .rollback(resourceIds)
        .catch(err => err);
      rollbackPromises.push(p);
    }
    await Promise.all(rollbackPromises);
    transactions[transactionId] = 'rolled_back';
    throw commitFailure.error;
  }
}

function getTransactionState(transactionId) {
  return transactions[transactionId];
}

module.exports = {
  registerParticipant,
  initiateTransaction,
  getTransactionState,
};