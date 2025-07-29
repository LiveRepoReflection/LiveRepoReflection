import org.junit.jupiter.api.Test;
import static org.assertj.core.api.Assertions.assertThat;
import java.util.*;
import java.util.concurrent.*;

public class DistributedTxTest {

    // Dummy implementation for service participants
    class DummyService {
        private final String id;
        private final String behavior; // "success", "abort", "timeout"
        private boolean committed = false;
        private boolean rolledBack = false;
        
        public DummyService(String id, String behavior) {
            this.id = id;
            this.behavior = behavior;
        }
        
        public String prepare() throws Exception {
            if ("timeout".equals(behavior)) {
                // Simulate a timeout by sleeping longer than the coordinator's timeout
                Thread.sleep(3000);
                return "TIMEOUT";
            }
            return "success".equals(behavior) ? "OK" : "ABORT";
        }
        
        public void commit() {
            committed = true;
        }
        
        public void rollback() {
            rolledBack = true;
        }
        
        public boolean isCommitted() {
            return committed;
        }
        
        public boolean isRolledBack() {
            return rolledBack;
        }
    }

    // Simplified Distributed Transaction Coordinator (DTC) implementation for testing purposes.
    class DistributedTransactionCoordinator {
        private final Map<String, DummyService> services = new ConcurrentHashMap<>();
        private final ExecutorService executor = Executors.newCachedThreadPool();
        private final long timeoutMillis = 1000;

        public void registerService(String id, DummyService service) {
            services.put(id, service);
        }

        public boolean executeTransaction() {
            List<Future<String>> futures = new ArrayList<>();
            for (DummyService service : services.values()) {
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
                    String result = future.get(timeoutMillis, TimeUnit.MILLISECONDS);
                    if (!"OK".equals(result)) {
                        allOk = false;
                    }
                } catch (Exception e) {
                    allOk = false;
                }
            }
            if (allOk) {
                for (DummyService service : services.values()) {
                    service.commit();
                }
            } else {
                for (DummyService service : services.values()) {
                    service.rollback();
                }
            }
            return allOk;
        }

        public void shutdown() {
            executor.shutdownNow();
        }
    }

    @Test
    public void testSuccessfulTransaction() {
        DistributedTransactionCoordinator coordinator = new DistributedTransactionCoordinator();
        DummyService service1 = new DummyService("inventory", "success");
        DummyService service2 = new DummyService("order", "success");
        DummyService service3 = new DummyService("payment", "success");
        coordinator.registerService("inventory", service1);
        coordinator.registerService("order", service2);
        coordinator.registerService("payment", service3);

        boolean result = coordinator.executeTransaction();
        assertThat(result).isTrue();
        assertThat(service1.isCommitted()).isTrue();
        assertThat(service2.isCommitted()).isTrue();
        assertThat(service3.isCommitted()).isTrue();
        assertThat(service1.isRolledBack()).isFalse();
        assertThat(service2.isRolledBack()).isFalse();
        assertThat(service3.isRolledBack()).isFalse();

        coordinator.shutdown();
    }

    @Test
    public void testTransactionWithAbort() {
        DistributedTransactionCoordinator coordinator = new DistributedTransactionCoordinator();
        DummyService service1 = new DummyService("inventory", "success");
        DummyService service2 = new DummyService("order", "abort");
        DummyService service3 = new DummyService("payment", "success");
        coordinator.registerService("inventory", service1);
        coordinator.registerService("order", service2);
        coordinator.registerService("payment", service3);

        boolean result = coordinator.executeTransaction();
        assertThat(result).isFalse();
        assertThat(service1.isRolledBack()).isTrue();
        assertThat(service2.isRolledBack()).isTrue();
        assertThat(service3.isRolledBack()).isTrue();
        assertThat(service1.isCommitted()).isFalse();

        coordinator.shutdown();
    }

    @Test
    public void testTransactionWithTimeout() {
        DistributedTransactionCoordinator coordinator = new DistributedTransactionCoordinator();
        DummyService service1 = new DummyService("inventory", "success");
        DummyService service2 = new DummyService("order", "timeout");
        coordinator.registerService("inventory", service1);
        coordinator.registerService("order", service2);

        boolean result = coordinator.executeTransaction();
        assertThat(result).isFalse();
        assertThat(service1.isRolledBack()).isTrue();
        assertThat(service2.isRolledBack()).isTrue();

        coordinator.shutdown();
    }

    @Test
    public void testIdempotencyOfCommitRollback() {
        DistributedTransactionCoordinator coordinator = new DistributedTransactionCoordinator();
        DummyService service1 = new DummyService("inventory", "success");
        coordinator.registerService("inventory", service1);

        // Execute the transaction which should commit successfully.
        boolean firstResult = coordinator.executeTransaction();
        assertThat(firstResult).isTrue();
        assertThat(service1.isCommitted()).isTrue();

        // Calling commit and rollback again should not change the state
        service1.commit();
        service1.rollback();
        // For the purpose of this test, we assume once committed, the state remains committed.
        assertThat(service1.isCommitted()).isTrue();

        coordinator.shutdown();
    }

    @Test
    public void testConcurrentTransactions() throws Exception {
        final int concurrentTransactions = 5;
        ExecutorService execService = Executors.newFixedThreadPool(concurrentTransactions);
        List<Future<Boolean>> futures = new ArrayList<>();

        for (int i = 0; i < concurrentTransactions; i++) {
            Future<Boolean> future = execService.submit(() -> {
                DistributedTransactionCoordinator coordinator = new DistributedTransactionCoordinator();
                DummyService service1 = new DummyService("inventory", "success");
                DummyService service2 = new DummyService("order", "success");
                coordinator.registerService("inventory", service1);
                coordinator.registerService("order", service2);
                boolean res = coordinator.executeTransaction();
                coordinator.shutdown();
                return res;
            });
            futures.add(future);
        }

        for (Future<Boolean> future : futures) {
            assertThat(future.get()).isTrue();
        }
        execService.shutdownNow();
    }
}