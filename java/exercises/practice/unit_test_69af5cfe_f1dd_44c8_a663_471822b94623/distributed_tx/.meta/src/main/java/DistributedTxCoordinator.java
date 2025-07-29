import java.util.*;
import java.util.concurrent.*;

public class DistributedTxCoordinator {

    private final Map<String, ServiceParticipant> services = new ConcurrentHashMap<>();
    private final ExecutorService executor = Executors.newCachedThreadPool();
    private final long TIMEOUT_MILLIS = 1000;

    /**
     * Registers a service participant with a unique service id.
     *
     * @param id the unique identifier for the service
     * @param service the service participant implementing the transaction protocol
     */
    public void registerService(String id, ServiceParticipant service) {
        services.put(id, service);
    }

    /**
     * Executes a distributed transaction using the Two-Phase Commit protocol.
     * In the first phase, a prepare request is sent concurrently to all registered services.
     * If all services respond with "OK" within the timeout, the transaction is committed.
     * Otherwise, a rollback is triggered on all services.
     *
     * @return true if the transaction is successfully committed, or false if it is rolled back.
     */
    public boolean executeTransaction() {
        List<Future<String>> futures = new ArrayList<>();
        // Phase 1: Prepare requests
        for (ServiceParticipant service : services.values()) {
            Future<String> future = executor.submit(() -> {
                try {
                    return service.prepare();
                } catch (Exception e) {
                    return "ABORT";
                }
            });
            futures.add(future);
        }

        boolean allOk = true;
        for (Future<String> future : futures) {
            try {
                String result = future.get(TIMEOUT_MILLIS, TimeUnit.MILLISECONDS);
                if (!"OK".equals(result)) {
                    allOk = false;
                }
            } catch (Exception e) {
                allOk = false;
            }
        }

        // Phase 2: Commit or Rollback based on the prepare phase results
        if (allOk) {
            for (ServiceParticipant service : services.values()) {
                service.commit();
            }
        } else {
            for (ServiceParticipant service : services.values()) {
                service.rollback();
            }
        }
        return allOk;
    }

    /**
     * Shuts down the internal executor service.
     */
    public void shutdown() {
        executor.shutdownNow();
    }

    /**
     * Interface representing a service participant in the distributed transaction.
     * Each service must implement the prepare, commit, and rollback operations.
     * Commit and rollback operations must be idempotent.
     */
    public interface ServiceParticipant {
        /**
         * Attempts to prepare for the transaction.
         *
         * @return "OK" if the service is prepared to commit, otherwise any other string (e.g., "ABORT") to indicate failure.
         * @throws Exception if an error occurs during preparation.
         */
        String prepare() throws Exception;

        /**
         * Commits the transaction. This operation must be idempotent.
         */
        void commit();

        /**
         * Rolls back the transaction. This operation must be idempotent.
         */
        void rollback();
    }
}