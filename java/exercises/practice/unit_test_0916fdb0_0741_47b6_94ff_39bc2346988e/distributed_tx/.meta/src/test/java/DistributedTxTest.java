package distributed_tx;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.*;
import static org.junit.jupiter.api.Assertions.*;

public class DistributedTxTest {

    private DistributedTransactionCoordinator coordinator;

    @BeforeEach
    public void setup() {
        coordinator = new DistributedTransactionCoordinator(200);
    }

    private static class DummyService implements Service {
        private final String id;
        private final boolean shouldPrepare;
        private final long prepareDelayMillis;

        public DummyService(String id, boolean shouldPrepare, long prepareDelayMillis) {
            this.id = id;
            this.shouldPrepare = shouldPrepare;
            this.prepareDelayMillis = prepareDelayMillis;
        }

        @Override
        public boolean prepare(UUID transactionId) {
            try {
                Thread.sleep(prepareDelayMillis);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return false;
            }
            return shouldPrepare;
        }

        @Override
        public void commit(UUID transactionId) {
            // Simulated commit operation.
        }

        @Override
        public void rollback(UUID transactionId) {
            // Simulated rollback operation.
        }

        @Override
        public String toString() {
            return id;
        }
    }

    @Test
    public void testAllServicesCommit() {
        List<Service> services = new ArrayList<>();
        services.add(new DummyService("service1", true, 50));
        services.add(new DummyService("service2", true, 50));
        services.add(new DummyService("service3", true, 50));

        UUID transactionId = UUID.randomUUID();
        boolean result = coordinator.executeTransaction(transactionId, services);
        assertTrue(result, "Transaction should commit when all services prepare successfully.");

        LogEntry logEntry = coordinator.getLogEntry(transactionId);
        assertNotNull(logEntry, "Log should contain the transaction entry.");
        assertEquals("COMMIT", logEntry.getDecision(), "Transaction log decision should be COMMIT.");
        assertEquals(3, logEntry.getServiceIds().size(), "Log should contain all participating services.");
    }

    @Test
    public void testServiceAbort() {
        List<Service> services = new ArrayList<>();
        services.add(new DummyService("service1", true, 50));
        services.add(new DummyService("service2", false, 50));
        services.add(new DummyService("service3", true, 50));

        UUID transactionId = UUID.randomUUID();
        boolean result = coordinator.executeTransaction(transactionId, services);
        assertFalse(result, "Transaction should rollback when any service fails to prepare.");

        LogEntry logEntry = coordinator.getLogEntry(transactionId);
        assertNotNull(logEntry, "Log should contain the transaction entry.");
        assertEquals("ROLLBACK", logEntry.getDecision(), "Transaction log decision should be ROLLBACK.");
        assertEquals(3, logEntry.getServiceIds().size(), "Log should contain all participating services.");
    }

    @Test
    public void testServiceTimeout() {
        List<Service> services = new ArrayList<>();
        services.add(new DummyService("service1", true, 50));
        services.add(new DummyService("service2", true, 300));
        services.add(new DummyService("service3", true, 50));

        UUID transactionId = UUID.randomUUID();
        boolean result = coordinator.executeTransaction(transactionId, services);
        assertFalse(result, "Transaction should rollback when any service exceeds timeout during prepare.");

        LogEntry logEntry = coordinator.getLogEntry(transactionId);
        assertNotNull(logEntry, "Log should contain the transaction entry.");
        assertEquals("ROLLBACK", logEntry.getDecision(), "Transaction log decision should be ROLLBACK.");
        assertEquals(3, logEntry.getServiceIds().size(), "Log should contain all participating services.");
    }

    @Test
    public void testConcurrentTransactions() throws InterruptedException, ExecutionException {
        int numberOfTransactions = 10;
        ExecutorService executor = Executors.newFixedThreadPool(5);
        List<Callable<Boolean>> tasks = new ArrayList<>();
        List<UUID> transactionIds = new ArrayList<>();

        for (int i = 0; i < numberOfTransactions; i++) {
            final UUID transactionId = UUID.randomUUID();
            transactionIds.add(transactionId);
            tasks.add(() -> {
                List<Service> services = new ArrayList<>();
                if (transactionId.getLeastSignificantBits() % 2 == 0) {
                    services.add(new DummyService("serviceA", true, 50));
                    services.add(new DummyService("serviceB", true, 50));
                    services.add(new DummyService("serviceC", true, 50));
                } else {
                    services.add(new DummyService("serviceA", true, 50));
                    services.add(new DummyService("serviceB", false, 50));
                    services.add(new DummyService("serviceC", true, 50));
                }
                return coordinator.executeTransaction(transactionId, services);
            });
        }

        List<Future<Boolean>> results = executor.invokeAll(tasks);
        executor.shutdown();
        executor.awaitTermination(5, TimeUnit.SECONDS);

        for (int i = 0; i < numberOfTransactions; i++) {
            UUID txnId = transactionIds.get(i);
            boolean outcome = results.get(i).get();
            LogEntry entry = coordinator.getLogEntry(txnId);
            assertNotNull(entry, "Log should contain the transaction entry.");
            if (txnId.getLeastSignificantBits() % 2 == 0) {
                assertTrue(outcome, "Transaction should commit.");
                assertEquals("COMMIT", entry.getDecision(), "Log decision should be COMMIT.");
            } else {
                assertFalse(outcome, "Transaction should rollback.");
                assertEquals("ROLLBACK", entry.getDecision(), "Log decision should be ROLLBACK.");
            }
            assertEquals(3, entry.getServiceIds().size(), "Log should record all 3 participating services.");
        }
    }
}