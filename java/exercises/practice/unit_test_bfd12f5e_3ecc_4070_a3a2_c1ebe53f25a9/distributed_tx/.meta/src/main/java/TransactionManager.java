package distributed_tx;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.logging.Logger;
import java.util.UUID;

public class TransactionManager {
    private static final Logger logger = Logger.getLogger(TransactionManager.class.getName());

    private enum TransactionState {
        INITIAL, PREPARED, COMMITTED, ROLLEDBACK
    }

    private static class TransactionContext {
        List<ResourceManager> resourceManagers = new ArrayList<>();
        TransactionState state = TransactionState.INITIAL;
    }

    private final Map<UUID, TransactionContext> transactions = new ConcurrentHashMap<>();

    /**
     * Starts a new distributed transaction.
     * @return a unique transaction ID.
     */
    public UUID begin() {
        UUID txId = UUID.randomUUID();
        TransactionContext ctx = new TransactionContext();
        transactions.put(txId, ctx);
        logger.info("Transaction begun: " + txId);
        return txId;
    }

    /**
     * Enlists a resource manager into an existing transaction.
     * @param transactionId the transaction identifier.
     * @param resourceManager the resource manager to enlist.
     */
    public void enlist(UUID transactionId, ResourceManager resourceManager) {
        TransactionContext ctx = transactions.get(transactionId);
        if (ctx == null) {
            throw new IllegalArgumentException("Transaction not found: " + transactionId);
        }
        synchronized (ctx) {
            if (ctx.state != TransactionState.INITIAL) {
                throw new IllegalStateException("Cannot enlist resource, transaction state is " + ctx.state);
            }
            ctx.resourceManagers.add(resourceManager);
            logger.info("Resource enlisted for transaction: " + transactionId);
        }
    }

    /**
     * Prepares all enlisted resource managers.
     * @param transactionId the transaction identifier.
     * @return true if all resource managers prepared successfully, false otherwise.
     */
    public boolean prepare(UUID transactionId) {
        TransactionContext ctx = transactions.get(transactionId);
        if (ctx == null) {
            throw new IllegalArgumentException("Transaction not found: " + transactionId);
        }
        synchronized (ctx) {
            if (ctx.state == TransactionState.PREPARED) {
                logger.info("Prepare already completed for transaction: " + transactionId);
                return true;
            }
            if (ctx.state == TransactionState.ROLLEDBACK) {
                logger.info("Transaction already rolled back: " + transactionId);
                return false;
            }
            logger.info("Preparing transaction: " + transactionId);
            for (ResourceManager rm : ctx.resourceManagers) {
                try {
                    boolean result = rm.prepare(transactionId);
                    if (!result) {
                        logger.warning("Resource failed to prepare for transaction: " + transactionId);
                        rollbackInternal(ctx, transactionId);
                        return false;
                    }
                } catch (Exception e) {
                    logger.warning("Exception during prepare for transaction: " + transactionId + " - " + e.getMessage());
                    rollbackInternal(ctx, transactionId);
                    return false;
                }
            }
            ctx.state = TransactionState.PREPARED;
            logger.info("Transaction prepared: " + transactionId);
            return true;
        }
    }

    /**
     * Commits the transaction if preparation is successful.
     * @param transactionId the transaction identifier.
     */
    public void commit(UUID transactionId) {
        TransactionContext ctx = transactions.get(transactionId);
        if (ctx == null) {
            throw new IllegalArgumentException("Transaction not found: " + transactionId);
        }
        synchronized (ctx) {
            if (ctx.state == TransactionState.COMMITTED) {
                logger.info("Transaction already committed: " + transactionId);
                return;
            }
            if (ctx.state != TransactionState.PREPARED) {
                logger.warning("Transaction not prepared, cannot commit: " + transactionId);
                throw new IllegalStateException("Cannot commit a transaction that is not prepared");
            }
            logger.info("Committing transaction: " + transactionId);
            try {
                for (ResourceManager rm : ctx.resourceManagers) {
                    rm.commit(transactionId);
                }
                ctx.state = TransactionState.COMMITTED;
                logger.info("Transaction committed: " + transactionId);
            } catch (Exception e) {
                logger.warning("Exception during commit for transaction: " + transactionId + " - " + e.getMessage());
                rollbackInternal(ctx, transactionId);
                throw new RuntimeException("Commit failed, transaction rolled back", e);
            }
        }
    }

    /**
     * Rolls back all enlisted resource managers.
     * @param transactionId the transaction identifier.
     */
    public void rollback(UUID transactionId) {
        TransactionContext ctx = transactions.get(transactionId);
        if (ctx == null) {
            throw new IllegalArgumentException("Transaction not found: " + transactionId);
        }
        synchronized (ctx) {
            if (ctx.state == TransactionState.ROLLEDBACK) {
                logger.info("Transaction already rolled back: " + transactionId);
                return;
            }
            rollbackInternal(ctx, transactionId);
        }
    }

    /**
     * Internal method to perform rollback.
     * @param ctx the transaction context.
     * @param transactionId the transaction identifier.
     */
    private void rollbackInternal(TransactionContext ctx, UUID transactionId) {
        logger.info("Rolling back transaction: " + transactionId);
        for (ResourceManager rm : ctx.resourceManagers) {
            try {
                rm.rollback(transactionId);
            } catch (Exception e) {
                logger.warning("Exception during rollback for transaction: " + transactionId + " - " + e.getMessage());
            }
        }
        ctx.state = TransactionState.ROLLEDBACK;
        logger.info("Transaction rolled back: " + transactionId);
    }
}