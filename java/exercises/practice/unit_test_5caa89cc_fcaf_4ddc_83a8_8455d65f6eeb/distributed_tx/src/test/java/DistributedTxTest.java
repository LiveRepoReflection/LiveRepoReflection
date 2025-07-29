import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.UUID;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;

import static org.junit.jupiter.api.Assertions.*;

public class DistributedTxTest {

    private TransactionManager txManager;

    @BeforeEach
    public void setup() {
        txManager = new TransactionManager();
    }

    @Test
    public void testBasicSuccessfulTransaction() throws Exception {
        String txId = txManager.startTransaction();
        
        TestParticipant p1 = new TestParticipant("p1", true, true);
        TestParticipant p2 = new TestParticipant("p2", true, true);
        
        txManager.registerParticipant(txId, p1);
        txManager.registerParticipant(txId, p2);
        
        boolean result = txManager.executeTransaction(txId);
        
        assertTrue(result);
        assertTrue(p1.isPrepared());
        assertTrue(p1.isCommitted());
        assertFalse(p1.isRolledBack());
        
        assertTrue(p2.isPrepared());
        assertTrue(p2.isCommitted());
        assertFalse(p2.isRolledBack());
    }

    @Test
    public void testTransactionRollbackOnPrepareFailure() throws Exception {
        String txId = txManager.startTransaction();
        
        TestParticipant p1 = new TestParticipant("p1", true, true);
        TestParticipant p2 = new TestParticipant("p2", false, true); // p2 will fail on prepare
        
        txManager.registerParticipant(txId, p1);
        txManager.registerParticipant(txId, p2);
        
        boolean result = txManager.executeTransaction(txId);
        
        assertFalse(result);
        assertTrue(p1.isPrepared());
        assertFalse(p1.isCommitted());
        assertTrue(p1.isRolledBack());
        
        assertTrue(p2.isPrepared());
        assertFalse(p2.isCommitted());
        assertTrue(p2.isRolledBack());
    }

    @Test
    public void testConcurrentTransactions() throws Exception {
        int numTransactions = 10;
        CountDownLatch latch = new CountDownLatch(numTransactions);
        ExecutorService executor = Executors.newFixedThreadPool(5);
        AtomicInteger successCount = new AtomicInteger(0);
        
        for (int i = 0; i < numTransactions; i++) {
            final int index = i;
            executor.submit(() -> {
                try {
                    String txId = txManager.startTransaction();
                    
                    TestParticipant p1 = new TestParticipant("p1-tx" + index, true, true);
                    TestParticipant p2 = new TestParticipant("p2-tx" + index, true, true);
                    
                    txManager.registerParticipant(txId, p1);
                    txManager.registerParticipant(txId, p2);
                    
                    boolean success = txManager.executeTransaction(txId);
                    if (success) {
                        successCount.incrementAndGet();
                    }
                } catch (Exception e) {
                    e.printStackTrace();
                } finally {
                    latch.countDown();
                }
            });
        }
        
        latch.await(10, TimeUnit.SECONDS);
        executor.shutdown();
        
        assertEquals(numTransactions, successCount.get());
    }

    @Test
    public void testTransactionWithTimeout() throws Exception {
        String txId = txManager.startTransaction();
        
        TestParticipant p1 = new TestParticipant("p1", true, true);
        SlowParticipant p2 = new SlowParticipant("p2-slow", 2000); // Takes 2 seconds to prepare
        
        txManager.registerParticipant(txId, p1);
        txManager.registerParticipant(txId, p2);
        
        // Set timeout to 1 second, which should cause p2 to timeout
        txManager.setTimeout(1000);
        
        boolean result = txManager.executeTransaction(txId);
        
        assertFalse(result);
        assertTrue(p1.isPrepared());
        assertTrue(p1.isRolledBack());
        assertFalse(p1.isCommitted());
    }

    @Test
    public void testIdempotentCommitAndRollback() throws Exception {
        String txId = txManager.startTransaction();
        
        IdempotencyTestParticipant p = new IdempotencyTestParticipant("p-idempotent");
        
        txManager.registerParticipant(txId, p);
        
        boolean result = txManager.executeTransaction(txId);
        
        assertTrue(result);
        assertEquals(1, p.getPrepareCallCount());
        assertEquals(1, p.getCommitCallCount());
        assertEquals(0, p.getRollbackCallCount());
        
        // Manually call commit again to test idempotence
        p.commit();
        assertEquals(1, p.getCommitCallCount());

        // Create a failing transaction to test rollback idempotence
        txId = txManager.startTransaction();
        IdempotencyTestParticipant p2 = new IdempotencyTestParticipant("p2-idempotent", false);
        txManager.registerParticipant(txId, p2);
        result = txManager.executeTransaction(txId);
        
        assertFalse(result);
        assertEquals(1, p2.getPrepareCallCount());
        assertEquals(0, p2.getCommitCallCount());
        assertEquals(1, p2.getRollbackCallCount());
        
        // Manually call rollback again to test idempotence
        p2.rollback();
        assertEquals(1, p2.getRollbackCallCount());
    }
    
