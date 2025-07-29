import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;

public class TransactionManagerTest {

    // Define a Service interface as described in the problem statement.
    interface Service {
        boolean prepare(String transactionId) throws InterruptedException;
        void commit(String transactionId);
        void rollback(String transactionId);
    }

    // A dummy implementation for testing successful prepare, commit, and rollback.
    static class TestService implements Service {
        private final String name;
        private final long delayInMillis;
        private final boolean shouldPrepareSucceed;
        // Records for inspection
        final List<String> log = new CopyOnWriteArrayList<>();
        final AtomicBoolean commitCalled = new AtomicBoolean(false);
        final AtomicBoolean rollbackCalled = new AtomicBoolean(false);

        TestService(String name, boolean shouldPrepareSucceed, long delayInMillis) {
            this.name = name;
            this.shouldPrepareSucceed = shouldPrepareSucceed;
            this.delayInMillis = delayInMillis;
        }

        @Override
        public boolean prepare(String transactionId) throws InterruptedException {
            if (delayInMillis > 0) {
                Thread.sleep(delayInMillis);
            }
            log.add(name + ":prepare:" + transactionId);
            return shouldPrepareSucceed;
        }

        @Override
        public void commit(String transactionId) {
            log.add(name + ":commit:" + transactionId);
            commitCalled.set(true);
        }

        @Override
        public void rollback(String transactionId) {
            log.add(name + ":rollback:" + transactionId);
            rollbackCalled.set(true);
        }
    }

    // A dummy implementation for testing timeout behavior.
    // This service never responds to prepare.
    static class TimeoutService implements Service {
        private final String name;

        TimeoutService(String name) {
            this.name = name;
        }

        @Override
        public boolean prepare(String transactionId) throws InterruptedException {
            // Simulate never returning (sleep more than timeout)
            Thread.sleep(10000);
            return true;
        }

        @Override
        public void commit(String transactionId) {
            // Should never be called in a timeout scenario.
        }

        @Override
        public void rollback(String transactionId) {
            // Do nothing
        }
    }

    // A simple TransactionManager implementation stub.
    // In unit tests, we assume the real implementation exists.
    // We provide a minimal mock-up for compiling the tests.
    static class TransactionManager {
        private final ConcurrentMap<String, List<Service>> transactions = new ConcurrentHashMap<>();
        // Timeout in milliseconds for the prepare phase.
        private final long prepareTimeoutMillis = 5000;
        // Executor for asynchronous tasks.
        private final ExecutorService executor = Executors.newCachedThreadPool();

        public String beginTransaction() {
            String txId = UUID.randomUUID().toString();
            transactions.put(txId, new CopyOnWriteArrayList<>());
            return txId;
        }

        public void enlistService(String transactionId, Service service) {
            List<Service> services = transactions.get(transactionId);
            if (services != null) {
                services.add(service);
            } else {
                throw new IllegalArgumentException("Transaction not found: " + transactionId);
            }
        }

        public boolean commitTransaction(String transactionId) {
            List<Service> services = transactions.get(transactionId);
            if (services == null) {
                throw new IllegalArgumentException("Transaction not found: " + transactionId);
            }

            List<Future<Boolean>> prepareFutures = new ArrayList<>();
            for (Service service : services) {
                Future<Boolean> future = executor.submit(() -> {
                    try {
                        return service.prepare(transactionId);
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                        return false;
                    }
                });
                prepareFutures.add(future);
            }

            boolean allPrepared = true;
            for (Future<Boolean> future : prepareFutures) {
                try {
                    Boolean result = future.get(prepareTimeoutMillis, TimeUnit.MILLISECONDS);
                    if (!result) {
                        allPrepared = false;
                    }
                } catch (TimeoutException | InterruptedException | ExecutionException e) {
                    allPrepared = false;
                }
            }

            if (allPrepared) {
                // All prepared successfully; commit on all services
                for (Service service : services) {
                    executor.submit(() -> service.commit(transactionId));
                }
            } else {
                // Rollback if any one fails or timeout occurs.
                for (Service service : services) {
                    executor.submit(() -> service.rollback(transactionId));
                }
            }
            // Clean up transaction
            transactions.remove(transactionId);
            return allPrepared;
        }

        public void rollbackTransaction(String transactionId) {
            List<Service> services = transactions.get(transactionId);
            if (services != null) {
                for (Service service : services) {
                    executor.submit(() -> service.rollback(transactionId));
                }
                transactions.remove(transactionId);
            }
        }

        public void shutdown() {
            executor.shutdownNow();
        }
    }

    private final TransactionManager transactionManager = new TransactionManager();

    @AfterEach
    public void tearDown() {
        transactionManager.shutdown();
    }

