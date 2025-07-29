import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;

import static org.junit.jupiter.api.Assertions.*;

class DistributedTransactionManagerTest {

    private DistributedTransactionManager manager;

    @BeforeEach
    void setUp() {
        manager = new DistributedTransactionManager();
    }

    // A mock implementation of TransactionalService that always succeeds.
    private static class SuccessService implements TransactionalService {
        int prepareCount = 0;
        int commitCount = 0;
        int rollbackCount = 0;

        @Override
        public synchronized boolean prepare(UUID transactionId, Object data) {
            prepareCount++;
            return true;
        }

        @Override
        public synchronized boolean commit(UUID transactionId) {
            commitCount++;
            return true;
        }

        @Override
        public synchronized boolean rollback(UUID transactionId) {
            rollbackCount++;
            return true;
        }
    }

    // A mock implementation that always fails during the prepare phase.
    private static class FailingService implements TransactionalService {
        int prepareCount = 0;
        int commitCount = 0;
        int rollbackCount = 0;

        @Override
        public synchronized boolean prepare(UUID transactionId, Object data) {
            prepareCount++;
            return false;
        }

        @Override
        public synchronized boolean commit(UUID transactionId) {
            commitCount++;
            return true;
        }

        @Override
        public synchronized boolean rollback(UUID transactionId) {
            rollbackCount++;
            return true;
        }
    }

    // A mock implementation that simulates a delayed response in prepare.
    private static class DelayedService implements TransactionalService {
        int prepareCount = 0;
        int commitCount = 0;
        int rollbackCount = 0;
        private final long delayMillis;

        DelayedService(long delayMillis) {
            this.delayMillis = delayMillis;
        }

        @Override
        public synchronized boolean prepare(UUID transactionId, Object data) {
            prepareCount++;
            try {
                Thread.sleep(delayMillis);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            return true;
        }

        @Override
        public synchronized boolean commit(UUID transactionId) {
            commitCount++;
            return true;
        }

        @Override
        public synchronized boolean rollback(UUID transactionId) {
            rollbackCount++;
            return true;
        }
    }

    // A mock implementation to test idempotency.
    private static class IdempotentService implements TransactionalService {
        int prepareCount = 0;
        int commitCount = 0;
        int rollbackCount = 0;
        private final Object lock = new Object();
        private final List<UUID> preparedTransactions = new ArrayList<>();
        private final List<UUID> committedTransactions = new ArrayList<>();
        private final List<UUID> rolledBackTransactions = new ArrayList<>();

        @Override
        public boolean prepare(UUID transactionId, Object data) {
            synchronized (lock) {
                if (!preparedTransactions.contains(transactionId)) {
                    preparedTransactions.add(transactionId);
                    prepareCount++;
                }
            }
            return true;
        }

        @Override
        public boolean commit(UUID transactionId) {
            synchronized (lock) {
                if (!committedTransactions.contains(transactionId)) {
                    committedTransactions.add(transactionId);
                    commitCount++;
                }
            }
            return true;
        }

        @Override
        public boolean rollback(UUID transactionId) {
            synchronized (lock) {
                if (!rolledBackTransactions.contains(transactionId)) {
                    rolledBackTransactions.add(transactionId);
                    rollbackCount++;
                }
            }
            return true;
        }
    }

    @Test
    void testSuccessfulTransaction() throws Exception {
        SuccessService service1 = new SuccessService();
        SuccessService service2 = new SuccessService();
        manager.registerService(service1);
        manager.registerService(service2);

        UUID txId = manager.beginTransaction();
        boolean result = manager.commitTransaction(txId, "TestData");
        assertTrue(result, "Transaction should succeed when all services prepare and commit successfully.");

        // Verify that prepare and commit were called once in each service and rollback not called.
        assertEquals(1, service1.prepareCount);
        assertEquals(1, service2.prepareCount);
        assertEquals(1, service1.commitCount);
        assertEquals(1, service2.commitCount);
        assertEquals(0, service1.rollbackCount);
        assertEquals(0, service2.rollbackCount);
    }

