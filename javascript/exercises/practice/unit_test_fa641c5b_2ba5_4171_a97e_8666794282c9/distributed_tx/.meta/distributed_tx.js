const fs = require('fs');
const path = require('path');

// Global registry to store transaction context for recovery.
const transactionRegistry = {};

// Utility function: Sleep for given milliseconds.
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Utility function: Wrap a promise with a timeout.
function promiseWithTimeout(promise, timeout) {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      reject(new Error("Timeout"));
    }, timeout);
    promise.then(
      (value) => {
        clearTimeout(timer);
        resolve(value);
      },
      (err) => {
        clearTimeout(timer);
        reject(err);
      }
    );
  });
}

// Log file helpers: Each transaction log is stored in a file named "<txId>_log.json" in the current directory.
function getLogFilePath(txId) {
  return path.join(__dirname, `${txId}_log.json`);
}

function writeLog(txId, logData) {
  const filePath = getLogFilePath(txId);
  fs.writeFileSync(filePath, JSON.stringify(logData, null, 2));
}

function updateLog(txId, logData) {
  writeLog(txId, logData);
}

function readLog(txId) {
  const filePath = getLogFilePath(txId);
  if (fs.existsSync(filePath)) {
    const content = fs.readFileSync(filePath, { encoding: 'utf8' });
    try {
      return JSON.parse(content);
    } catch(e) {
      return null;
    }
  }
  return null;
}

/**
 * runTransaction implements a distributed transaction coordinator using the two-phase commit (2PC) protocol.
 * @param {string} txId - A unique transaction identifier.
 * @param {Array} participants - Array of participant objects. Each must have a unique 'id' and the functions:
 *      prepare(): Promise<string> -> returns "vote_commit" or "vote_abort"
 *      commit(): Promise<void>
 *      rollback(): Promise<void>
 * @param {Object} config - Optional configuration object with:
 *      timeout: number (timeout in ms for each participant call)
 *      simulateCrash: boolean (if true, simulates a crash after prepare phase)
 *      maxRetries: number (maximum retry attempts for each participant call)
 * @returns {Promise<boolean>} - Resolves to true if transaction committed, false if rolled back.
 */
async function runTransaction(txId, participants, config = {}) {
  const timeout = config.timeout || 200;
  const maxRetries = config.maxRetries || 3;
  const simulateCrash = config.simulateCrash || false;
  const votes = {};

  // Phase 1: Prepare - invoke prepare() on all participants, with retry and timeout.
  for (const participant of participants) {
    let attempts = 0;
    let vote = 'vote_abort';
    while (attempts < maxRetries) {
      try {
        vote = await promiseWithTimeout(
          participant.prepare(),
          timeout
        );
        if (vote !== 'vote_commit' && vote !== 'vote_abort') {
          // Unexpected vote: treat as abort.
          vote = 'vote_abort';
        }
        break; // Exit loop on successful prepare call.
      } catch (e) {
        attempts++;
        if (attempts >= maxRetries) {
          vote = 'vote_abort';
          break;
        }
        // Exponential backoff before retrying.
        await sleep(50 * Math.pow(2, attempts));
      }
    }
    votes[participant.id] = vote;
  }

  // Persist log for the prepare phase.
  let logData = {
    txId,
    phase: 'PREPARE',
    votes,
    state: 'PENDING'
  };
  writeLog(txId, logData);

  // Save transaction context for recovery.
  transactionRegistry[txId] = {
    participants,
    timeout,
    maxRetries
  };

  // Determine if transaction should commit.
  const shouldCommit = Object.values(votes).every(vote => vote === 'vote_commit');

  // If simulateCrash flag is set, simulate crash before Phase 2.
  if (simulateCrash) {
    throw new Error("Simulated crash after prepare phase");
  }

  // Phase 2: Commit or Rollback.
  if (shouldCommit) {
    // Commit phase for each participant with retry.
    for (const participant of participants) {
      let attempts = 0;
      while (attempts < maxRetries) {
        try {
          await promiseWithTimeout(
            participant.commit(),
            timeout
          );
          break;
        } catch (e) {
          attempts++;
          if (attempts >= maxRetries) {
            // In persistent failure, fallback to rollback.
            try {
              await participant.rollback();
            } catch (err) {
              // If rollback fails, continue; idempotency ensures safety.
            }
            break;
          }
          await sleep(50 * Math.pow(2, attempts));
        }
      }
    }
    logData.state = 'COMMITTED';
    logData.phase = 'COMPLETE';
    updateLog(txId, logData);
    // Clear transaction context.
    delete transactionRegistry[txId];
    return true;
  } else {
    // Rollback phase for each participant with retry.
    for (const participant of participants) {
      let attempts = 0;
      while (attempts < maxRetries) {
        try {
          await promiseWithTimeout(
            participant.rollback(),
            timeout
          );
          break;
        } catch (e) {
          attempts++;
          if (attempts >= maxRetries) {
            break;
          }
          await sleep(50 * Math.pow(2, attempts));
        }
      }
    }
    logData.state = 'ROLLED_BACK';
    logData.phase = 'COMPLETE';
    updateLog(txId, logData);
    delete transactionRegistry[txId];
    return false;
  }
}

/**
 * recoverTransaction attempts to resolve an incomplete distributed transaction based on its log.
 * @param {string} txId - The transaction identifier to recover.
 * @returns {Promise<boolean>} - Resolves to true if transaction is committed upon recovery, false if rolled back.
 */
async function recoverTransaction(txId) {
  const storedLog = readLog(txId);
  if (!storedLog) {
    throw new Error(`No log found for transaction ${txId}`);
  }
  // If transaction is already complete, return its state.
  if (storedLog.state === 'COMMITTED') {
    return true;
  }
  if (storedLog.state === 'ROLLED_BACK') {
    return false;
  }
  // Retrieve participants from the global transaction registry.
  const txContext = transactionRegistry[txId];
  if (!txContext) {
    throw new Error(`No transaction context available for ${txId}`);
  }
  const { participants, timeout, maxRetries } = txContext;

  // Decide action based on prepare votes stored in the log.
  const votes = storedLog.votes;
  const shouldCommit = Object.values(votes).every(vote => vote === 'vote_commit');

  if (shouldCommit) {
    for (const participant of participants) {
      let attempts = 0;
      while (attempts < maxRetries) {
        try {
          await promiseWithTimeout(
            participant.commit(),
            timeout
          );
          break;
        } catch (e) {
          attempts++;
          if (attempts >= maxRetries) {
            try {
              await participant.rollback();
            } catch (err) {
              // Continue if rollback fails.
            }
            break;
          }
          await sleep(50 * Math.pow(2, attempts));
        }
      }
    }
    storedLog.state = 'COMMITTED';
    storedLog.phase = 'COMPLETE';
    updateLog(txId, storedLog);
    delete transactionRegistry[txId];
    return true;
  } else {
    for (const participant of participants) {
      let attempts = 0;
      while (attempts < maxRetries) {
        try {
          await promiseWithTimeout(
            participant.rollback(),
            timeout
          );
          break;
        } catch (e) {
          attempts++;
          if (attempts >= maxRetries) {
            break;
          }
          await sleep(50 * Math.pow(2, attempts));
        }
      }
    }
    storedLog.state = 'ROLLED_BACK';
    storedLog.phase = 'COMPLETE';
    updateLog(txId, storedLog);
    delete transactionRegistry[txId];
    return false;
  }
}

module.exports = { runTransaction, recoverTransaction };