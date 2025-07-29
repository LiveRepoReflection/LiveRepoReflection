package distributed_tx.src.test.java;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;

import static org.junit.jupiter.api.Assertions.*;

import distributed_tx.Microservice;
import distributed_tx.TransactionCoordinator;

public class TransactionCoordinatorTest {

    private TransactionCoordinator coordinator;

    @BeforeEach
    public void setUp() {
        coordinator = new TransactionCoordinator();
    }

    private static class SuccessfulMicroservice implements Microservice {
        private boolean prepared = false;
        private boolean committed = false;
        private boolean rolledBack = false;

        @Override
        public boolean prepare(int transactionId) {
            prepared = true;
            return true;
        }

        @Override
        public void commit(int transactionId) {
            committed = true;
        }

        @Override
        public void rollback(int transactionId) {
            rolledBack = true;
        }

        public boolean isPrepared() {
            return prepared;
        }

        public boolean isCommitted() {
            return committed;
        }

        public boolean isRolledBack() {
            return rolledBack;
        }
    }

    private static class FailingMicroservice implements Microservice {
        private boolean rolledBack = false;

        @Override
        public boolean prepare(int transactionId) {
            return false;
        }

        @Override
        public void commit(int transactionId) {
        }

        @Override
        public void rollback(int transactionId) {
            rolledBack = true;
        }

        public boolean isRolledBack() {
            return rolledBack;
        }
    }

    private static class ExceptionMicroservice implements Microservice {
        private boolean rolledBack = false;

        @Override
        public boolean prepare(int transactionId) {
            throw new RuntimeException("Prepare exception");
        }

        @Override
        public void commit(int transactionId) {
        }

        @Override
        public void rollback(int transactionId) {
            rolledBack = true;
        }

        public boolean isRolledBack() {
            return rolledBack;
        }
    }

    private static class DelayedMicroservice implements Microservice {
        private final long delayMillis;
        private boolean rolledBack = false;

        public DelayedMicroservice(long delayMillis) {
            this.delayMillis = delayMillis;
        }

        @Override
        public boolean prepare(int transactionId) {
            try {
                Thread.sleep(delayMillis);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            return true;
        }

        @Override
        public void commit(int transactionId) {
        }

        @Override
        public void rollback(int transactionId) {
            rolledBack = true;
        }

        public boolean isRolledBack() {
            return rolledBack;
        }
    }

    @Test
    public void testSuccessfulCommit() {
        SuccessfulMicroservice service1 = new SuccessfulMicroservice();
        SuccessfulMicroservice service2 = new SuccessfulMicroservice();
        int txId = coordinator.begin();
        coordinator.enlist(txId, service1);
        coordinator.enlist(txId, service2);

        boolean commitResult = coordinator.commit(txId);
        assertTrue(commitResult, "Commit should succeed when all microservices prepare successfully.");
        assertTrue(service1.isPrepared(), "Service1 should have been prepared.");
        assertTrue(service2.isPrepared(), "Service2 should have been prepared.");
        assertTrue(service1.isCommitted(), "Service1 should have committed.");
        assertTrue(service2.isCommitted(), "Service2 should have committed.");
    }

    @Test
    public void testPrepareFailureTriggersRollback() {
        SuccessfulMicroservice service1 = new SuccessfulMicroservice();
        FailingMicroservice service2 = new FailingMicroservice();
        int txId = coordinator.begin();
        coordinator.enlist(txId, service1);
        coordinator.enlist(txId, service2);

        boolean commitResult = coordinator.commit(txId);
        assertFalse(commitResult, "Commit should fail if any microservice fails prepare.");
        assertTrue(service1.isRolledBack(), "Service1 should have rolled back after prepare failure.");
        assertTrue(service2.isRolledBack(), "Service2 should have rolled back after prepare failure.");
    }

    @Test
    public void testExceptionInPrepareTriggersRollback() {
        SuccessfulMicroservice service1 = new SuccessfulMicroservice();
        ExceptionMicroservice service2 = new ExceptionMicroservice();
        int txId = coordinator.begin();
        coordinator.enlist(txId, service1);
        coordinator.enlist(txId, service2);

        boolean commitResult = coordinator.commit(txId);
        assertFalse(commitResult, "Commit should fail if any microservice throws an exception during prepare.");
        assertTrue(service1.isRolledBack(), "Service1 should have rolled back on exception in partner service.");
        assertTrue(service2.isRolledBack(), "Service2 should have rolled back on exception.");
    }

    @Test
    @Timeout(value = 7, unit = TimeUnit.SECONDS)
    public void testDelayedPrepareTimeoutTriggersRollback() {
        long delay = 6000;
        DelayedMicroservice delayedService = new DelayedMicroservice(delay);
        SuccessfulMicroservice service = new SuccessfulMicroservice();
        int txId = coordinator.begin();
        coordinator.enlist(txId, delayedService);
        coordinator.enlist(txId, service);

        boolean commitResult = coordinator.commit(txId);
        assertFalse(commitResult, "Commit should fail when one service times out.");
        assertTrue(delayedService.isRolledBack(), "Delayed service should have rolled back due to timeout.");
        assertTrue(service.isRolledBack(), "Service should have rolled back due to timeout in partner service.");
    }

    @Test
    public void testRollbackMethodIndependently() {
        SuccessfulMicroservice service1 = new SuccessfulMicroservice();
        SuccessfulMicroservice service2 = new SuccessfulMicroservice();
        int txId = coordinator.begin();
        coordinator.enlist(txId, service1);
        coordinator.enlist(txId, service2);

        boolean rollbackResult = coordinator.rollback(txId);
        assertTrue(rollbackResult, "Rollback should succeed when all enlisted services rollback successfully.");
        assertTrue(service1.isRolledBack(), "Service1 should have rolled back.");
        assertTrue(service2.isRolledBack(), "Service2 should have rolled back.");
    }

    @Test
    public void testConcurrentTransactions() throws Exception {
        int threadCount = 10;
        ExecutorService executor = Executors.newFixedThreadPool(threadCount);
        List<Callable<Boolean>> tasks = new ArrayList<>();
        CountDownLatch latch = new CountDownLatch(1);

        for (int i = 0; i < threadCount; i++) {
            tasks.add(() -> {
                latch.await();
                SuccessfulMicroservice service = new SuccessfulMicroservice();
                int txId = coordinator.begin();
                coordinator.enlist(txId, service);
                return coordinator.commit(txId);
            });
        }

        latch.countDown();
        List<Future<Boolean>> results = executor.invokeAll(tasks);

        for (Future<Boolean> future : results) {
            assertTrue(future.get(), "Each concurrent transaction should commit successfully.");
        }
        executor.shutdown();
        assertTrue(executor.awaitTermination(5, TimeUnit.SECONDS), "Executor did not terminate in the allotted time.");
    }
}