    @Test
    void testPrepareFailure() throws Exception {
        SuccessService service1 = new SuccessService();
        FailingService service2 = new FailingService();
        manager.registerService(service1);
        manager.registerService(service2);

        UUID txId = manager.beginTransaction();
        boolean result = manager.commitTransaction(txId, "TestData");
        assertFalse(result, "Transaction should fail if any service fails during prepare.");

        // On failure, both services should have rollback called.
        assertEquals(1, service1.prepareCount);
        assertEquals(1, service2.prepareCount);
        assertEquals(0, service1.commitCount);
        assertEquals(0, service2.commitCount);
        assertEquals(1, service1.rollbackCount);
        assertEquals(1, service2.rollbackCount);
    }

    @Test
    @Timeout(value = 5, unit = TimeUnit.SECONDS)
    void testPrepareTimeout() throws Exception {
        // Assume the manager uses a timeout less than 2000ms for prepare phase.
        DelayedService delayedService = new DelayedService(3000);
        manager.registerService(delayedService);

        UUID txId = manager.beginTransaction();
        boolean result = manager.commitTransaction(txId, "TestData");
        // The delayed service should trigger a timeout causing rollback.
        assertFalse(result, "Transaction should fail and rollback due to timeout in prepare.");

        // Verify that prepare was attempted but commit was not called, and rollback was called.
        assertEquals(1, delayedService.prepareCount);
        assertEquals(0, delayedService.commitCount);
        assertEquals(1, delayedService.rollbackCount);
    }

    @Test
    void testIdempotency() throws Exception {
        IdempotentService idempotentService = new IdempotentService();
        manager.registerService(idempotentService);

        UUID txId = manager.beginTransaction();
        // Call commitTransaction twice for the same transaction id.
        boolean firstAttempt = manager.commitTransaction(txId, "TestData");
        boolean secondAttempt = manager.commitTransaction(txId, "TestData");

        // Both attempts should result in a success, but the service methods must be invoked only once.
        assertTrue(firstAttempt, "First commit attempt should succeed.");
        assertTrue(secondAttempt, "Second commit attempt should succeed due to idempotency.");
        assertEquals(1, idempotentService.prepareCount, "Prepare should be called only once.");
        assertEquals(1, idempotentService.commitCount, "Commit should be called only once.");
        // In a successful commit, rollback should never be called.
        assertEquals(0, idempotentService.rollbackCount, "Rollback should not be called.");
    }

    @Test
    void testConcurrency() throws Exception {
        int threadCount = 10;
        int transactionsPerThread = 5;
        SuccessService service = new SuccessService();
        manager.registerService(service);

        ExecutorService executor = Executors.newFixedThreadPool(threadCount);
        CountDownLatch latch = new CountDownLatch(threadCount);
        List<Future<Boolean>> futures = new ArrayList<>();

        for (int i = 0; i < threadCount; i++) {
            futures.add(executor.submit(new Callable<Boolean>() {
                @Override
                public Boolean call() throws Exception {
                    for (int j = 0; j < transactionsPerThread; j++) {
                        UUID txId = manager.beginTransaction();
                        boolean result = manager.commitTransaction(txId, "ConcurrentData");
                        if (!result) {
                            return false;
                        }
                    }
                    latch.countDown();
                    return true;
                }
            }));
        }

        latch.await(10, TimeUnit.SECONDS);
        executor.shutdown();
        executor.awaitTermination(10, TimeUnit.SECONDS);

        for (Future<Boolean> future : futures) {
            assertTrue(future.get(), "All concurrent transactions should commit successfully.");
        }
        // Total prepare and commit counts must equal threadCount * transactionsPerThread.
        int expectedCalls = threadCount * transactionsPerThread;
        assertEquals(expectedCalls, service.prepareCount, "Total prepare calls mismatch in concurrency test.");
        assertEquals(expectedCalls, service.commitCount, "Total commit calls mismatch in concurrency test.");
        assertEquals(0, service.rollbackCount, "Rollback should not be called in successful concurrent transactions.");
    }
}