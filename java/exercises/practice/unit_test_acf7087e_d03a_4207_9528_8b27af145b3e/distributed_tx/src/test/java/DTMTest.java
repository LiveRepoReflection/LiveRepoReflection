import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;

import static org.junit.jupiter.api.Assertions.*;

public class DTMTest {

    private DTM dtm;

    @BeforeEach
    public void setUp() {
        dtm = new DTM();
    }

    @Test
    public void testSuccessfulTransaction() {
        String txId = dtm.begin();
        MockParticipant p1 = new MockParticipant("service1", true, true);
        MockParticipant p2 = new MockParticipant("service2", true, true);
        MockParticipant p3 = new MockParticipant("service3", true, true);

        dtm.enlist(txId, p1);
        dtm.enlist(txId, p2);
        dtm.enlist(txId, p3);

        boolean success = dtm.commit(txId);

        assertTrue(success, "Transaction should commit successfully");
        assertTrue(p1.isPrepared(), "Participant 1 should be prepared");
        assertTrue(p2.isPrepared(), "Participant 2 should be prepared");
        assertTrue(p3.isPrepared(), "Participant 3 should be prepared");
        assertTrue(p1.isCommitted(), "Participant 1 should be committed");
        assertTrue(p2.isCommitted(), "Participant 2 should be committed");
        assertTrue(p3.isCommitted(), "Participant 3 should be committed");
        assertFalse(p1.isRolledBack(), "Participant 1 should not be rolled back");
        assertFalse(p2.isRolledBack(), "Participant 2 should not be rolled back");
        assertFalse(p3.isRolledBack(), "Participant 3 should not be rolled back");
    }

    @Test
    public void testFailedPreparationLeadsToRollback() {
        String txId = dtm.begin();
        MockParticipant p1 = new MockParticipant("service1", true, true);
        MockParticipant p2 = new MockParticipant("service2", false, true); // Will fail in prepare phase
        MockParticipant p3 = new MockParticipant("service3", true, true);

        dtm.enlist(txId, p1);
        dtm.enlist(txId, p2);
        dtm.enlist(txId, p3);

        boolean success = dtm.commit(txId);

        assertFalse(success, "Transaction should not commit");
        assertTrue(p1.isPrepared(), "Participant 1 should be prepared");
        assertFalse(p2.isPrepared(), "Participant 2 should not be prepared");
        assertTrue(p3.isPrepared(), "Participant 3 should be prepared");
        assertFalse(p1.isCommitted(), "Participant 1 should not be committed");
        assertFalse(p2.isCommitted(), "Participant 2 should not be committed");
        assertFalse(p3.isCommitted(), "Participant 3 should not be committed");
        assertTrue(p1.isRolledBack(), "Participant 1 should be rolled back");
        assertTrue(p2.isRolledBack(), "Participant 2 should be rolled back");
        assertTrue(p3.isRolledBack(), "Participant 3 should be rolled back");
    }

    @Test
    public void testExplicitRollback() {
        String txId = dtm.begin();
        MockParticipant p1 = new MockParticipant("service1", true, true);
        MockParticipant p2 = new MockParticipant("service2", true, true);

        dtm.enlist(txId, p1);
        dtm.enlist(txId, p2);

        dtm.rollback(txId);

        assertFalse(p1.isPrepared(), "Participant 1 should not be prepared");
        assertFalse(p2.isPrepared(), "Participant 2 should not be prepared");
        assertFalse(p1.isCommitted(), "Participant 1 should not be committed");
        assertFalse(p2.isCommitted(), "Participant 2 should not be committed");
        assertTrue(p1.isRolledBack(), "Participant 1 should be rolled back");
        assertTrue(p2.isRolledBack(), "Participant 2 should be rolled back");
    }

    @Test
    public void testParticipantTimeout() {
        String txId = dtm.begin();
        MockParticipant p1 = new MockParticipant("service1", true, true);
        TimingOutParticipant p2 = new TimingOutParticipant("service2");
        MockParticipant p3 = new MockParticipant("service3", true, true);

        dtm.enlist(txId, p1);
        dtm.enlist(txId, p2);
        dtm.enlist(txId, p3);

        boolean success = dtm.commit(txId);

        assertFalse(success, "Transaction should not commit due to timeout");
        assertTrue(p1.isRolledBack(), "Participant 1 should be rolled back");
        assertTrue(p3.isRolledBack(), "Participant 3 should be rolled back");
    }

    @Test
    @Timeout(value = 10, unit = TimeUnit.SECONDS)
    public void testConcurrentTransactions() throws InterruptedException {
        final int numTransactions = 100;
        final int numParticipantsPerTx = 5;
        final CountDownLatch latch = new CountDownLatch(numTransactions);
        final AtomicInteger successCount = new AtomicInteger(0);
        
        List<Thread> threads = new ArrayList<>();
        
        for (int i = 0; i < numTransactions; i++) {
            final int txNum = i;
            Thread t = new Thread(() -> {
                try {
                    String txId = dtm.begin();
                    
                    // Every 10th transaction will fail
                    boolean shouldFail = txNum % 10 == 0;
                    
                    for (int j = 0; j < numParticipantsPerTx; j++) {
                        // One participant will fail in the failing transactions
                        boolean participantWillFail = shouldFail && j == 0;
                        MockParticipant p = new MockParticipant(
                                "service" + txNum + "-" + j, 
                                !participantWillFail, 
                                true);
                        dtm.enlist(txId, p);
                    }
                    
                    boolean success = dtm.commit(txId);
                    if (success) {
                        successCount.incrementAndGet();
                    }
                } finally {
                    latch.countDown();
                }
            });
            threads.add(t);
            t.start();
        }
        
        // Wait for all transactions to complete
        latch.await();
        
        // 90% of transactions should succeed (every 10th fails)
        assertEquals(90, successCount.get(), "90% of transactions should succeed");
    }

