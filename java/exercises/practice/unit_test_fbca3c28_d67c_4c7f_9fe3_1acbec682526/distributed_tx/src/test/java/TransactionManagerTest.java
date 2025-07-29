package distributed_tx;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.util.*;
import java.util.concurrent.*;

// Assume that the following interfaces/classes are part of the project:
// - TransactionManager: with methods begin(List<Microservice> services): UUID, commit(UUID transactionId): boolean, rollback(UUID transactionId): boolean, recover(): void.
// - Microservice: with methods prepare(UUID transactionId): String, commit(UUID transactionId): void, rollback(UUID transactionId): void.
// These interfaces are used by the TransactionManager to coordinate distributed transactions.

public class TransactionManagerTest {

    // A mock implementation of the Microservice to be used for testing.
    private class MockMicroservice implements Microservice {
        private final String id;
        private final boolean succeedPrepare;
        private final long responseDelayMs;

        public MockMicroservice(String id, boolean succeedPrepare, long responseDelayMs) {
            this.id = id;
            this.succeedPrepare = succeedPrepare;
            this.responseDelayMs = responseDelayMs;
        }

        // Simulate the prepare phase by sleeping for the specified delay and returning a status.
        @Override
        public String prepare(UUID transactionId) {
            try {
                Thread.sleep(responseDelayMs);
            } catch (InterruptedException e) {
                // In a real implementation, proper interrupt handling would be required.
            }
            return succeedPrepare ? "prepared" : "abort";
        }

        // Simulate commit. Since microservices are idempotent, no additional behavior is needed.
        @Override
        public void commit(UUID transactionId) {
            // No-op: in a unit test environment, we simply simulate success.
        }

        // Simulate rollback.
        @Override
        public void rollback(UUID transactionId) {
            // No-op: in a unit test environment, we simply simulate success.
        }

        @Override
        public String toString() {
            return id;
        }
    }

    // Test that a transaction commits successfully when all microservices prepare correctly.
    @Test
    public void testSuccessfulCommit() throws Exception {
        TransactionManager tm = new TransactionManager();
        List<Microservice> services = new ArrayList<>();
        services.add(new MockMicroservice("Service1", true, 10));
        services.add(new MockMicroservice("Service2", true, 20));
        services.add(new MockMicroservice("Service3", true, 30));

        UUID txnId = tm.begin(services);
        boolean commitResult = tm.commit(txnId);
        assertTrue(commitResult, "Transaction should commit successfully when all services return 'prepared'.");
    }

    // Test that a transaction is rolled back if any microservice fails during the prepare phase.
    @Test
    public void testPrepareFailure() throws Exception {
        TransactionManager tm = new TransactionManager();
        List<Microservice> services = new ArrayList<>();
        services.add(new MockMicroservice("Service1", true, 10));
        // This microservice will fail the prepare phase.
        services.add(new MockMicroservice("Service2", false, 20));
        services.add(new MockMicroservice("Service3", true, 30));

        UUID txnId = tm.begin(services);
        boolean commitResult = tm.commit(txnId);
        assertFalse(commitResult, "Transaction should rollback if any service returns 'abort' in prepare phase.");
    }

    // Test that a transaction is rolled back when one microservice response exceeds the TM timeout.
    @Test
    public void testTimeoutDuringPrepare() throws Exception {
        TransactionManager tm = new TransactionManager();
        List<Microservice> services = new ArrayList<>();
        services.add(new MockMicroservice("Service1", true, 10));
        // This microservice simulates a delay that exceeds the TM's timeout threshold.
        services.add(new MockMicroservice("Service2", true, 100));
        services.add(new MockMicroservice("Service3", true, 20));

        UUID txnId = tm.begin(services);
        boolean commitResult = tm.commit(txnId);
        assertFalse(commitResult, "Transaction should rollback when a prepare call times out.");
    }

    // Test that multiple concurrent transactions can be processed properly without interference or deadlocks.
    @Test
    public void testConcurrentTransactions() throws Exception {
        final TransactionManager tm = new TransactionManager();
        int numTransactions = 10;
        ExecutorService executor = Executors.newFixedThreadPool(5);
        List<Callable<Boolean>> tasks = new ArrayList<>();

        for (int i = 0; i < numTransactions; i++) {
            tasks.add(() -> {
                List<Microservice> services = Arrays.asList(
                    new MockMicroservice("Service1", true, 10),
                    new MockMicroservice("Service2", true, 10)
                );
                UUID txnId = tm.begin(services);
                return tm.commit(txnId);
            });
        }

        List<Future<Boolean>> futures = executor.invokeAll(tasks);
        executor.shutdown();
        for (Future<Boolean> future : futures) {
            assertTrue(future.get(), "All concurrent transactions should commit successfully.");
        }
    }

    // Test the crash recovery mechanism. A transaction that did not complete before a crash should be recovered properly.
    @Test
    public void testCrashRecovery() throws Exception {
        TransactionManager tm = new TransactionManager();
        List<Microservice> services = new ArrayList<>();
        services.add(new MockMicroservice("Service1", true, 10));
        services.add(new MockMicroservice("Service2", true, 10));

        UUID txnId = tm.begin(services);
        // Simulate a crash scenario by not calling commit immediately.
        tm.recover();
        // After recovery, attempting to commit should complete the transaction successfully.
        boolean commitResult = tm.commit(txnId);
        assertTrue(commitResult, "Recovered transaction should commit successfully after crash recovery.");
    }
}