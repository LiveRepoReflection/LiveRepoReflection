import java.util.*;
import java.util.concurrent.*;
import java.util.logging.Logger;
import java.util.logging.Level;

public class DistributedTransactionCoordinator {
    private static final Logger LOGGER = Logger.getLogger(DistributedTransactionCoordinator.class.getName());
    private static final int MAX_RESOURCE_MANAGERS = 10;
    private static final int DEFAULT_TIMEOUT_MS = 1000;
    private static final int MAX_RETRIES = 3;

    private final Map<UUID, TransactionContext> activeTransactions;
    private final ConcurrentMap<ResourceManager, Set<UUID>> resourceLocks;
    private final ExecutorService executorService;

    public DistributedTransactionCoordinator() {
        this.activeTransactions = new ConcurrentHashMap<>();
        this.resourceLocks = new ConcurrentHashMap<>();
        this.executorService = Executors.newCachedThreadPool();
    }

    public UUID beginTransaction() {
        UUID tid = UUID.randomUUID();
        activeTransactions.put(tid, new TransactionContext());
        LOGGER.info("Started transaction: " + tid);
        return tid;
    }

    public boolean enlistResource(UUID tid, ResourceManager rm, String operationDetails) {
        TransactionContext context = activeTransactions.get(tid);
        if (context == null) {
            throw new IllegalStateException("Transaction not found: " + tid);
        }

        if (context.getResourceManagers().size() >= MAX_RESOURCE_MANAGERS) {
            throw new IllegalStateException("Maximum number of resource managers reached");
        }

        context.addResourceManager(rm, operationDetails);
        LOGGER.info("Enlisted resource manager in transaction " + tid);
        return true;
    }

    public boolean commitTransaction(UUID tid) {
        TransactionContext context = activeTransactions.get(tid);
        if (context == null) {
            throw new IllegalStateException("Transaction not found: " + tid);
        }

        try {
            // Prepare phase
            if (!preparePhase(tid, context)) {
                rollbackTransaction(tid);
                return false;
            }

            // Commit phase
            return commitPhase(tid, context);
        } finally {
            cleanupTransaction(tid);
        }
    }

    public void rollbackTransaction(UUID tid) {
        TransactionContext context = activeTransactions.get(tid);
        if (context == null) {
            return;
        }

        LOGGER.info("Rolling back transaction: " + tid);
        for (Map.Entry<ResourceManager, String> entry : context.getResourceManagers().entrySet()) {
            ResourceManager rm = entry.getKey();
            try {
                rm.rollback(tid);
            } catch (Exception e) {
                LOGGER.log(Level.SEVERE, "Error during rollback for transaction " + tid, e);
            }
        }

        cleanupTransaction(tid);
    }

    private boolean preparePhase(UUID tid, TransactionContext context) {
        LOGGER.info("Starting prepare phase for transaction: " + tid);
        List<Future<Boolean>> prepareFutures = new ArrayList<>();

        for (Map.Entry<ResourceManager, String> entry : context.getResourceManagers().entrySet()) {
            ResourceManager rm = entry.getKey();
            String operationDetails = entry.getValue();

            if (operationDetails.startsWith("READ_ONLY:")) {
                context.markReadOnly(rm);
                continue;
            }

            Future<Boolean> prepareFuture = executorService.submit(() -> {
                try {
                    if (isDeadlocked(tid, rm)) {
                        return false;
                    }
                    return rm.prepare(tid, operationDetails);
                } catch (Exception e) {
                    LOGGER.log(Level.SEVERE, "Error during prepare phase", e);
                    return false;
                }
            });
            prepareFutures.add(prepareFuture);
        }

        try {
            for (Future<Boolean> future : prepareFutures) {
                if (!future.get(DEFAULT_TIMEOUT_MS, TimeUnit.MILLISECONDS)) {
                    return false;
                }
            }
            return true;
        } catch (Exception e) {
            LOGGER.log(Level.SEVERE, "Prepare phase failed for transaction " + tid, e);
            return false;
        }
    }

    private boolean commitPhase(UUID tid, TransactionContext context) {
        LOGGER.info("Starting commit phase for transaction: " + tid);
        boolean success = true;

        for (Map.Entry<ResourceManager, String> entry : context.getResourceManagers().entrySet()) {
            ResourceManager rm = entry.getKey();
            if (context.isReadOnly(rm)) {
                continue;
            }

            for (int retry = 0; retry < MAX_RETRIES; retry++) {
                try {
                    rm.commit(tid);
                    break;
                } catch (Exception e) {
                    LOGGER.log(Level.WARNING, "Commit retry " + (retry + 1) + " failed for transaction " + tid, e);
                    if (retry == MAX_RETRIES - 1) {
                        success = false;
                    }
                    try {
                        Thread.sleep(100 * (retry + 1));
                    } catch (InterruptedException ie) {
                        Thread.currentThread().interrupt();
                        return false;
                    }
                }
            }
        }

        return success;
    }

    private boolean isDeadlocked(UUID tid, ResourceManager rm) {
        Set<UUID> existingLocks = resourceLocks.computeIfAbsent(rm, k -> ConcurrentHashMap.newKeySet());
        if (!existingLocks.add(tid)) {
            return true;
        }
        return false;
    }

    private void cleanupTransaction(UUID tid) {
        TransactionContext context = activeTransactions.remove(tid);
        if (context != null) {
            for (ResourceManager rm : context.getResourceManagers().keySet()) {
                Set<UUID> locks = resourceLocks.get(rm);
                if (locks != null) {
                    locks.remove(tid);
                }
            }
        }
        LOGGER.info("Cleaned up transaction: " + tid);
    }
}