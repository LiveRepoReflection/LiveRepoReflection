import java.util.Map;
import java.util.HashMap;
import java.util.concurrent.*;

public class DistributedTxCoordinator {
    private final Map<String, Service> serviceRegistry;
    private final ExecutorService executor;

    public DistributedTxCoordinator(Map<String, Service> serviceRegistry) {
        this.serviceRegistry = serviceRegistry;
        this.executor = Executors.newCachedThreadPool();
    }

    public TransactionStatus processTransaction(Transaction tx) {
        // Phase 1: Prepare Phase - Send prepare requests concurrently.
        Map<String, Future<Boolean>> futures = new HashMap<>();
        for (String serviceId : tx.getServiceIds()) {
            Service service = serviceRegistry.get(serviceId);
            Future<Boolean> future = executor.submit(() -> {
                try {
                    return service.prepare(tx.getId(), tx.getOperation());
                } catch (Exception e) {
                    return false;
                }
            });
            futures.put(serviceId, future);
        }

        boolean allPrepared = true;
        for (Future<Boolean> future : futures.values()) {
            try {
                // Timeout is set to 5 seconds per service.
                if (!future.get(5, TimeUnit.SECONDS)) {
                    allPrepared = false;
                }
            } catch (Exception e) {
                allPrepared = false;
            }
        }

        // Phase 2: Commit or Rollback Phase - Execute based on prepare phase outcome.
        for (String serviceId : tx.getServiceIds()) {
            Service service = serviceRegistry.get(serviceId);
            try {
                if (allPrepared) {
                    service.commit(tx.getId());
                } else {
                    service.rollback(tx.getId());
                }
            } catch (Exception e) {
                // Exceptions during commit/rollback are handled gracefully.
            }
        }

        return allPrepared ? TransactionStatus.COMMITTED : TransactionStatus.ROLLEDBACK;
    }

    public void shutdown() {
        executor.shutdownNow();
    }
}