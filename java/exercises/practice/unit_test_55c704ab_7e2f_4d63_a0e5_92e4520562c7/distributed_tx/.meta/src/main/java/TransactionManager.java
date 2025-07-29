import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import java.util.concurrent.atomic.AtomicLong;

public class TransactionManager {

    private final ConcurrentMap<Long, Set<String>> transactionServices;
    private final AtomicLong transactionIdGenerator;

    public TransactionManager() {
        transactionServices = new ConcurrentHashMap<>();
        transactionIdGenerator = new AtomicLong(1);
    }

    /**
     * Starts a new transaction and returns a unique transactionId.
     */
    public long begin() {
        long txId = transactionIdGenerator.getAndIncrement();
        transactionServices.put(txId, ConcurrentHashMap.newKeySet());
        return txId;
    }

    /**
     * Enlists the microservice endpoint in a given transaction.
     *
     * @param transactionId The transaction identifier.
     * @param serviceEndpoint The service endpoint URL.
     */
    public void enlist(long transactionId, String serviceEndpoint) {
        Set<String> services = transactionServices.get(transactionId);
        if (services == null) {
            throw new IllegalArgumentException("Transaction " + transactionId + " does not exist.");
        }
        services.add(serviceEndpoint);
    }

    /**
     * Commits the transaction using a Two-Phase Commit (2PC) protocol.
     *
     * Phase 1: Prepare phase.
     * Phase 2: Commit phase.
     *
     * @param transactionId The transaction identifier.
     * @return true if commit was successful across all enlisted services, false otherwise.
     */
    public boolean commit(long transactionId) {
        Set<String> services = transactionServices.get(transactionId);
        if (services == null) {
            throw new IllegalArgumentException("Transaction " + transactionId + " does not exist.");
        }

        // Phase 1: Prepare phase
        boolean allPrepared = true;
        for (String service : services) {
            try {
                boolean prepared = callServiceWithRetry(service, "prepare", transactionId);
                if (!prepared) {
                    allPrepared = false;
                    break;
                }
            } catch (Exception e) {
                allPrepared = false;
                break;
            }
        }

        if (!allPrepared) {
            // If any service fails during prepare, rollback the transaction.
            rollback(transactionId);
            return false;
        }

        // Phase 2: Commit phase
        boolean allCommitted = true;
        for (String service : services) {
            try {
                boolean committed = callServiceWithRetry(service, "commit", transactionId);
                if (!committed) {
                    allCommitted = false;
                    break;
                }
            } catch (Exception e) {
                allCommitted = false;
                break;
            }
        }

        if (!allCommitted) {
            // If commit fails on any service, attempt rollback
            rollback(transactionId);
            return false;
        }

        return true;
    }

    /**
     * Rolls back the transaction across all enlisted services.
     *
     * @param transactionId The transaction identifier.
     * @return true if rollback was successful across all enlisted services, false otherwise.
     */
    public boolean rollback(long transactionId) {
        Set<String> services = transactionServices.get(transactionId);
        if (services == null) {
            throw new IllegalArgumentException("Transaction " + transactionId + " does not exist.");
        }

        boolean allRolledBack = true;
        for (String service : services) {
            try {
                boolean rolledBack = callServiceWithRetry(service, "rollback", transactionId);
                if (!rolledBack) {
                    allRolledBack = false;
                }
            } catch (Exception e) {
                allRolledBack = false;
            }
        }
        return allRolledBack;
    }

    /**
     * Helper method that implements retry logic for calling a microservice API.
     *
     * @param serviceEndpoint The service endpoint URL.
     * @param operation The operation being called ("prepare", "commit", "rollback").
     * @param transactionId The transaction identifier.
     * @return true if the call was successful, false otherwise.
     * @throws Exception if the call fails after maximum retries.
     */
    private boolean callServiceWithRetry(String serviceEndpoint, String operation, long transactionId) throws Exception {
        int maxRetries = 3;
        int attempt = 0;
        long backoff = 100L; // initial backoff in milliseconds

        while (attempt < maxRetries) {
            try {
                boolean result = callService(serviceEndpoint, operation, transactionId);
                return result;
            } catch (Exception e) {
                attempt++;
                if (attempt >= maxRetries) {
                    throw e;
                }
                Thread.sleep(backoff);
                backoff *= 2;
            }
        }
        return false;
    }

    /**
     * Simulates calling a microservice API for a given operation.
     * In a real-world scenario, this would make an HTTP call to the microservice endpoint.
     * This method is designed to be overridden (e.g., in tests) to simulate various behaviors.
     *
     * @param serviceEndpoint The service endpoint URL.
     * @param operation The operation to perform ("prepare", "commit", "rollback").
     * @param transactionId The transaction identifier.
     * @return true if the operation succeeds, false otherwise.
     * @throws Exception if the operation fails.
     */
    protected boolean callService(String serviceEndpoint, String operation, long transactionId) throws Exception {
        // Default implementation: always succeeds.
        // In a production environment, insert HTTP client logic here.
        return true;
    }
}