package distributed_tx;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;
import org.junit.jupiter.api.Assertions;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.Executors;
import java.util.concurrent.ExecutorService;

/**
 * Comprehensive unit tests for the Distributed Transaction Manager using 2PC.
 * 
 * Assumptions:
 *  - A TransactionManager class exists with methods:
 *       String beginTransaction();
 *       void registerService(Service service);
 *       void addOperation(String transactionId, Operation op);
 *       void executeTransaction(String transactionId);
 *       TransactionStatus getTransactionStatus(String transactionId);
 *
 *  - A Service interface exists with methods:
 *       boolean prepare(String transactionId, Operation op) throws Exception;
 *       void commit(String transactionId) throws Exception;
 *       void rollback(String transactionId) throws Exception;
 *       String getName();
 *
 *  - An Operation class exists that encapsulates the operation details for a service.
 *
 * The unit tests below simulate various scenarios including successful transactions,
 * prepare failures, timeouts, concurrent transactions, and idempotency behavior.
 */
public class TransactionManagerTest {

    private TransactionManager transactionManager;

    @BeforeEach
    public void setUp() {
        // Assuming the TransactionManager has a default constructor.
        transactionManager = new TransactionManager();
    }

    /**
     * A mock implementation of the Service interface to simulate behavior.
     */
    public static class MockService implements Service {
        private final String name;
        private final boolean prepareSuccess;
        private final boolean commitSuccess;
        private final boolean rollbackSuccess;
        private final long prepareDelayMillis;
        private boolean prepareCalled = false;
        private boolean commitCalled = false;
        private boolean rollbackCalled = false;

        public MockService(String name, boolean prepareSuccess, boolean commitSuccess, boolean rollbackSuccess, long prepareDelayMillis) {
            this.name = name;
            this.prepareSuccess = prepareSuccess;
            this.commitSuccess = commitSuccess;
            this.rollbackSuccess = rollbackSuccess;
            this.prepareDelayMillis = prepareDelayMillis;
        }

        @Override
        public boolean prepare(String transactionId, Operation op) throws Exception {
            prepareCalled = true;
            if (prepareDelayMillis > 0) {
                Thread.sleep(prepareDelayMillis);
            }
            return prepareSuccess;
        }

        @Override
        public void commit(String transactionId) throws Exception {
            commitCalled = true;
            if (!commitSuccess) {
                throw new Exception("Commit failed at service: " + name);
            }
        }

        @Override
        public void rollback(String transactionId) throws Exception {
            rollbackCalled = true;
            if (!rollbackSuccess) {
                throw new Exception("Rollback failed at service: " + name);
            }
        }

        @Override
        public String getName() {
            return name;
        }

        public boolean isPrepareCalled() {
            return prepareCalled;
        }

        public boolean isCommitCalled() {
            return commitCalled;
        }

        public boolean isRollbackCalled() {
            return rollbackCalled;
        }
    }

    /**
     * A helper method to create a dummy Operation.
     * Assumes the Operation takes a service name, operation detail, and some data.
     */
    private Operation createOperation(String serviceName, String detail, Object data) {
        // Assuming Operation has a constructor: Operation(String serviceName, String detail, Object data)
        return new Operation(serviceName, detail, data);
    }

    @Test
    public void testSuccessfulTransaction() throws Exception {
        // Create two services that will succeed in prepare and commit.
        MockService serviceA = new MockService("ServiceA", true, true, true, 0);
        MockService serviceB = new MockService("ServiceB", true, true, true, 0);

        transactionManager.registerService(serviceA);
        transactionManager.registerService(serviceB);

        String txId = transactionManager.beginTransaction();
        transactionManager.addOperation(txId, createOperation(serviceA.getName(), "opA", "dataA"));
        transactionManager.addOperation(txId, createOperation(serviceB.getName(), "opB", "dataB"));

        transactionManager.executeTransaction(txId);

        Assertions.assertEquals(TransactionStatus.COMMITTED, transactionManager.getTransactionStatus(txId),
                "Transaction should be committed successfully.");
        Assertions.assertTrue(serviceA.isPrepareCalled(), "ServiceA should have been prepared.");
        Assertions.assertTrue(serviceB.isPrepareCalled(), "ServiceB should have been prepared.");
        Assertions.assertTrue(serviceA.isCommitCalled(), "ServiceA should have been committed.");
        Assertions.assertTrue(serviceB.isCommitCalled(), "ServiceB should have been committed.");
    }

