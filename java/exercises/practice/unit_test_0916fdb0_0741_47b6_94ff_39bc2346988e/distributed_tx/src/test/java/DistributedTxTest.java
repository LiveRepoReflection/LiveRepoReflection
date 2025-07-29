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
        // Assume the coordinator can be instantiated with a configurable timeout (in milliseconds)
        coordinator = new DistributedTransactionCoordinator(200); // 200ms timeout for prepare calls
    }

    // Dummy Service implementation to simulate a participating service in the transaction
    private static class DummyService implements Service {
        private final String id;
        private final boolean shouldPrepare;
        private final long prepareDelayMillis; // delay in milliseconds on prepare call

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
            // In a real implementation, commit logic would go here.
        }

        @Override
        public void rollback(UUID transactionId) {
            // In a real implementation, rollback logic would go here.
        }

        @Override
        public String toString() {
            return id;
        }
    }

    @Test
    public void testAllServicesCommit() {
        // All services prepare successfully without delay.
        List<Service> services = new ArrayList<>();
        services.add(new DummyService("service1", true, 50));
        services.add(new DummyService("service2", true, 50));
        services.add(new DummyService("service3", true, 50));

        UUID transactionId = UUID.randomUUID();
        boolean result = coordinator.executeTransaction(transactionId, services);
        assertTrue(result, "Transaction should commit when all services prepare successfully.");

        // Verify that the log contains this transaction and the commit decision.
        LogEntry logEntry = coordinator.getLogEntry(transactionId);
        assertNotNull(logEntry, "Log should contain the transaction entry.");
        assertEquals("COMMIT", logEntry.getDecision(), "Transaction log decision should be COMMIT.");
        assertEquals(3, logEntry.getServiceIds().size(), "Log should contain all participating services.");
    }

    @Test
    public void testServiceAbort() {
        // One service fails to prepare, causing the transaction to rollback.
        List<Service> services = new ArrayList<>();
        services.add(new DummyService("service1", true, 50));
        services.add(new DummyService("service2", false, 50)); // this service will abort
        services.add(new DummyService("service3", true, 50));

        UUID transactionId = UUID.randomUUID();
        boolean result = coordinator.executeTransaction(transactionId, services);
        assertFalse(result, "Transaction should rollback when any service fails to prepare.");

        // Verify that the log contains this transaction and the rollback decision.
        LogEntry logEntry = coordinator.getLogEntry(transactionId);
        assertNotNull(logEntry, "Log should contain the transaction entry.");
        assertEquals("ROLLBACK", logEntry.getDecision(), "Transaction log decision should be ROLLBACK.");
        assertEquals(3, logEntry.getServiceIds().size(), "Log should contain all participating services.");
    }

    @Test
    public void testServiceTimeout() {
        // One service simulates a delay longer than the coordinator's timeout
        List<Service> services = new ArrayList<>();
        services.add(new DummyService("service1", true, 50));
        services.add(new DummyService("service2", true, 300)); // exceeds the 200ms timeout
        services.add(new DummyService("service3", true, 50));

        UUID transactionId = UUID.randomUUID();
        boolean result = coordinator.executeTransaction(transactionId, services);
        assertFalse(result, "Transaction should rollback when any service exceeds timeout during prepare.");

        // Verify that the log contains this transaction and the rollback decision.
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

        // Create 10 transactions with varied service responses.
        for (int i = 0; i < numberOfTransactions; i++) {
            final UUID transactionId = UUID.randomUUID();
            transactionIds.add(transactionId);
            tasks.add(() -> {
                List<Service> services = new ArrayList<>();
                // Alternate between all success and one failure.
                if (transactionId.getLeastSignificantBits() % 2 == 0) {
                    services.add(new DummyService("serviceA", true, 50));
                    services.add(new DummyService("serviceB", true, 50));
                    services.add(new DummyService("serviceC", true, 50));
                } else {
                    services.add(new DummyService("serviceA", true, 50));
                    services.add(new DummyService("serviceB", false, 50)); // failure leads to rollback
                    services.add(new DummyService("serviceC", true, 50));
                }
                return coordinator.executeTransaction(transactionId, services);
            });
        }

        List<Future<Boolean>> results = executor.invokeAll(tasks);
        executor.shutdown();
        executor.awaitTermination(5, TimeUnit.SECONDS);

        // Verify outcomes based on our simulation.
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