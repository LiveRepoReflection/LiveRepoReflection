package distributed_tx;

import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;

public class DistributedTransactionCoordinator {

    private final Map<Integer, Service> services;
    private final ExecutorService executor;

    public DistributedTransactionCoordinator(Map<Integer, Service> services) {
        this.services = services;
        this.executor = Executors.newCachedThreadPool();
    }

    public boolean initiateTransaction(List<Integer> serviceIds, String data) {
        String transactionId = UUID.randomUUID().toString();
        List<Future<Boolean>> futures = new CopyOnWriteArrayList<>();

        // Phase 1: Prepare
        for (Integer id : serviceIds) {
            Service service = services.get(id);
            if (service == null || !service.isAlive()) {
                rollbackServices(serviceIds, transactionId);
                return false;
            }
            Future<Boolean> future = executor.submit(() -> service.prepare(transactionId, data));
            futures.add(future);
        }

        boolean allPrepared = true;
        for (Future<Boolean> future : futures) {
            try {
                // Wait up to 2 seconds for each prepare call.
                boolean res = future.get(2, TimeUnit.SECONDS);
                if (!res) {
                    allPrepared = false;
                }
            } catch (Exception e) {
                allPrepared = false;
            }
        }

        // Phase 2: Commit or Rollback
        if (allPrepared) {
            for (Integer id : serviceIds) {
                Service service = services.get(id);
                try {
                    service.commit(transactionId);
                } catch (Exception e) {
                    rollbackServices(serviceIds, transactionId);
                    return false;
                }
            }
            return true;
        } else {
            rollbackServices(serviceIds, transactionId);
            return false;
        }
    }

    private void rollbackServices(List<Integer> serviceIds, String transactionId) {
        for (Integer id : serviceIds) {
            Service service = services.get(id);
            if (service != null && service.isAlive()) {
                service.rollback(transactionId);
            }
        }
    }

    public void shutdownCoordinator() {
        executor.shutdown();
    }

    // Interface representing a microservice in the distributed transaction system.
    public interface Service {
        boolean isAlive();
        boolean prepare(String transactionId, String data);
        void commit(String transactionId);
        void rollback(String transactionId);
    }
}