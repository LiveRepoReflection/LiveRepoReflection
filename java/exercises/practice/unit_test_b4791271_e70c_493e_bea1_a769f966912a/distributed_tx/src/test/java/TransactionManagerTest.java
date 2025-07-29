package distributed_tx;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.ArrayList;
import java.util.List;

public class TransactionManagerTest {

    // A mock implementation of the TransactionParticipant interface.
    // It records the number of times each method is called and can simulate failures and delays.
    private static class TestParticipant implements TransactionParticipant {
        private final String name;
        private volatile boolean prepared = false;
        private volatile boolean committed = false;
        private volatile boolean rolledBack = false;
        private final boolean failPrepare;
        private final long prepareDelay; // in milliseconds
        private final AtomicInteger prepareCount = new AtomicInteger(0);
        private final AtomicInteger commitCount = new AtomicInteger(0);
        private final AtomicInteger rollbackCount = new AtomicInteger(0);

        public TestParticipant(String name, boolean failPrepare, long prepareDelay) {
            this.name = name;
            this.failPrepare = failPrepare;
            this.prepareDelay = prepareDelay;
        }

        @Override
        public boolean prepare() throws Exception {
            Thread.sleep(prepareDelay);
            prepareCount.incrementAndGet();
            if (failPrepare) {
                throw new Exception("Prepare failed for " + name);
            }
            prepared = true;
            return true;
        }

        @Override
        public void commit() throws Exception {
            commitCount.incrementAndGet();
            if (!committed) {
                committed = true;
            }
        }

        @Override
        public void rollback() throws Exception {
            rollbackCount.incrementAndGet();
            if (!rolledBack) {
                rolledBack = true;
            }
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

        public int getPrepareCount() {
            return prepareCount.get();
        }

        public int getCommitCount() {
            return commitCount.get();
        }

        public int getRollbackCount() {
            return rollbackCount.get();
        }
    }

    // Helper method to create a TransactionManager with a specified timeout (in milliseconds)
    private TransactionManager createTransactionManager(long timeoutMs) {
        TransactionManager tm = new TransactionManager();
        tm.setTimeout(timeoutMs);
        return tm;
    }

    @Test
    public void testSuccessfulTransaction() throws Exception {
        TransactionManager tm = createTransactionManager(5000); // 5 second timeout
        TestParticipant participant1 = new TestParticipant("P1", false, 100);
        TestParticipant participant2 = new TestParticipant("P2", false, 100);

        tm.registerParticipant(participant1);
        tm.registerParticipant(participant2);

        boolean result = tm.executeTransaction();
        assertTrue(result, "Transaction should commit successfully");

        assertTrue(participant1.isCommitted(), "Participant1 should be committed");
        assertFalse(participant1.isRolledBack(), "Participant1 should not be rolled back");

        assertTrue(participant2.isCommitted(), "Participant2 should be committed");
        assertFalse(participant2.isRolledBack(), "Participant2 should not be rolled back");
    }

    @Test
    public void testFailedTransactionDueToPrepareFailure() throws Exception {
        TransactionManager tm = createTransactionManager(5000); // 5 second timeout
        TestParticipant participant1 = new TestParticipant("P1", false, 100);
        TestParticipant participant2 = new TestParticipant("P2", true, 100);  // This participant will fail during prepare.
        TestParticipant participant3 = new TestParticipant("P3", false, 100);

        tm.registerParticipant(participant1);
        tm.registerParticipant(participant2);
        tm.registerParticipant(participant3);

        boolean result = tm.executeTransaction();
        assertFalse(result, "Transaction should rollback due to prepare failure");

        // Every participant should be rolled back in case of prepare failure.
        assertTrue(participant1.isRolledBack(), "Participant1 should be rolled back");
        assertTrue(participant2.isRolledBack(), "Participant2 should be rolled back");
        assertTrue(participant3.isRolledBack(), "Participant3 should be rolled back");
    }

    @Test
    public void testTransactionTimeoutLeadingToRollback() throws Exception {
        // Create a TransactionManager with a timeout shorter than the participant's prepare delay.
        TransactionManager tm = createTransactionManager(200); // 200 ms timeout
        TestParticipant participant1 = new TestParticipant("P1", false, 300); // Delay exceeds timeout

        tm.registerParticipant(participant1);

        boolean result = tm.executeTransaction();
        // Expect a rollback because the participant's prepare takes too long.
        assertFalse(result, "Transaction should rollback due to timeout");

        assertTrue(participant1.isRolledBack(), "Participant1 should be rolled back due to timeout");
    }

    @Test
    public void testIdempotentCommitRollback() throws Exception {
        // First, execute a successful transaction.
        TransactionManager tm1 = createTransactionManager(5000);
        TestParticipant participant = new TestParticipant("P", false, 100);
        tm1.registerParticipant(participant);
        boolean result1 = tm1.executeTransaction();
        assertTrue(result1, "Transaction should commit successfully");
        int initialCommitCount = participant.getCommitCount();

        // Manually invoke commit again to test idempotency.
        participant.commit();
        assertEquals(initialCommitCount, participant.getCommitCount() - 1, "Commit should be idempotent");

        // Now, execute a transaction that fails and triggers a rollback.
        TransactionManager tm2 = createTransactionManager(5000);
        TestParticipant participantFail = new TestParticipant("PF", true, 100);
        tm2.registerParticipant(participantFail);
        boolean result2 = tm2.executeTransaction();
        assertFalse(result2, "Transaction should rollback due to prepare failure");
        int initialRollbackCount = participantFail.getRollbackCount();
        participantFail.rollback();
        assertEquals(initialRollbackCount, participantFail.getRollbackCount() - 1, "Rollback should be idempotent");
    }

    @Test
    public void testConcurrentTransactions() throws Exception {
        final int numTransactions = 10;
        ExecutorService executor = Executors.newFixedThreadPool(numTransactions);
        List<Future<Boolean>> futures = new ArrayList<>();

        for (int i = 0; i < numTransactions; i++) {
            final int idx = i;
            Future<Boolean> future = executor.submit(() -> {
                TransactionManager tm = createTransactionManager(5000);
                TestParticipant p1 = new TestParticipant("T" + idx + "_P1", false, 50);
                TestParticipant p2 = new TestParticipant("T" + idx + "_P2", false, 50);
                tm.registerParticipant(p1);
                tm.registerParticipant(p2);
                return tm.executeTransaction();
            });
            futures.add(future);
        }

        int commitCount = 0;
        int rollbackCount = 0;
        for (Future<Boolean> f : futures) {
            if (f.get()) {
                commitCount++;
            } else {
                rollbackCount++;
            }
        }
        executor.shutdown();

        assertEquals(numTransactions, commitCount, "All concurrent transactions should commit successfully");
        assertEquals(0, rollbackCount, "No transaction should rollback in concurrent execution");
    }
}