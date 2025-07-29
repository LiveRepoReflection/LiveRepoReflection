package distributed_tx;

import java.util.*;
import java.util.concurrent.*;
import java.util.logging.Logger;
import java.util.concurrent.locks.ReentrantLock;

public class TransactionCoordinator {
    private final ConcurrentMap<UUID, List<Resource>> transactionResources = new ConcurrentHashMap<>();
    private final Logger logger = Logger.getLogger(TransactionCoordinator.class.getName());
    // Basic deadlock prevention mechanism using resource locks by resource identifier.
    private final ConcurrentMap<String, ReentrantLock> resourceLocks = new ConcurrentHashMap<>();

    public TransactionContext beginTransaction() {
        TransactionContext context = new TransactionContext(UUID.randomUUID());
        transactionResources.put(context.getTransactionId(), new CopyOnWriteArrayList<>());
        logger.info("Transaction begun: " + context.getTransactionId());
        return context;
    }

    public void enlistResource(TransactionContext context, Resource resource) {
        List<Resource> resources = transactionResources.get(context.getTransactionId());
        if (resources != null) {
            resources.add(resource);
            logger.info("Resource enlisted for transaction: " + context.getTransactionId());
        }
    }

    public void commitTransaction(TransactionContext context) throws Exception {
        List<Resource> resources = transactionResources.get(context.getTransactionId());
        if (resources == null) {
            throw new IllegalArgumentException("Transaction not found: " + context.getTransactionId());
        }
        // Phase 1: Prepare
        for (Resource resource : resources) {
            boolean prepared = retryPrepare(resource, context);
            if (!prepared) {
                logger.warning("Prepare failed for transaction: " + context.getTransactionId());
                rollbackTransaction(context);
                return;
            }
        }
        // Phase 2: Commit
        List<Resource> committedResources = new ArrayList<>();
        for (Resource resource : resources) {
            boolean committed;
            try {
                committed = resource.commit(context);
            } catch (InterruptedException e) {
                logger.severe("Interrupted during commit: " + e.getMessage());
                Thread.currentThread().interrupt();
                committed = false;
            }
            if (!committed) {
                logger.warning("Commit failed for a resource in transaction: " + context.getTransactionId());
                // Attempt to rollback committed resources
                for (Resource committedResource : committedResources) {
                    safeRollback(committedResource, context);
                }
                // Also attempt rollback on the resource that failed commit.
                safeRollback(resource, context);
                throw new Exception("Commit failed and rollback completed for transaction: " + context.getTransactionId());
            } else {
                committedResources.add(resource);
            }
        }
        logger.info("Transaction committed successfully: " + context.getTransactionId());
    }

    public void rollbackTransaction(TransactionContext context) throws Exception {
        List<Resource> resources = transactionResources.get(context.getTransactionId());
        if (resources == null) {
            throw new IllegalArgumentException("Transaction not found: " + context.getTransactionId());
        }
        Exception rollbackException = null;
        for (Resource resource : resources) {
            boolean rolledBack = safeRollback(resource, context);
            if (!rolledBack) {
                rollbackException = new Exception("Rollback failed for one or more resources in transaction: " + context.getTransactionId());
            }
        }
        if (rollbackException != null) {
            throw rollbackException;
        }
        logger.info("Transaction rolled back: " + context.getTransactionId());
    }

    private boolean retryPrepare(Resource resource, TransactionContext context) throws InterruptedException {
        int maxRetries = 3;
        long backoff = 50; // initial backoff in milliseconds
        for (int i = 0; i < maxRetries; i++) {
            try {
                boolean success = resource.prepare(context);
                if (success) {
                    return true;
                }
            } catch (InterruptedException e) {
                logger.severe("Interrupted during prepare: " + e.getMessage());
                Thread.currentThread().interrupt();
                return false;
            }
            Thread.sleep(backoff);
            backoff *= 2;
        }
        return false;
    }

    private boolean safeRollback(Resource resource, TransactionContext context) {
        try {
            return resource.rollback(context);
        } catch (InterruptedException e) {
            logger.severe("Interrupted during rollback: " + e.getMessage());
            Thread.currentThread().interrupt();
            return false;
        }
    }

    // Deadlock prevention: lock a resource by its identifier.
    public void lockResource(String resourceId) {
        ReentrantLock lock = resourceLocks.computeIfAbsent(resourceId, id -> new ReentrantLock());
        try {
            if (!lock.tryLock(500, TimeUnit.MILLISECONDS)) {
                throw new RuntimeException("Deadlock detected for resource: " + resourceId);
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new RuntimeException("Interrupted while acquiring lock for resource: " + resourceId);
        }
    }

    public void unlockResource(String resourceId) {
        ReentrantLock lock = resourceLocks.get(resourceId);
        if (lock != null && lock.isHeldByCurrentThread()) {
            lock.unlock();
        }
    }
}