import org.junit.Test;
import org.junit.Before;
import org.junit.After;
import static org.junit.Assert.*;

import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class DistributedTxTest {

    private DistributedTransactionCoordinator dtc;

    @Before
    public void setUp() {
        dtc = new DistributedTransactionCoordinator();
    }

    @After
    public void tearDown() {
        dtc.shutdown();
    }

    // A simple mock implementation for a transaction participant.
    // Each participant supports prepare, commit, and rollback operations.
    private static class MockParticipant implements TransactionParticipant {
        private final boolean prepareResult;
        private boolean committed = false;
        private boolean rolledBack = false;
        private final long delayMillis; // delay for simulating timeout or latency
        private final boolean throwExceptionOnPrepare;

        public MockParticipant(boolean prepareResult, long delayMillis, boolean throwExceptionOnPrepare) {
            this.prepareResult = prepareResult;
            this.delayMillis = delayMillis;
            this.throwExceptionOnPrepare = throwExceptionOnPrepare;
        }

        public MockParticipant(boolean prepareResult) {
            this(prepareResult, 0, false);
        }

        @Override
        public boolean prepare() throws Exception {
            if (delayMillis > 0) {
                Thread.sleep(delayMillis);
            }
            if (throwExceptionOnPrepare) {
                throw new Exception("Prepare Exception");
            }
            return prepareResult;
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

    @Test
    public void testSuccessfulCommit() throws Exception {
        // Test a transaction where all participants succeed in their prepare phase
        String txId = dtc.beginTransaction();
        MockParticipant participant1 = new MockParticipant(true);
        MockParticipant participant2 = new MockParticipant(true);
        MockParticipant participant3 = new MockParticipant(true);

        dtc.registerParticipant(txId, participant1);
        dtc.registerParticipant(txId, participant2);
        dtc.registerParticipant(txId, participant3);

        boolean result = dtc.executeTransaction(txId);
        assertTrue("Transaction should commit successfully", result);
        assertTrue(participant1.isCommitted());
        assertTrue(participant2.isCommitted());
        assertTrue(participant3.isCommitted());
        assertFalse(participant1.isRolledBack());
        assertFalse(participant2.isRolledBack());
        assertFalse(participant3.isRolledBack());
    }

    @Test
    public void testRollbackOnPrepareFailure() throws Exception {
        // Test a transaction where one participant fails during the prepare phase
        String txId = dtc.beginTransaction();
        MockParticipant participant1 = new MockParticipant(true);
        MockParticipant participant2 = new MockParticipant(false);  // fails prepare
        MockParticipant participant3 = new MockParticipant(true);

        dtc.registerParticipant(txId, participant1);
        dtc.registerParticipant(txId, participant2);
        dtc.registerParticipant(txId, participant3);

        boolean result = dtc.executeTransaction(txId);
        assertFalse("Transaction should rollback due to prepare failure", result);
        assertTrue(participant1.isRolledBack());
        assertTrue(participant2.isRolledBack());
        assertTrue(participant3.isRolledBack());
        assertFalse(participant1.isCommitted());
        assertFalse(participant2.isCommitted());
        assertFalse(participant3.isCommitted());
    }

    @Test
    public void testRollbackOnExceptionDuringPrepare() throws Exception {
        // Test a transaction where one participant throws an exception during prepare
        String txId = dtc.beginTransaction();
        MockParticipant participant1 = new MockParticipant(true);
        MockParticipant participant2 = new MockParticipant(true, 0, true); // throws exception
        MockParticipant participant3 = new MockParticipant(true);

        dtc.registerParticipant(txId, participant1);
        dtc.registerParticipant(txId, participant2);
        dtc.registerParticipant(txId, participant3);

        boolean result = dtc.executeTransaction(txId);
        assertFalse("Transaction should rollback due to exception in prepare", result);
        assertTrue(participant1.isRolledBack());
        assertTrue(participant2.isRolledBack());
        assertTrue(participant3.isRolledBack());
    }

    @Test
    public void testTimeoutDuringPrepare() throws Exception {
        // Test a transaction where one participant delays beyond the timeout threshold.
        // Assuming the coordinator timeout is lower than 1500ms.
        String txId = dtc.beginTransaction();
        MockParticipant participant1 = new MockParticipant(true);
        // This participant will delay, causing a timeout.
        MockParticipant participant2 = new MockParticipant(true, 1500, false);
        MockParticipant participant3 = new MockParticipant(true);

        dtc.registerParticipant(txId, participant1);
        dtc.registerParticipant(txId, participant2);
        dtc.registerParticipant(txId, participant3);

        boolean result = dtc.executeTransaction(txId);
        assertFalse("Transaction should rollback due to timeout", result);
        assertTrue(participant1.isRolledBack());
        assertTrue(participant2.isRolledBack());
        assertTrue(participant3.isRolledBack());
    }

    @Test
    public void testConcurrentTransactions() throws Exception {
        // Test concurrent execution of multiple transactions to ensure thread safety.
        final int numTransactions = 10;
        final ExecutorService executor = Executors.newFixedThreadPool(numTransactions);
        final CountDownLatch latch = new CountDownLatch(numTransactions);
        final boolean[] results = new boolean[numTransactions];

        for (int i = 0; i < numTransactions; i++) {
            final int idx = i;
            executor.submit(() -> {
                try {
                    String txId = dtc.beginTransaction();
                    // For even transactions, simulate success; for odd, simulate prepare failure.
                    if (idx % 2 == 0) {
                        dtc.registerParticipant(txId, new MockParticipant(true));
                        dtc.registerParticipant(txId, new MockParticipant(true));
                    } else {
                        dtc.registerParticipant(txId, new MockParticipant(true));
                        dtc.registerParticipant(txId, new MockParticipant(false));
                    }
                    results[idx] = dtc.executeTransaction(txId);
                } catch (Exception e) {
                    results[idx] = false;
                } finally {
                    latch.countDown();
                }
            });
        }
        latch.await(5, TimeUnit.SECONDS);
        executor.shutdownNow();

        for (int i = 0; i < numTransactions; i++) {
            if (i % 2 == 0) {
                assertTrue("Transaction " + i + " should commit successfully", results[i]);
            } else {
                assertFalse("Transaction " + i + " should rollback due to failure", results[i]);
            }
        }
    }
}