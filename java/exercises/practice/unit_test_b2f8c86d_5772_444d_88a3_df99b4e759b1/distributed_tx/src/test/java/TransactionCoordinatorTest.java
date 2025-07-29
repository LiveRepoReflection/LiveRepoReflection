import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

import static org.junit.jupiter.api.Assertions.*;

public class TransactionCoordinatorTest {

    private TransactionCoordinator coordinator;

    // Dummy implementations of TransactionalService for testing.
    static class SuccessfulService implements TransactionalService {
        private boolean prepared = false;
        private boolean committed = false;
        private boolean rolledBack = false;

        @Override
        public boolean prepare() {
            prepared = true;
            return true;
        }

        @Override
        public void commit() {
            committed = true;
        }

        @Override
        public void rollback() {
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

    static class FailingService implements TransactionalService {
        private boolean prepared = false;
        private boolean committed = false;
        private boolean rolledBack = false;

        @Override
        public boolean prepare() {
            prepared = true;
            return false;
        }

        @Override
        public void commit() {
            committed = true;
        }

        @Override
        public void rollback() {
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

    static class ExceptionService implements TransactionalService {

        @Override
        public boolean prepare() {
            throw new RuntimeException("Exception in prepare");
        }

        @Override
        public void commit() {
            throw new RuntimeException("Exception in commit");
        }

        @Override
        public void rollback() {
            // For testing, do nothing.
        }
    }

    static class DelayedService implements TransactionalService {
        private boolean committed = false;
        private boolean rolledBack = false;

        @Override
        public boolean prepare() {
            try {
                // Sleep longer than the coordinator's timeout to simulate delay
                Thread.sleep(6000);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            return true;
        }

        @Override
        public void commit() {
            committed = true;
        }

        @Override
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

    @BeforeEach
    public void setUp() {
        coordinator = new TransactionCoordinator();
    }

    @Test
    public void testSuccessfulTransaction() {
        SuccessfulService service1 = new SuccessfulService();
        SuccessfulService service2 = new SuccessfulService();

        coordinator.registerService(service1);
        coordinator.registerService(service2);

        String transactionId = coordinator.startTransaction();
        coordinator.executeTransaction(transactionId);

        // Both services should have been prepared and then committed.
        assertTrue(service1.isPrepared());
        assertTrue(service2.isPrepared());
        assertTrue(service1.isCommitted());
        assertTrue(service2.isCommitted());
    }

    @Test
    public void testFailingTransaction() {
        SuccessfulService service1 = new SuccessfulService();
        FailingService service2 = new FailingService();

        coordinator.registerService(service1);
        coordinator.registerService(service2);

        String transactionId = coordinator.startTransaction();
        coordinator.executeTransaction(transactionId);

        // When one service fails prepare, the entire transaction should roll back.
        assertTrue(service1.isPrepared());
        assertTrue(service2.isPrepared());
        assertTrue(service1.isRolledBack());
        // For failing service, rollback is also expected.
        assertTrue(service2.isRolledBack());
        // Commit should not have been called.
        assertFalse(service1.isCommitted());
        assertFalse(service2.isCommitted());
    }

    @Test
    public void testExceptionDuringPrepare() {
        SuccessfulService service1 = new SuccessfulService();
        ExceptionService service2 = new ExceptionService();

        coordinator.registerService(service1);
        coordinator.registerService(service2);

        String transactionId = coordinator.startTransaction();
        coordinator.executeTransaction(transactionId);

        // Exception in prepare should lead to rollback for all services.
        assertTrue(service1.isRolledBack());
        // Even though ExceptionService does not track state, its exception should force the coordinator to rollback.
        assertFalse(service1.isCommitted());
    }

    @Test
    public void testDelayedServiceTimeout() {
        SuccessfulService service1 = new SuccessfulService();
        DelayedService service2 = new DelayedService();

        coordinator.registerService(service1);
        coordinator.registerService(service2);

        String transactionId = coordinator.startTransaction();
        coordinator.executeTransaction(transactionId);

        // The delayed service should cause a timeout leading to rollback for all services.
        assertTrue(service1.isRolledBack());
        assertTrue(service2.isRolledBack());
        assertFalse(service1.isCommitted());
        assertFalse(service2.isCommitted());
    }

    @Test
    public void testConcurrentTransactions() throws InterruptedException {
        int transactionCount = 10;
        ExecutorService executor = Executors.newFixedThreadPool(transactionCount);
        AtomicInteger successTransactions = new AtomicInteger(0);

        Runnable transactionTask = () -> {
            TransactionCoordinator localCoordinator = new TransactionCoordinator();
            SuccessfulService service = new SuccessfulService();
            localCoordinator.registerService(service);
            String txId = localCoordinator.startTransaction();
            localCoordinator.executeTransaction(txId);
            if (service.isCommitted()) {
                successTransactions.incrementAndGet();
            }
        };

        for (int i = 0; i < transactionCount; i++) {
            executor.submit(transactionTask);
        }
        executor.shutdown();
        boolean terminated = executor.awaitTermination(15, TimeUnit.SECONDS);
        assertTrue(terminated);
        assertEquals(transactionCount, successTransactions.get());
    }

    @Test
    public void testExplicitCommitAfterPrepare() {
        SuccessfulService service1 = new SuccessfulService();

        coordinator.registerService(service1);

        String transactionId = coordinator.startTransaction();
        coordinator.executePreparePhase(transactionId);
        coordinator.commitTransaction(transactionId);

        assertTrue(service1.isCommitted());
        assertFalse(service1.isRolledBack());
    }

    @Test
    public void testExplicitRollbackAfterPrepare() {
        SuccessfulService service1 = new SuccessfulService();

        coordinator.registerService(service1);

        String transactionId = coordinator.startTransaction();
        coordinator.executePreparePhase(transactionId);
        coordinator.rollbackTransaction(transactionId);

        assertTrue(service1.isRolledBack());
        assertFalse(service1.isCommitted());
    }
}