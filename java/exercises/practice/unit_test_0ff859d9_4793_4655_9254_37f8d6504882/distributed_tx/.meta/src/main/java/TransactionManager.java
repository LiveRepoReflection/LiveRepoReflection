import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.logging.Logger;

public class TransactionManager {
    private final Map<TransactionID, List<ResourceManager>> transactions;
    private final Logger logger;

    public TransactionManager() {
        transactions = new ConcurrentHashMap<>();
        logger = Logger.getLogger(TransactionManager.class.getName());
    }

    public TransactionID begin() {
        TransactionID txId = new TransactionID();
        transactions.put(txId, Collections.synchronizedList(new ArrayList<>()));
        logger.info("Transaction begun: " + txId);
        return txId;
    }

    public void enlist(TransactionID transactionId, ResourceManager resourceManager) {
        List<ResourceManager> rms = transactions.get(transactionId);
        if (rms == null) {
            throw new IllegalArgumentException("Transaction not found: " + transactionId);
        }
        rms.add(resourceManager);
        logger.info("ResourceManager enlisted in transaction: " + transactionId);
    }

    public boolean commit(TransactionID transactionId) {
        List<ResourceManager> rms = transactions.get(transactionId);
        if (rms == null) {
            throw new IllegalArgumentException("Transaction not found: " + transactionId);
        }
        synchronized (rms) {
            logger.info("Starting commit phase for transaction: " + transactionId);
            List<ResourceManager> preparedResources = new ArrayList<>();

            // Phase 1: Prepare
            for (ResourceManager rm : rms) {
                try {
                    boolean prepared = rm.prepare(transactionId);
                    if (prepared) {
                        preparedResources.add(rm);
                        logger.info("ResourceManager prepared successfully for transaction: " + transactionId);
                    } else {
                        logger.warning("ResourceManager failed to prepare for transaction: " + transactionId);
                        rollbackPrepared(preparedResources, transactionId);
                        return false;
                    }
                } catch (Exception e) {
                    logger.severe("Exception during prepare phase for transaction: " + transactionId + " - " + e.getMessage());
                    rollbackPrepared(preparedResources, transactionId);
                    return false;
                }
            }

            // Phase 2: Commit
            for (ResourceManager rm : rms) {
                try {
                    rm.commit(transactionId);
                    logger.info("ResourceManager committed for transaction: " + transactionId);
                } catch (Exception e) {
                    logger.severe("Exception during commit phase for transaction: " + transactionId + " - " + e.getMessage());
                }
            }
            logger.info("Transaction committed: " + transactionId);
            return true;
        }
    }

    private void rollbackPrepared(List<ResourceManager> preparedResources, TransactionID transactionId) {
        for (ResourceManager rm : preparedResources) {
            try {
                rm.rollback(transactionId);
                logger.info("Rolled back ResourceManager for transaction: " + transactionId);
            } catch (Exception e) {
                logger.severe("Exception during rollback phase for transaction: " + transactionId + " - " + e.getMessage());
            }
        }
        logger.info("Transaction rolled back: " + transactionId);
    }

    public void rollback(TransactionID transactionId) {
        List<ResourceManager> rms = transactions.get(transactionId);
        if (rms == null) {
            throw new IllegalArgumentException("Transaction not found: " + transactionId);
        }
        synchronized (rms) {
            logger.info("Starting explicit rollback for transaction: " + transactionId);
            for (ResourceManager rm : rms) {
                try {
                    rm.rollback(transactionId);
                    logger.info("ResourceManager rolled back for transaction: " + transactionId);
                } catch (Exception e) {
                    logger.severe("Exception during rollback for transaction: " + transactionId + " - " + e.getMessage());
                }
            }
            logger.info("Transaction rolled back explicitly: " + transactionId);
        }
    }

    public void recover() {
        logger.info("Starting recovery process");
        // Create a copy of the keys to avoid concurrent modification
        Set<TransactionID> txIds = new HashSet<>(transactions.keySet());
        for (TransactionID txId : txIds) {
            List<ResourceManager> rms = transactions.get(txId);
            if (rms == null) continue;
            synchronized (rms) {
                boolean allPreparedOrCommitted = true;
                for (ResourceManager rm : rms) {
                    TransactionState state = rm.recover(txId);
                    if (!(state == TransactionState.PREPARED || state == TransactionState.COMMITTED)) {
                        allPreparedOrCommitted = false;
                        break;
                    }
                }
                if (allPreparedOrCommitted) {
                    logger.info("Recovery detected in-flight transaction (prepared state): " + txId + ". Completing commit.");
                    for (ResourceManager rm : rms) {
                        try {
                            rm.commit(txId);
                            logger.info("ResourceManager committed during recovery for transaction: " + txId);
                        } catch (Exception e) {
                            logger.severe("Exception during recovery commit for transaction: " + txId + " - " + e.getMessage());
                        }
                    }
                } else {
                    logger.info("Recovery detected inconsistent transaction state for " + txId + ". Performing rollback.");
                    for (ResourceManager rm : rms) {
                        try {
                            rm.rollback(txId);
                            logger.info("ResourceManager rolled back during recovery for transaction: " + txId);
                        } catch (Exception e) {
                            logger.severe("Exception during recovery rollback for transaction: " + txId + " - " + e.getMessage());
                        }
                    }
                }
                transactions.remove(txId);
            }
        }
        logger.info("Recovery process completed");
    }
}