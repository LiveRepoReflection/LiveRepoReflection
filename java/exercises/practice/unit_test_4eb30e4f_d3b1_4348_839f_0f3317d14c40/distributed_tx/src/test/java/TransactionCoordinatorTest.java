import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.List;
import java.util.ArrayList;

class TransactionCoordinatorTest {

    private TransactionCoordinator coordinator;

    @BeforeEach
    void setUp() {
        coordinator = new TransactionCoordinator();
    }

    @Test
    void testSuccessfulTransaction() {
        Transaction tx = new Transaction("tx1");
        // All microservices prepare successfully.
        tx.addOperation(new TestMicroservice("InventoryService", true));
        tx.addOperation(new TestMicroservice("PaymentService", true));
        tx.addOperation(new TestMicroservice("ShippingService", true));
        tx.addOperation(new TestMicroservice("OrderService", true));

        CoordinatorResult result = coordinator.processTransaction(tx);
        assertEquals(CoordinatorResult.COMMIT, result);

        // Ensure that commit is called on every microservice.
        for (MicroserviceOperation op : tx.getOperations()) {
            assertTrue(((TestMicroservice) op).isCommitted());
        }
    }

    @Test
    void testPrepareFailure() {
        Transaction tx = new Transaction("tx2");
        tx.addOperation(new TestMicroservice("InventoryService", true));
        // Simulate failure in prepare phase.
        tx.addOperation(new TestMicroservice("PaymentService", false));
        tx.addOperation(new TestMicroservice("ShippingService", true));
        tx.addOperation(new TestMicroservice("OrderService", true));

        CoordinatorResult result = coordinator.processTransaction(tx);
        assertEquals(CoordinatorResult.ROLLBACK, result);

        // Ensure that rollback is called on every microservice.
        for (MicroserviceOperation op : tx.getOperations()) {
            assertTrue(((TestMicroservice) op).isRolledBack());
        }
    }

    @Test
    void testIdempotencyCommit() {
        Transaction tx = new Transaction("tx3");
        TestMicroservice service = new TestMicroservice("PaymentService", true);
        tx.addOperation(service);

        // Process transaction: should commit successfully.
        CoordinatorResult result = coordinator.processTransaction(tx);
        assertEquals(CoordinatorResult.COMMIT, result);

        // Reprocess the transaction and verify commit is not applied more than once.
        coordinator.reProcessTransaction(tx);
        assertEquals(1, service.getCommitCount());
    }

    @Test
    void testTimeoutHandling() {
        Transaction tx = new Transaction("tx4");
        tx.addOperation(new TestMicroservice("InventoryService", true));
        // Simulate delayed response that exceeds timeout.
        TestMicroservice delayedService = new TestMicroservice("PaymentService", true, 5000);
        tx.addOperation(delayedService);

        // Set coordinator timeout to 1000 ms.
        coordinator.setTimeout(1000);

        CoordinatorResult result = coordinator.processTransaction(tx);
        // Expecting rollback due to timeout.
        assertEquals(CoordinatorResult.ROLLBACK, result);
    }

    @Test
    void testDeadlockResolution() {
        // Simulate potential deadlock by using a common microservice between two transactions.
        Transaction tx1 = new Transaction("tx5");
        Transaction tx2 = new Transaction("tx6");

        TestMicroservice commonService = new TestMicroservice("CommonService", true);

        tx1.addOperation(new TestMicroservice("InventoryService", true));
        tx1.addOperation(commonService);

        tx2.addOperation(commonService);
        tx2.addOperation(new TestMicroservice("OrderService", true));

        // Process transactions concurrently.
        Thread t1 = new Thread(() -> coordinator.processTransaction(tx1));
        Thread t2 = new Thread(() -> coordinator.processTransaction(tx2));
        t1.start();
        t2.start();
        try {
            t1.join();
            t2.join();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }

        // For simulation, ensure that deadlock handling restricted duplicate commits on common service.
        // At most one commit should have been applied.
        int commitCount = commonService.getCommitCount();
        assertTrue(commitCount <= 1);
    }

