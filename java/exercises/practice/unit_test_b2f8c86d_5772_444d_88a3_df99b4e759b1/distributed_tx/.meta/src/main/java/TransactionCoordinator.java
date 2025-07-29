import java.util.List;
import java.util.ArrayList;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;

public class TransactionCoordinator {

    private final List<TransactionalService> services = new CopyOnWriteArrayList<>();
    private final ConcurrentHashMap<String, TransactionStatus> transactions = new ConcurrentHashMap<>();
    private final long prepareTimeoutMillis = 5000;

    private enum TransactionStatus { PENDING, PREPARED, COMMITTED, ROLLED_BACK }

    /**
     * Registers a service to participate in transactions.
     */
    public void registerService(TransactionalService service) {
        services.add(service);
    }

    /**
     * Starts a new transaction and returns its unique transactionId.
     */
    public String startTransaction() {
        String transactionId = UUID.randomUUID().toString();
        transactions.put(transactionId, TransactionStatus.PENDING);
        return transactionId;
    }

    /**
     * Executes the two-phase commit protocol in one call.
     * Phase one: prepare all services.
     * Phase two: if all prepared successfully, commit; otherwise rollback.
     */
    public void executeTransaction(String transactionId) {
        executePreparePhase(transactionId);
        if (transactions.get(transactionId) == TransactionStatus.PREPARED) {
            commitServices();
            transactions.put(transactionId, TransactionStatus.COMMITTED);
        }
    }

    /**
     * Explicitly executes just the prepare phase.
     * If any service fails to prepare (including timeout or exception), 
     * the transaction is automatically rolled back.
     */
    public void executePreparePhase(String transactionId) {
        if (!transactions.containsKey(transactionId)) {
            return;
        }

        boolean allPrepared = true;
        ExecutorService executor = Executors.newFixedThreadPool(services.size());
        List<Future<Boolean>> futures = new ArrayList<>();

        for (TransactionalService service : services) {
            Future<Boolean> future = executor.submit(() -> {
                try {
                    return service.prepare();
                } catch (Exception e) {
                    // Log error in real-world scenario
                    return false;
                }
            });
            futures.add(future);
        }

        for (Future<Boolean> future : futures) {
            try {
                boolean result = future.get(prepareTimeoutMillis, TimeUnit.MILLISECONDS);
                if (!result) {
                    allPrepared = false;
                }
            } catch (Exception e) {
                allPrepared = false;
            }
        }
        executor.shutdown();

        if (allPrepared) {
            transactions.put(transactionId, TransactionStatus.PREPARED);
        } else {
            transactions.put(transactionId, TransactionStatus.ROLLED_BACK);
            rollbackServices();
        }
    }

    /**
     * Explicitly commits a transaction that has been prepared.
     */
    public void commitTransaction(String transactionId) {
        TransactionStatus status = transactions.get(transactionId);
        if (status == null) {
            return;
        }
        if (status == TransactionStatus.PREPARED) {
            commitServices();
            transactions.put(transactionId, TransactionStatus.COMMITTED);
        }
    }

    /**
     * Explicitly rolls back a transaction.
     */
    public void rollbackTransaction(String transactionId) {
        TransactionStatus status = transactions.get(transactionId);
        if (status == null) {
            return;
        }
        if (status == TransactionStatus.PENDING || status == TransactionStatus.PREPARED) {
            rollbackServices();
            transactions.put(transactionId, TransactionStatus.ROLLED_BACK);
        }
    }

    /**
     * Helper method to iterate over all registered services and commit them.
     * Each call to commit() is wrapped in try-catch to ensure idempotency in the 
     * presence of exceptions.
     */
    private void commitServices() {
        for (TransactionalService service : services) {
            try {
                service.commit();
            } catch (Exception e) {
                // Log error in real-world scenario
            }
        }
    }

    /**
     * Helper method to iterate over all registered services and rollback them.
     * Each call to rollback() is wrapped in try-catch to ensure idempotency
     * in the presence of exceptions.
     */
    private void rollbackServices() {
        for (TransactionalService service : services) {
            try {
                service.rollback();
            } catch (Exception e) {
                // Log error in real-world scenario
            }
        }
    }
    
    /*
     * Note: In a real-world distributed system, the transaction state would be persisted
     * to a durable storage to support recovery after failures. This implementation
     * uses in-memory storage for simplicity.
     */
}