    @Test
    public void testPrepareFailure() throws Exception {
        // Create one service that fails in prepare.
        MockService serviceA = new MockService("ServiceA", true, true, true, 0);
        MockService serviceB = new MockService("ServiceB", false, true, true, 0); // Fails in prepare.

        transactionManager.registerService(serviceA);
        transactionManager.registerService(serviceB);

        String txId = transactionManager.beginTransaction();
        transactionManager.addOperation(txId, createOperation(serviceA.getName(), "opA", "dataA"));
        transactionManager.addOperation(txId, createOperation(serviceB.getName(), "opB", "dataB"));

        transactionManager.executeTransaction(txId);

        Assertions.assertEquals(TransactionStatus.ROLLEDBACK, transactionManager.getTransactionStatus(txId),
                "Transaction should be rolled back due to prepare failure.");
        Assertions.assertTrue(serviceA.isPrepareCalled(), "ServiceA should have been prepared.");
        Assertions.assertTrue(serviceB.isPrepareCalled(), "ServiceB should have been prepared.");
        Assertions.assertTrue(serviceA.isRollbackCalled(), "ServiceA should have been rolled back.");
        Assertions.assertTrue(serviceB.isRollbackCalled(), "ServiceB should have been rolled back.");
    }

    @Test
    public void testTimeoutTransaction() throws Exception {
        // Create a service that simulates a delay causing a timeout.
        // Assuming that TransactionManager is configured with a timeout threshold less than 2000 ms.
        MockService serviceA = new MockService("ServiceA", true, true, true, 0);
        MockService serviceB = new MockService("ServiceB", true, true, true, 3000); // Delayed prepare causing timeout.

        transactionManager.registerService(serviceA);
        transactionManager.registerService(serviceB);

        String txId = transactionManager.beginTransaction();
        transactionManager.addOperation(txId, createOperation(serviceA.getName(), "opA", "dataA"));
        transactionManager.addOperation(txId, createOperation(serviceB.getName(), "opB", "dataB"));

        transactionManager.executeTransaction(txId);

        Assertions.assertEquals(TransactionStatus.ROLLEDBACK, transactionManager.getTransactionStatus(txId),
                "Transaction should be rolled back due to prepare timeout.");
        Assertions.assertTrue(serviceA.isPrepareCalled(), "ServiceA should have been prepared.");
        Assertions.assertTrue(serviceB.isPrepareCalled(), "ServiceB should have been prepared.");
        Assertions.assertTrue(serviceA.isRollbackCalled(), "ServiceA should have been rolled back.");
        Assertions.assertTrue(serviceB.isRollbackCalled(), "ServiceB should have been rolled back.");
    }

    @Test
    public void testConcurrentTransactions() throws Exception {
        final int transactionCount = 10;
        final ExecutorService executor = Executors.newFixedThreadPool(transactionCount);
        final CountDownLatch latch = new CountDownLatch(transactionCount);
        final List<String> txIds = new ArrayList<>();

        // Pre-register services that always succeed.
        MockService serviceA = new MockService("ServiceA", true, true, true, 0);
        MockService serviceB = new MockService("ServiceB", true, true, true, 0);
        transactionManager.registerService(serviceA);
        transactionManager.registerService(serviceB);

        for (int i = 0; i < transactionCount; i++) {
            executor.submit(() -> {
                try {
                    String txId = transactionManager.beginTransaction();
                    synchronized (txIds) {
                        txIds.add(txId);
                    }
                    transactionManager.addOperation(txId, createOperation(serviceA.getName(), "opA", UUID.randomUUID().toString()));
                    transactionManager.addOperation(txId, createOperation(serviceB.getName(), "opB", UUID.randomUUID().toString()));
                    transactionManager.executeTransaction(txId);
                } catch (Exception e) {
                    // Exception in one transaction should not affect others.
                } finally {
                    latch.countDown();
                }
            });
        }
        latch.await(5, TimeUnit.SECONDS);
        executor.shutdownNow();

        synchronized (txIds) {
            for (String txId : txIds) {
                TransactionStatus status = transactionManager.getTransactionStatus(txId);
                Assertions.assertEquals(TransactionStatus.COMMITTED, status,
                        "All concurrent transactions should have been committed successfully.");
            }
        }
    }

    @Test
    public void testIdempotentCommit() throws Exception {
        // Create services that succeed.
        MockService serviceA = new MockService("ServiceA", true, true, true, 0);
        transactionManager.registerService(serviceA);

        String txId = transactionManager.beginTransaction();
        transactionManager.addOperation(txId, createOperation(serviceA.getName(), "opA", "dataA"));

        // Execute the transaction normally.
        transactionManager.executeTransaction(txId);

        // Simulate calling executeTransaction a second time on the same transaction.
        // It should handle idempotency by not re-triggering operations.
        transactionManager.executeTransaction(txId);

        Assertions.assertEquals(TransactionStatus.COMMITTED, transactionManager.getTransactionStatus(txId),
                "Transaction should remain committed on repeated execution.");
        Assertions.assertTrue(serviceA.isPrepareCalled(), "ServiceA should have been prepared.");
        Assertions.assertTrue(serviceA.isCommitCalled(), "ServiceA should have been committed once, idempotently.");
    }
}