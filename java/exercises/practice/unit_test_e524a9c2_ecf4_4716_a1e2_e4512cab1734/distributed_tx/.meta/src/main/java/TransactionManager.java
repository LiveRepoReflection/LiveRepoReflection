import java.util.List;
import java.util.UUID;
import java.util.ArrayList;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.concurrent.ExecutionException;

public class TransactionManager {
    // Map to store active transactions and their enlisted services.
    private final ConcurrentMap<String, List<Service>> transactions = new ConcurrentHashMap<>();

    // Timeout in milliseconds for the prepare phase.
    private final long prepareTimeoutMillis = 5000;

    // ExecutorService to handle asynchronous service invocations.
    private final ExecutorService executor = Executors.newCachedThreadPool();

    /**
     * Starts a new transaction.
     *
     * @return A unique transaction identifier.
     */
    public String beginTransaction() {
        String transactionId = UUID.randomUUID().toString();
        transactions.put(transactionId, new CopyOnWriteArrayList<>());
        return transactionId;
    }

    /**
     * Enlists a service into the specified transaction.
     *
     * @param transactionId the unique identifier of the transaction.
     * @param service the service to enlist.
     * @throws IllegalArgumentException if the transaction does not exist.
     */
    public void enlistService(String transactionId, Service service) {
        List<Service> services = transactions.get(transactionId);
        if (services == null) {
            throw new IllegalArgumentException("Transaction not found: " + transactionId);
        }
        services.add(service);
    }

    /**
     * Attempts to commit the transaction using the two-phase commit protocol.
     *
     * Phase 1: Prepare phase – calls prepare() on all enlisted services asynchronously.
     * If all services return true within the timeout, proceed to commit.
     * If any service fails to prepare or the timeout is exceeded, rollback the transaction.
     *
     * Phase 2: If prepared successfully, calls commit() on all enlisted services asynchronously.
     *
     * @param transactionId the unique identifier of the transaction.
     * @return true if the transaction is successfully committed; false if rolled back.
     * @throws IllegalArgumentException if the transaction does not exist.
     */
    public boolean commitTransaction(String transactionId) {
        List<Service> services = transactions.get(transactionId);
        if (services == null) {
            throw new IllegalArgumentException("Transaction not found: " + transactionId);
        }

        List<Future<Boolean>> prepareFutures = new ArrayList<>();
        // Phase 1: Prepare phase
        for (Service service : services) {
            Future<Boolean> future = executor.submit(() -> {
                try {
                    return service.prepare(transactionId);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    return false;
                }
            });
            prepareFutures.add(future);
        }

        boolean allPrepared = true;
        for (Future<Boolean> future : prepareFutures) {
            try {
                Boolean result = future.get(prepareTimeoutMillis, TimeUnit.MILLISECONDS);
                if (!result) {
                    allPrepared = false;
                }
            } catch (TimeoutException | InterruptedException | ExecutionException e) {
                allPrepared = false;
            }
        }

        // Phase 2: Commit or Rollback based on prepare phase result.
        if (allPrepared) {
            // If all services prepared successfully, commit the transaction.
            for (Service service : services) {
                executor.submit(() -> service.commit(transactionId));
            }
        } else {
            // If any service fails to prepare or timeout occurs, rollback the transaction.
            for (Service service : services) {
                executor.submit(() -> service.rollback(transactionId));
            }
        }

        // Clean up the transaction.
        transactions.remove(transactionId);
        return allPrepared;
    }

    /**
     * Explicitly rollbacks a transaction by instructing all enlisted services to rollback.
     * This method can be safely called multiple times (idempotent).
     *
     * @param transactionId the unique identifier of the transaction.
     */
    public void rollbackTransaction(String transactionId) {
        List<Service> services = transactions.get(transactionId);
        if (services != null) {
            for (Service service : services) {
                executor.submit(() -> service.rollback(transactionId));
            }
            transactions.remove(transactionId);
        }
    }

    /**
     * Shuts down the internal executor service.
     * This method should be called to release resources when the TransactionManager is no longer needed.
     */
    public void shutdown() {
        executor.shutdownNow();
    }
}