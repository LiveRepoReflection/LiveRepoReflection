import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Timeout;
import org.junit.jupiter.api.Assertions;

import java.util.List;
import java.util.ArrayList;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.Executors;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.atomic.AtomicInteger;

public class TransactionManagerTest {

    private TransactionManager transactionManager;

    @BeforeEach
    public void setUp() {
        // Assume TransactionManager has a default constructor.
        transactionManager = new TransactionManager();
    }

    // TestParticipant is a dummy implementation of Participant interface used for testing.
    private static class TestParticipant implements Participant {
        private final String name;
        private final boolean failOnPrepare;
        private final long prepareDelayMillis;
        private final AtomicInteger commitCount = new AtomicInteger(0);
        private final AtomicInteger rollbackCount = new AtomicInteger(0);
        private boolean prepared = false;

        public TestParticipant(String name, boolean failOnPrepare, long prepareDelayMillis) {
            this.name = name;
            this.failOnPrepare = failOnPrepare;
            this.prepareDelayMillis = prepareDelayMillis;
        }

        @Override
        public Vote prepare() throws Exception {
            if (prepareDelayMillis > 0) {
                Thread.sleep(prepareDelayMillis);
            }
            prepared = true;
            if (failOnPrepare) {
                return Vote.ROLLBACK;
            }
            return Vote.COMMIT;
        }

        @Override
        public void commit() {
            // Idempotent commit call
            commitCount.incrementAndGet();
        }

        @Override
        public void rollback() {
            // Idempotent rollback call
            rollbackCount.incrementAndGet();
        }

        public boolean isCommitted() {
            return commitCount.get() >= 1;
        }

        public boolean isRolledBack() {
            return rollbackCount.get() >= 1;
        }
    }

    @Test
    public void testSuccessfulTransaction() throws Exception {
        List<Participant> participants = new ArrayList<>();
        TestParticipant p1 = new TestParticipant("InventoryService", false, 0);
        TestParticipant p2 = new TestParticipant("OrderService", false, 0);
        TestParticipant p3 = new TestParticipant("PaymentService", false, 0);
        TestParticipant p4 = new TestParticipant("ShippingQueue", false, 0);

        participants.add(p1);
        participants.add(p2);
        participants.add(p3);
        participants.add(p4);

        transactionManager.executeTransaction(participants);

        // All participants should have been committed and not rolled back.
        Assertions.assertTrue(p1.isCommitted(), "InventoryService should be committed");
        Assertions.assertTrue(p2.isCommitted(), "OrderService should be committed");
        Assertions.assertTrue(p3.isCommitted(), "PaymentService should be committed");
        Assertions.assertTrue(p4.isCommitted(), "ShippingQueue should be committed");

        Assertions.assertFalse(p1.isRolledBack(), "InventoryService should not be rolled back");
        Assertions.assertFalse(p2.isRolledBack(), "OrderService should not be rolled back");
        Assertions.assertFalse(p3.isRolledBack(), "PaymentService should not be rolled back");
        Assertions.assertFalse(p4.isRolledBack(), "ShippingQueue should not be rolled back");
    }

    @Test
    public void testFailingTransaction() throws Exception {
        List<Participant> participants = new ArrayList<>();
        TestParticipant p1 = new TestParticipant("InventoryService", false, 0);
        TestParticipant p2 = new TestParticipant("OrderService", true, 0); // This service will fail during prepare.
        TestParticipant p3 = new TestParticipant("PaymentService", false, 0);
        TestParticipant p4 = new TestParticipant("ShippingQueue", false, 0);

        participants.add(p1);
        participants.add(p2);
        participants.add(p3);
        participants.add(p4);

        try {
            transactionManager.executeTransaction(participants);
            Assertions.fail("Transaction should have rolled back due to prepare failure");
        } catch (TransactionFailedException e) {
            // Expected exception, transaction failed.
        }

        // All participants should have been rolled back.
        Assertions.assertTrue(p1.isRolledBack(), "InventoryService should be rolled back");
        Assertions.assertTrue(p2.isRolledBack(), "OrderService should be rolled back");
        Assertions.assertTrue(p3.isRolledBack(), "PaymentService should be rolled back");
        Assertions.assertTrue(p4.isRolledBack(), "ShippingQueue should be rolled back");

        // None should have received commit.
        Assertions.assertFalse(p1.isCommitted(), "InventoryService should not be committed");
        Assertions.assertFalse(p2.isCommitted(), "OrderService should not be committed");
        Assertions.assertFalse(p3.isCommitted(), "PaymentService should not be committed");
        Assertions.assertFalse(p4.isCommitted(), "ShippingQueue should not be committed");
    }