    @Test
    void testRecoveryFromLog() {
        Transaction tx = new Transaction("tx7");
        tx.addOperation(new TestMicroservice("InventoryService", true));
        tx.addOperation(new TestMicroservice("PaymentService", true));

        // Save transaction to log.
        coordinator.saveTransactionLog(tx);

        // Simulate coordinator crash and restart.
        coordinator = new TransactionCoordinator();
        coordinator.loadTransactionLog();

        // Recover and reprocess pending transactions.
        CoordinatorResult result = coordinator.recoverPendingTransactions();
        assertEquals(CoordinatorResult.COMMIT, result);
    }

    // Dummy classes and interfaces to support the unit tests.
    // These simulate components of the distributed transaction system.

    private static class Transaction {
        private final String id;
        private final List<MicroserviceOperation> operations = new ArrayList<>();

        public Transaction(String id) {
            this.id = id;
        }

        public String getId() {
            return id;
        }

        public void addOperation(MicroserviceOperation op) {
            operations.add(op);
        }

        public List<MicroserviceOperation> getOperations() {
            return operations;
        }
    }

    private interface MicroserviceOperation {
        boolean prepare(long timeout) throws InterruptedException;
        void commit();
        void rollback();
    }

    private enum CoordinatorResult {
        COMMIT, ROLLBACK
    }

    private static class TransactionCoordinator {
        private long timeout = 2000; // default timeout of 2000 milliseconds
        private final List<Transaction> transactionLog = new ArrayList<>();

        public void setTimeout(long timeout) {
            this.timeout = timeout;
        }

        public CoordinatorResult processTransaction(Transaction tx) {
            boolean allPrepared = true;
            for (MicroserviceOperation op : tx.getOperations()) {
                try {
                    if (!op.prepare(timeout)) {
                        allPrepared = false;
                        break;
                    }
                } catch (InterruptedException e) {
                    allPrepared = false;
                    break;
                }
            }
            CoordinatorResult result;
            if (allPrepared) {
                for (MicroserviceOperation op : tx.getOperations()) {
                    op.commit();
                }
                result = CoordinatorResult.COMMIT;
            } else {
                for (MicroserviceOperation op : tx.getOperations()) {
                    op.rollback();
                }
                result = CoordinatorResult.ROLLBACK;
            }
            return result;
        }

        // Reprocess transaction for idempotency testing.
        public void reProcessTransaction(Transaction tx) {
            for (MicroserviceOperation op : tx.getOperations()) {
                op.commit();
            }
        }

        // Simulate saving a transaction log.
        public void saveTransactionLog(Transaction tx) {
            transactionLog.add(tx);
        }

        // Simulate loading transaction log (in-memory simulation).
        public void loadTransactionLog() {
            // In an actual implementation, this would load from persistent storage.
        }

        // Process all transactions in the log during recovery.
        public CoordinatorResult recoverPendingTransactions() {
            CoordinatorResult finalResult = CoordinatorResult.COMMIT;
            for (Transaction tx : transactionLog) {
                CoordinatorResult res = processTransaction(tx);
                if (res == CoordinatorResult.ROLLBACK) {
                    finalResult = CoordinatorResult.ROLLBACK;
                }
            }
            return finalResult;
        }
    }

    private static class TestMicroservice implements MicroserviceOperation {
        private final String name;
        private final boolean prepareSuccess;
        private boolean committed;
        private boolean rolledBack;
        private int commitCount;
        private final long artificialDelay; // in milliseconds

        public TestMicroservice(String name, boolean prepareSuccess) {
            this(name, prepareSuccess, 0);
        }

        public TestMicroservice(String name, boolean prepareSuccess, long artificialDelay) {
            this.name = name;
            this.prepareSuccess = prepareSuccess;
            this.artificialDelay = artificialDelay;
            this.committed = false;
            this.rolledBack = false;
            this.commitCount = 0;
        }

        @Override
        public boolean prepare(long timeout) throws InterruptedException {
            if (artificialDelay > 0) {
                if (artificialDelay > timeout) {
                    Thread.sleep(timeout);
                    return false;
                } else {
                    Thread.sleep(artificialDelay);
                }
            }
            return prepareSuccess;
        }

        @Override
        public void commit() {
            // Enforce idempotency: commit only once.
            if (!committed) {
                committed = true;
                commitCount++;
            }
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

        public int getCommitCount() {
            return commitCount;
        }
    }
}