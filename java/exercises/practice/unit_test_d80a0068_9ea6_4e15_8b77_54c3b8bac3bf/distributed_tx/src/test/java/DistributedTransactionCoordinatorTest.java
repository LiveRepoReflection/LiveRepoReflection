package distributed_tx;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.util.*;
import java.util.concurrent.*;

public class DistributedTransactionCoordinatorTest {

    // A fake service to simulate behavior of a microservice in the distributed transaction.
    static class FakeService {
        private final int id;
        private boolean shouldPrepareSucceed;
        private boolean alive;
        private boolean prepared;

        public FakeService(int id, boolean shouldPrepareSucceed, boolean alive) {
            this.id = id;
            this.shouldPrepareSucceed = shouldPrepareSucceed;
            this.alive = alive;
            this.prepared = false;
        }

        public boolean isAlive() {
            return alive;
        }

        public boolean prepare(String transactionId, String data) {
            if (!alive) {
                return false;
            }
            prepared = shouldPrepareSucceed;
            return shouldPrepareSucceed;
        }

        public void commit(String transactionId) {
            if (!prepared) {
                throw new IllegalStateException("Commit called without successful prepare");
            }
            // Simulate a commit operation (no state change needed for testing)
        }

        public void rollback(String transactionId) {
            prepared = false;
        }
    }

    // A simplified DistributedTransactionCoordinator that uses the FakeService instances.
    static class DistributedTransactionCoordinator {
        private final Map<Integer, FakeService> services;
        private final ExecutorService executor = Executors.newCachedThreadPool();

        public DistributedTransactionCoordinator(Map<Integer, FakeService> services) {
            this.services = services;
        }

        public boolean initiateTransaction(List<Integer> serviceIds, String data) {
            String transactionId = UUID.randomUUID().toString();
            List<Future<Boolean>> futures = new ArrayList<>();

            // Phase 1: Prepare
            for (Integer id : serviceIds) {
                FakeService service = services.get(id);
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
                    FakeService service = services.get(id);
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
                FakeService service = services.get(id);
                if (service != null && service.isAlive()) {
                    service.rollback(transactionId);
                }
            }
        }
    }

    @Test
    public void testSuccessfulTransaction() {
        Map<Integer, FakeService> services = new HashMap<>();
        services.put(0, new FakeService(0, true, true));
        services.put(1, new FakeService(1, true, true));
        services.put(2, new FakeService(2, true, true));

        DistributedTransactionCoordinator coordinator = new DistributedTransactionCoordinator(services);
        List<Integer> serviceIds = Arrays.asList(0, 1, 2);
        boolean result = coordinator.initiateTransaction(serviceIds, "Update Data");
        assertTrue(result, "Transaction should commit when all services prepare successfully.");
    }

    @Test
    public void testPrepareFailureCausesRollback() {
        Map<Integer, FakeService> services = new HashMap<>();
        services.put(0, new FakeService(0, true, true));
        // This service will fail during prepare.
        services.put(1, new FakeService(1, false, true));
        services.put(2, new FakeService(2, true, true));

        DistributedTransactionCoordinator coordinator = new DistributedTransactionCoordinator(services);
        List<Integer> serviceIds = Arrays.asList(0, 1, 2);
        boolean result = coordinator.initiateTransaction(serviceIds, "Update Data");
        assertFalse(result, "Transaction should rollback when one service fails its prepare.");
    }

    @Test
    public void testServiceNotAliveCausesRollback() {
        Map<Integer, FakeService> services = new HashMap<>();
        services.put(0, new FakeService(0, true, true));
        // Service 1 is not alive.
        services.put(1, new FakeService(1, true, false));
        services.put(2, new FakeService(2, true, true));

        DistributedTransactionCoordinator coordinator = new DistributedTransactionCoordinator(services);
        List<Integer> serviceIds = Arrays.asList(0, 1, 2);
        boolean result = coordinator.initiateTransaction(serviceIds, "Update Data");
        assertFalse(result, "Transaction should rollback if a service is not alive.");
    }

    @Test
    public void testCommitFailureDuringPhaseTwoCausesRollback() {
        Map<Integer, FakeService> services = new HashMap<>();
        // Simulate failure during commit by overriding commit() in a subclass.
        FakeService failingService = new FakeService(0, true, true) {
            @Override
            public void commit(String transactionId) {
                throw new RuntimeException("Commit failure simulated.");
            }
        };
        services.put(0, failingService);
        services.put(1, new FakeService(1, true, true));

        DistributedTransactionCoordinator coordinator = new DistributedTransactionCoordinator(services);
        List<Integer> serviceIds = Arrays.asList(0, 1);
        boolean result = coordinator.initiateTransaction(serviceIds, "Update Data");
        assertFalse(result, "Transaction should rollback if commit fails in phase 2.");
    }

    @Test
    public void testConcurrentTransactions() throws InterruptedException, ExecutionException {
        Map<Integer, FakeService> services = new ConcurrentHashMap<>();
        // Create 5 services that always succeed.
        for (int i = 0; i < 5; i++) {
            services.put(i, new FakeService(i, true, true));
        }
        DistributedTransactionCoordinator coordinator = new DistributedTransactionCoordinator(services);
        ExecutorService executorService = Executors.newFixedThreadPool(10);
        List<Callable<Boolean>> tasks = new ArrayList<>();

        // Run 20 concurrent transactions.
        for (int i = 0; i < 20; i++) {
            tasks.add(() -> {
                List<Integer> serviceIds = Arrays.asList(0, 1, 2, 3, 4);
                return coordinator.initiateTransaction(serviceIds, "Concurrent Update");
            });
        }

        List<Future<Boolean>> futures = executorService.invokeAll(tasks);
        for (Future<Boolean> future : futures) {
            assertTrue(future.get(), "All concurrent transactions should commit successfully.");
        }
        executorService.shutdown();
    }
}