    @Test
    public void testTransactionIdUniqueness() {
        final int numTransactions = 1000;
        List<String> transactionIds = new ArrayList<>();
        
        for (int i = 0; i < numTransactions; i++) {
            transactionIds.add(dtm.begin());
        }
        
        // Check that all IDs are unique
        long uniqueCount = transactionIds.stream().distinct().count();
        assertEquals(numTransactions, uniqueCount, "All transaction IDs should be unique");
    }

    @Test
    public void testIdempotentCommit() {
        String txId = dtm.begin();
        IdempotencyCheckingParticipant p1 = new IdempotencyCheckingParticipant("service1");
        
        dtm.enlist(txId, p1);
        
        // First commit
        boolean success1 = dtm.commit(txId);
        assertTrue(success1, "First commit should succeed");
        assertEquals(1, p1.getPrepareCount(), "prepare() should be called once");
        assertEquals(1, p1.getCommitCount(), "commit() should be called once");
        
        // Second commit of the same transaction (testing idempotency)
        boolean success2 = dtm.commit(txId);
        assertTrue(success2, "Second commit should succeed (idempotent)");
        
        // Check if the methods were called again (they shouldn't be for idempotency)
        assertEquals(1, p1.getPrepareCount(), "prepare() should still be called only once");
        assertEquals(1, p1.getCommitCount(), "commit() should still be called only once");
    }

    @Test
    public void testIdempotentRollback() {
        String txId = dtm.begin();
        IdempotencyCheckingParticipant p1 = new IdempotencyCheckingParticipant("service1");
        
        dtm.enlist(txId, p1);
        
        // First rollback
        dtm.rollback(txId);
        assertEquals(1, p1.getRollbackCount(), "rollback() should be called once");
        
        // Second rollback of the same transaction (testing idempotency)
        dtm.rollback(txId);
        
        // Check if rollback was called again (it shouldn't be for idempotency)
        assertEquals(1, p1.getRollbackCount(), "rollback() should still be called only once");
    }

    // Represents a participant in the distributed transaction
    private static class MockParticipant implements Participant {
        private final String name;
        private final boolean willPrepareSuccessfully;
        private final boolean willCommitSuccessfully;
        private boolean prepared = false;
        private boolean committed = false;
        private boolean rolledBack = false;

        public MockParticipant(String name, boolean willPrepareSuccessfully, boolean willCommitSuccessfully) {
            this.name = name;
            this.willPrepareSuccessfully = willPrepareSuccessfully;
            this.willCommitSuccessfully = willCommitSuccessfully;
        }

        @Override
        public boolean prepare(String transactionId) {
            if (willPrepareSuccessfully) {
                prepared = true;
                return true;
            }
            return false;
        }

        @Override
        public boolean commit(String transactionId) {
            if (!prepared) {
                return false;
            }
            if (willCommitSuccessfully) {
                committed = true;
                return true;
            }
            return false;
        }

        @Override
        public boolean rollback(String transactionId) {
            rolledBack = true;
            return true;
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

        @Override
        public String toString() {
            return "MockParticipant[" + name + "]";
        }
    }

    // A participant that simulates a timeout during prepare
    private static class TimingOutParticipant implements Participant {
        private final String name;
        private boolean rolledBack = false;

        public TimingOutParticipant(String name) {
            this.name = name;
        }

        @Override
        public boolean prepare(String transactionId) {
            try {
                // Simulate a long operation that will time out
                Thread.sleep(10000);
            } catch (InterruptedException e) {
                // Ignore
            }
            return false;
        }

        @Override
        public boolean commit(String transactionId) {
            return false;
        }

        @Override
        public boolean rollback(String transactionId) {
            rolledBack = true;
            return true;
        }

        public boolean isRolledBack() {
            return rolledBack;
        }

        @Override
        public String toString() {
            return "TimingOutParticipant[" + name + "]";
        }
    }

    // A participant that counts method calls to check for idempotency
    private static class IdempotencyCheckingParticipant implements Participant {
        private final String name;
        private final AtomicInteger prepareCount = new AtomicInteger(0);
        private final AtomicInteger commitCount = new AtomicInteger(0);
        private final AtomicInteger rollbackCount = new AtomicInteger(0);
        private final AtomicBoolean prepareResult = new AtomicBoolean(true);

        public IdempotencyCheckingParticipant(String name) {
            this.name = name;
        }

        @Override
        public boolean prepare(String transactionId) {
            prepareCount.incrementAndGet();
            return prepareResult.get();
        }

        @Override
        public boolean commit(String transactionId) {
            commitCount.incrementAndGet();
            return true;
        }

        @Override
        public boolean rollback(String transactionId) {
            rollbackCount.incrementAndGet();
            return true;
        }

        public int getPrepareCount() {
            return prepareCount.get();
        }

        public int getCommitCount() {
            return commitCount.get();
        }

        public int getRollbackCount() {
            return rollbackCount.get();
        }

        @Override
        public String toString() {
            return "IdempotencyCheckingParticipant[" + name + "]";
        }
    }
}