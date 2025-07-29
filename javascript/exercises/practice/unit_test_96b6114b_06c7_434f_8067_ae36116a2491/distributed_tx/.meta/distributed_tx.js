'use strict';

const transactionCache = new Map();
let transactionCounter = 0;

function generateTransactionId() {
  transactionCounter++;
  return `tx_${Date.now()}_${transactionCounter}`;
}

async function transfer(fromAccountId, toAccountId, amount) {
  if (!fromAccountId || !toAccountId || typeof amount !== 'number') {
    throw new Error('Invalid parameters');
  }
  
  const cacheKey = `${fromAccountId}-${toAccountId}-${amount}`;
  if (transactionCache.has(cacheKey)) {
    return transactionCache.get(cacheKey);
  }
  
  const transactionPromise = (async () => {
    const transactionId = generateTransactionId();
    
    const fromShard = getShard(fromAccountId);
    const toShard = getShard(toAccountId);
    
    // Build shard operations mapping
    const shardOperations = new Map();
    if (fromShard === toShard) {
      shardOperations.set(fromShard, [
        { accountId: fromAccountId, amount: amount, type: 'DEBIT' },
        { accountId: toAccountId, amount: amount, type: 'CREDIT' }
      ]);
    } else {
      shardOperations.set(fromShard, [
        { accountId: fromAccountId, amount: amount, type: 'DEBIT' }
      ]);
      shardOperations.set(toShard, [
        { accountId: toAccountId, amount: amount, type: 'CREDIT' }
      ]);
    }
    
    // Two-Phase Commit: Prepare Phase
    const preparedShards = [];
    try {
      await Promise.all([...shardOperations.entries()].map(async ([shardId, operations]) => {
        const prepared = await sendPrepare(shardId, transactionId, operations);
        if (!prepared) {
          throw new Error(`Shard ${shardId} declined prepare`);
        }
        preparedShards.push(shardId);
      }));
    } catch (preparationError) {
      // Rollback shards that prepared successfully
      await Promise.all(preparedShards.map(async (shardId) => {
        await sendRollback(shardId, transactionId);
      }));
      throw preparationError;
    }
    
    // Two-Phase Commit: Commit Phase
    try {
      await Promise.all([...shardOperations.keys()].map(async (shardId) => {
        await sendCommit(shardId, transactionId);
      }));
    } catch (commitError) {
      // If commit fails, rollback all shards involved
      await Promise.all([...shardOperations.keys()].map(async (shardId) => {
        await sendRollback(shardId, transactionId);
      }));
      throw commitError;
    }
    
    return { transactionId, status: 'committed' };
  })();
  
  transactionCache.set(cacheKey, transactionPromise);
  return transactionPromise;
}

module.exports = { transfer };