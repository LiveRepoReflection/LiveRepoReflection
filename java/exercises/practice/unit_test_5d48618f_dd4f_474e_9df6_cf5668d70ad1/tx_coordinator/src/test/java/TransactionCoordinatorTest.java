import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;

import static org.junit.jupiter.api.Assertions.*;

class TransactionCoordinatorTest {

    private TransactionCoordinator coordinator;

    @BeforeEach
    void setUp() {
        coordinator = new TransactionCoordinator();
    }

    // A dummy implementation of Service for testing purposes.
    private static class TestService implements Service {
        private final boolean failPrepare;
        private final boolean failCommit;
        private final List<String> log;
        private boolean prepared = false;
        private boolean committed = false;
        private boolean rolledback = false;
        private int prepareCount = 0;
        private int commitCount = 0;
        private int rollbackCount = 0;
        
        TestService(boolean failPrepare, boolean failCommit) {
            this.failPrepare = failPrepare;
            this.failCommit = failCommit;
            this.log = Collections.synchronizedList(new ArrayList<>());
        }

        @Override
        public boolean prepare(String transactionId) {
            prepareCount++;
            log.add("prepare:" + transactionId);
            if (failPrepare) {
                return false;
            }
            prepared = true;
            return true;
        }

        @Override
        public boolean commit(String transactionId) {
            commitCount++;
            log.add("commit:" + transactionId);
            if (!prepared) {
                // Should not commit if not prepared.
                return false;
            }
            if (failCommit) {
                return false;
            }
            committed = true;
            return true;
        }

        @Override
        public boolean rollback(String transactionId) {
            rollbackCount++;
            log.add("rollback:" + transactionId);
            rolledback = true;
            return true;
        }

        public boolean isPrepared() {
            return prepared;
        }

        public boolean isCommitted() {
            return committed;
        }

        public boolean isRolledback() {
            return rolledback;
        }
        
        public int getPrepareCount() {
            return prepareCount;
        }
        
        public int getCommitCount() {
            return commitCount;
        }
        
        public int getRollbackCount() {
            return rollbackCount;
        }
        
        public List<String> getLog() {
            return log;
        }
    }

    @Test
    void testSuccessfulTransaction() {
        String txId = coordinator.begin();
        TestService service1 = new TestService(false, false);
        TestService service2 = new TestService(false, false);

        coordinator.enlistService(txId, service1);
        coordinator.enlistService(txId, service2);

        boolean success = coordinator.commit(txId);
        assertTrue(success, "Transaction should commit successfully.");

        // Both services should have been prepared and committed without rollback.
        assertTrue(service1.isPrepared(), "Service1 should be prepared.");
        assertTrue(service2.isPrepared(), "Service2 should be prepared.");
        assertTrue(service1.isCommitted(), "Service1 should be committed.");
        assertTrue(service2.isCommitted(), "Service2 should be committed.");
        assertFalse(service1.isRolledback(), "Service1 should not have rolled back.");
        assertFalse(service2.isRolledback(), "Service2 should not have rolled back.");
    }

    @Test
    void testPrepareFailure() {
        String txId = coordinator.begin();
        TestService service1 = new TestService(true, false); // Will fail in prepare
        TestService service2 = new TestService(false, false);

        coordinator.enlistService(txId, service1);
        coordinator.enlistService(txId, service2);

        boolean success = coordinator.commit(txId);
        assertFalse(success, "Transaction should fail due to prepare failure.");

        // In rollback scenario, both services must have rollback been called.
        assertTrue(service1.isRolledback(), "Service1 should have rolled back.");
        assertTrue(service2.isRolledback(), "Service2 should have rolled back.");
        // Even though service2 prepared successfully, rollback should be invoked.
        assertTrue(service2.isPrepared(), "Service2 should have been prepared.");
        assertFalse(service1.isCommitted(), "Service1 should not commit.");
        assertFalse(service2.isCommitted(), "Service2 should not commit.");
    }

    @Test
    void testCommitFailure() {
        String txId = coordinator.begin();
        TestService service1 = new TestService(false, true); // Will fail on commit
        TestService service2 = new TestService(false, false);

        coordinator.enlistService(txId, service1);
        coordinator.enlistService(txId, service2);

        boolean success = coordinator.commit(txId);
        assertFalse(success, "Transaction should fail due to commit failure.");

        // Even though prepare succeeded, commit failure requires rollback on all.
        assertTrue(service1.isRolledback(), "Service1 should have been rolled back.");
        assertTrue(service2.isRolledback(), "Service2 should have been rolled back.");

        // Ensure commit was attempted
        assertEquals(1, service1.getCommitCount(), "Service1 commit should be attempted once.");
        assertEquals(1, service2.getCommitCount(), "Service2 commit should be attempted once.");
    }

    @Test
    void testIdempotency() {
        String txId = coordinator.begin();
        TestService service1 = new TestService(false, false);
        TestService service2 = new TestService(false, false);

        coordinator.enlistService(txId, service1);
        coordinator.enlistService(txId, service2);

        boolean firstAttempt = coordinator.commit(txId);
        assertTrue(firstAttempt, "First commit should succeed.");
        // Call commit again; should have no additional effect.
        boolean secondAttempt = coordinator.commit(txId);
        assertTrue(secondAttempt, "Second commit should be idempotent and not fail.");

        // Verify that commit methods on the services were called only once.
        assertEquals(1, service1.getCommitCount(), "Service1 commit should be called only once.");
        assertEquals(1, service2.getCommitCount(), "Service2 commit should be called only once.");
    }

    @Test
    @Timeout(value = 10, unit = TimeUnit.SECONDS)
    void testConcurrentTransactions() throws InterruptedException, ExecutionException {
        int threadCount = 10;
        ExecutorService executor = Executors.newFixedThreadPool(threadCount);
        List<Callable<Boolean>> tasks = new ArrayList<>();

        for (int i = 0; i < threadCount; i++) {
            tasks.add(() -> {
                String txId = coordinator.begin();
                TestService serviceA = new TestService(false, false);
                TestService serviceB = new TestService(false, false);
                // Enlist a couple of services in the transaction.
                coordinator.enlistService(txId, serviceA);
                coordinator.enlistService(txId, serviceB);
                // Simulate some randomness in processing.
                return coordinator.commit(txId);
            });
        }
        List<Future<Boolean>> results = executor.invokeAll(tasks);
        for (Future<Boolean> future : results) {
            assertTrue(future.get(), "All concurrent transactions should commit successfully.");
        }
        executor.shutdown();
    }
}