    @Test
    public void testSuccessfulTransaction() throws InterruptedException {
        String txId = transactionManager.beginTransaction();
        TestService service1 = new TestService("Service1", true, 0);
        TestService service2 = new TestService("Service2", true, 0);
        transactionManager.enlistService(txId, service1);
        transactionManager.enlistService(txId, service2);

        boolean result = transactionManager.commitTransaction(txId);
        Assertions.assertTrue(result);
        // Allow some time for async commits
        Thread.sleep(100);
        Assertions.assertTrue(service1.commitCalled.get());
        Assertions.assertTrue(service2.commitCalled.get());
        Assertions.assertFalse(service1.rollbackCalled.get());
        Assertions.assertFalse(service2.rollbackCalled.get());
    }

    @Test
    public void testFailedPrepareTransaction() throws InterruptedException {
        String txId = transactionManager.beginTransaction();
        TestService service1 = new TestService("Service1", true, 0);
        // This service will fail preparation.
        TestService service2 = new TestService("Service2", false, 0);
        transactionManager.enlistService(txId, service1);
        transactionManager.enlistService(txId, service2);

        boolean result = transactionManager.commitTransaction(txId);
        Assertions.assertFalse(result);
        // Allow time for async rollbacks
        Thread.sleep(100);
        Assertions.assertFalse(service1.commitCalled.get());
        Assertions.assertFalse(service2.commitCalled.get());
        Assertions.assertTrue(service1.rollbackCalled.get());
        Assertions.assertTrue(service2.rollbackCalled.get());
    }

    @Test
    public void testTimeoutPrepareTransaction() throws InterruptedException {
        String txId = transactionManager.beginTransaction();
        TestService service1 = new TestService("Service1", true, 0);
        // Timeout service sleeps for 10 seconds, exceeding the 5-second limit.
        TimeoutService service2 = new TimeoutService("TimeoutService");
        transactionManager.enlistService(txId, service1);
        transactionManager.enlistService(txId, service2);

        boolean result = transactionManager.commitTransaction(txId);
        Assertions.assertFalse(result);
        // Allow time for async rollbacks, though TimeoutService does nothing.
        Thread.sleep(100);
        Assertions.assertFalse(service1.commitCalled.get());
        Assertions.assertTrue(service1.rollbackCalled.get());
    }

    @Test
    public void testRollbackTransactionExplicitly() throws InterruptedException {
        String txId = transactionManager.beginTransaction();
        TestService service1 = new TestService("Service1", true, 0);
        TestService service2 = new TestService("Service2", true, 0);
        transactionManager.enlistService(txId, service1);
        transactionManager.enlistService(txId, service2);

        // Explicitly rollback before commit.
        transactionManager.rollbackTransaction(txId);
        // Allow time for async rollbacks.
        Thread.sleep(100);

        Assertions.assertTrue(service1.rollbackCalled.get());
        Assertions.assertTrue(service2.rollbackCalled.get());
        // Even if we try to commit afterwards, transaction should not be found.
        Assertions.assertThrows(IllegalArgumentException.class, () -> transactionManager.commitTransaction(txId));
    }

    @Test
    public void testConcurrentTransactions() throws InterruptedException, ExecutionException {
        int concurrentTransactions = 10;
        ExecutorService testExecutor = Executors.newFixedThreadPool(concurrentTransactions);
        List<Future<Boolean>> results = new ArrayList<>();
        AtomicInteger successCount = new AtomicInteger(0);

        for (int i = 0; i < concurrentTransactions; i++) {
            Future<Boolean> future = testExecutor.submit(() -> {
                String txId = transactionManager.beginTransaction();
                TestService service1 = new TestService("Service1", true, 0);
                TestService service2 = new TestService("Service2", true, 0);
                transactionManager.enlistService(txId, service1);
                transactionManager.enlistService(txId, service2);
                boolean committed = transactionManager.commitTransaction(txId);
                if (committed) {
                    successCount.incrementAndGet();
                }
                // Wait a little to let async tasks complete.
                Thread.sleep(50);
                return committed;
            });
            results.add(future);
        }
        for (Future<Boolean> future : results) {
            future.get();
        }
        testExecutor.shutdown();
        Assertions.assertEquals(concurrentTransactions, successCount.get());
    }

    @Test
    public void testIdempotentRollback() throws InterruptedException {
        String txId = transactionManager.beginTransaction();
        TestService service1 = new TestService("Service1", true, 0);
        transactionManager.enlistService(txId, service1);
        // Call rollback multiple times
        transactionManager.rollbackTransaction(txId);
        // Second rollback should do nothing harmful.
        transactionManager.rollbackTransaction(txId);
        // Allow time for async rollbacks.
        Thread.sleep(100);
        Assertions.assertTrue(service1.rollbackCalled.get());
    }
}