    @Test
    public void testNonExistingTransaction() {
        String invalidTxId = UUID.randomUUID().toString();
        Exception exception = assertThrows(IllegalArgumentException.class, () -> {
            txManager.executeTransaction(invalidTxId);
        });
        
        assertTrue(exception.getMessage().contains("Transaction not found"));
    }

    @Test
    public void testTransactionCompletionCleanup() throws Exception {
        String txId = txManager.startTransaction();
        
        TestParticipant p1 = new TestParticipant("p1", true, true);
        txManager.registerParticipant(txId, p1);
        
        txManager.executeTransaction(txId);
        
        // Try to execute the same transaction again - should fail because it's been completed and removed
        Exception exception = assertThrows(IllegalArgumentException.class, () -> {
            txManager.executeTransaction(txId);
        });
        
        assertTrue(exception.getMessage().contains("Transaction not found"));
    }

    @Test
    public void testParticipantRegistrationAfterExecution() throws Exception {
        String txId = txManager.startTransaction();
        
        TestParticipant p1 = new TestParticipant("p1", true, true);
        txManager.registerParticipant(txId, p1);
        
        txManager.executeTransaction(txId);
        
        // Try to register a participant to a completed transaction
        TestParticipant p2 = new TestParticipant("p2", true, true);
        Exception exception = assertThrows(IllegalArgumentException.class, () -> {
            txManager.registerParticipant(txId, p2);
        });
        
        assertTrue(exception.getMessage().contains("Transaction not found"));
    }

    // Helper test classes
    
    private static class TestParticipant implements Participant {
        private final String name;
        private final boolean prepareSuccess;
        private final boolean commitSuccess;
        private boolean prepared = false;
        private boolean committed = false;
        private boolean rolledBack = false;
        
        public TestParticipant(String name, boolean prepareSuccess, boolean commitSuccess) {
            this.name = name;
            this.prepareSuccess = prepareSuccess;
            this.commitSuccess = commitSuccess;
        }
        
        @Override
        public boolean prepare() {
            prepared = true;
            return prepareSuccess;
        }
        
        @Override
        public void commit() {
            if (!prepared) {
                throw new IllegalStateException("Cannot commit without preparing first");
            }
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
        
        @Override
        public String toString() {
            return "TestParticipant[" + name + "]";
        }
    }
    
    private static class SlowParticipant implements Participant {
        private final String name;
        private final long delayMs;
        private boolean rolledBack = false;
        
        public SlowParticipant(String name, long delayMs) {
            this.name = name;
            this.delayMs = delayMs;
        }
        
        @Override
        public boolean prepare() {
            try {
                Thread.sleep(delayMs);
                return true;
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return false;
            }
        }
        
        @Override
        public void commit() {
            // No-op for test purposes
        }
        
        @Override
        public void rollback() {
            rolledBack = true;
        }
        
        public boolean isRolledBack() {
            return rolledBack;
        }
        
        @Override
        public String toString() {
            return "SlowParticipant[" + name + "]";
        }
    }
    
    private static class IdempotencyTestParticipant implements Participant {
        private final String name;
        private final boolean prepareSuccess;
        private final AtomicInteger prepareCallCount = new AtomicInteger(0);
        private final AtomicInteger commitCallCount = new AtomicInteger(0);
        private final AtomicInteger rollbackCallCount = new AtomicInteger(0);
        private final AtomicBoolean prepared = new AtomicBoolean(false);
        
        public IdempotencyTestParticipant(String name) {
            this(name, true);
        }
        
        public IdempotencyTestParticipant(String name, boolean prepareSuccess) {
            this.name = name;
            this.prepareSuccess = prepareSuccess;
        }
        
        @Override
        public boolean prepare() {
            prepareCallCount.incrementAndGet();
            prepared.set(true);
            return prepareSuccess;
        }
        
        @Override
        public void commit() {
            if (prepared.get() && commitCallCount.get() == 0) {
                commitCallCount.incrementAndGet();
            }
        }
        
        @Override
        public void rollback() {
            if (rollbackCallCount.get() == 0) {
                rollbackCallCount.incrementAndGet();
            }
        }
        
        public int getPrepareCallCount() {
            return prepareCallCount.get();
        }
        
        public int getCommitCallCount() {
            return commitCallCount.get();
        }
        
        public int getRollbackCallCount() {
            return rollbackCallCount.get();
        }
        
        @Override
        public String toString() {
            return "IdempotencyTestParticipant[" + name + "]";
        }
    }
}