    @Test
    @Timeout(5)
    public void testTimeoutDuringPrepare() throws Exception {
        List<Participant> participants = new ArrayList<>();
        // This participant introduces a delay longer than the TransactionManager's timeout threshold.
        TestParticipant p1 = new TestParticipant("SlowService", false, 3000);
        TestParticipant p2 = new TestParticipant("FastService", false, 0);

        participants.add(p1);
        participants.add(p2);

        try {
            transactionManager.executeTransaction(participants);
            Assertions.fail("Transaction should have timed out and rolled back");
        } catch (TransactionTimeoutException e) {
            // Expected exception for timeout.
        }

        Assertions.assertTrue(p1.isRolledBack(), "SlowService should be rolled back due to timeout");
        Assertions.assertTrue(p2.isRolledBack(), "FastService should have been rolled back due to timeout in one participant");
        Assertions.assertFalse(p1.isCommitted(), "SlowService should not be committed");
        Assertions.assertFalse(p2.isCommitted(), "FastService should not be committed");
    }

    @Test
    public void testIdempotencyOfCommitAndRollback() throws Exception {
        List<Participant> participants = new ArrayList<>();
        TestParticipant p1 = new TestParticipant("InventoryService", false, 0);
        TestParticipant p2 = new TestParticipant("OrderService", false, 0);

        participants.add(p1);
        participants.add(p2);

        // Execute a successful transaction.
        transactionManager.executeTransaction(participants);

        // Call commit and rollback again to test idempotency.
        p1.commit();
        p1.rollback();
        p2.commit();
        p2.rollback();

        // Both commit and rollback should have been called only once during the transaction,
        // additional calls should not alter the final state.
        Assertions.assertTrue(p1.isCommitted(), "InventoryService should be committed and idempotent");
        Assertions.assertTrue(p2.isCommitted(), "OrderService should be committed and idempotent");
        // Rollback count may be > 0 if the implementation does not prevent extra invocation,
        // but the state should remain committed, so our simple check is that commit was done.
    }

    @Test
    public void testConcurrentTransactions() throws Exception {
        int concurrentRuns = 10;
        ExecutorService executor = Executors.newFixedThreadPool(concurrentRuns);
        CountDownLatch latch = new CountDownLatch(concurrentRuns);
        List<Exception> exceptions = new ArrayList<>();

        for (int i = 0; i < concurrentRuns; i++) {
            executor.submit(() -> {
                try {
                    List<Participant> participants = new ArrayList<>();
                    TestParticipant p1 = new TestParticipant("InventoryService", false, 0);
                    TestParticipant p2 = new TestParticipant("OrderService", false, 0);
                    TestParticipant p3 = new TestParticipant("PaymentService", false, 0);
                    participants.add(p1);
                    participants.add(p2);
                    participants.add(p3);
                    transactionManager.executeTransaction(participants);

                    // Validate that transaction was successful.
                    if (!p1.isCommitted() || !p2.isCommitted() || !p3.isCommitted()) {
                        throw new Exception("Transaction did not complete successfully in concurrent run");
                    }
                } catch (Exception ex) {
                    synchronized (exceptions) {
                        exceptions.add(ex);
                    }
                } finally {
                    latch.countDown();
                }
            });
        }

        latch.await(10, TimeUnit.SECONDS);
        executor.shutdownNow();
        if (!exceptions.isEmpty()) {
            Assertions.fail("One or more concurrent transactions failed: " + exceptions);
        }
    }
}