package tx_manager;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;
import static org.junit.jupiter.api.Assertions.*;

import java.util.concurrent.*;
import java.util.List;
import java.util.ArrayList;

public class TxManagerTest {

    // Enum representing a participant's vote during prepare phase.
    enum Vote {
        COMMIT,
        ABORT
    }

    // A simple mock participant for testing purposes.
    // Assumes that the actual implementation of Participant exists in the main code.
    class TestParticipant implements Participant {
        private final String id;
        private final boolean voteCommit;
        private boolean prepared = false;
        private boolean committed = false;
        private boolean rolledBack = false;
        private final long delayMillis; // artificial delay to simulate timeouts

        public TestParticipant(String id, boolean voteCommit) {
            this(id, voteCommit, 0);
        }

        public TestParticipant(String id, boolean voteCommit, long delayMillis) {
            this.id = id;
            this.voteCommit = voteCommit;
            this.delayMillis = delayMillis;
        }

        @Override
        public Vote prepare(String transactionId) {
            try {
                if (delayMillis > 0) {
                    Thread.sleep(delayMillis);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            prepared = true;
            return voteCommit ? Vote.COMMIT : Vote.ABORT;
        }

        @Override
        public void commit(String transactionId) {
            committed = true;
        }

        @Override
        public void rollback(String transactionId) {
            rolledBack = true;
        }

        public boolean isCommitted() {
            return committed;
        }

        public boolean isRolledBack() {
            return rolledBack;
        }
    }

    // Test case 1: Verify that when all participants vote to commit, the transaction is successfully committed.
    @Test
    public void testCommitSuccessful() {
        TransactionManager tm = new TransactionManager();
        String txId = tm.beginTransaction();

        TestParticipant participant1 = new TestParticipant("p1", true);
        TestParticipant participant2 = new TestParticipant("p2", true);

        tm.registerParticipant(txId, participant1);
        tm.registerParticipant(txId, participant2);

        tm.commitTransaction(txId);

        assertTrue(participant1.isCommitted(), "Participant p1 should be committed");
        assertTrue(participant2.isCommitted(), "Participant p2 should be committed");
        assertFalse(participant1.isRolledBack(), "Participant p1 should not be rolled back");
        assertFalse(participant2.isRolledBack(), "Participant p2 should not be rolled back");
    }

    // Test case 2: Verify that if any participant votes to abort, the transaction manager rolls back the transaction.
    @Test
    public void testRollbackDueToAbortVote() {
        TransactionManager tm = new TransactionManager();
        String txId = tm.beginTransaction();

        TestParticipant participant1 = new TestParticipant("p1", true);
        TestParticipant participant2 = new TestParticipant("p2", false); // This participant votes abort

        tm.registerParticipant(txId, participant1);
        tm.registerParticipant(txId, participant2);

        tm.commitTransaction(txId);

        assertTrue(participant1.isRolledBack(), "Participant p1 should be rolled back due to an abort vote");
        assertTrue(participant2.isRolledBack(), "Participant p2 should be rolled back due to an abort vote");
        assertFalse(participant1.isCommitted(), "Participant p1 should not be committed");
        assertFalse(participant2.isCommitted(), "Participant p2 should not be committed");
    }

    // Test case 3: Simulate a participant timeout during the prepare phase, expecting the transaction to be rolled back.
    @Test
    @Timeout(5)
    public void testRollbackDueToTimeout() {
        TransactionManager tm = new TransactionManager();
        String txId = tm.beginTransaction();

        // Participant with a delay simulating a late response (e.g., timeout scenario)
        TestParticipant participant1 = new TestParticipant("p1", true, 3000);
        TestParticipant participant2 = new TestParticipant("p2", true);

        tm.registerParticipant(txId, participant1);
        tm.registerParticipant(txId, participant2);

        tm.commitTransaction(txId);

        // Expect that a timeout leads to rollback on all participants.
        assertTrue(participant1.isRolledBack(), "Participant p1 should be rolled back due to timeout");
        assertTrue(participant2.isRolledBack(), "Participant p2 should be rolled back due to timeout");
        assertFalse(participant1.isCommitted(), "Participant p1 should not be committed");
        assertFalse(participant2.isCommitted(), "Participant p2 should not be committed");
    }

    // Test case 4: Execute multiple transactions concurrently to ensure the transaction manager can handle concurrent operations.
    @Test
    public void testConcurrentTransactions() throws InterruptedException, ExecutionException {
        TransactionManager tm = new TransactionManager();
        int numberOfTransactions = 10;
        ExecutorService executor = Executors.newFixedThreadPool(5);
        List<Future<Boolean>> futures = new ArrayList<>();

        for (int i = 0; i < numberOfTransactions; i++) {
            final int index = i;
            Future<Boolean> future = executor.submit(() -> {
                String txId = tm.beginTransaction();
                TestParticipant participant1 = new TestParticipant("tx" + index + "_p1", true);
                TestParticipant participant2 = new TestParticipant("tx" + index + "_p2", true);

                tm.registerParticipant(txId, participant1);
                tm.registerParticipant(txId, participant2);

                tm.commitTransaction(txId);
                return participant1.isCommitted() && participant2.isCommitted();
            });
            futures.add(future);
        }

        for (Future<Boolean> future : futures) {
            assertTrue(future.get(), "All concurrent transactions should commit successfully");
        }

        executor.shutdown();
        assertTrue(executor.awaitTermination(5, TimeUnit.SECONDS), "Executor did not terminate in time");
    }

    // Test case 5: Verify that registering the same participant multiple times does not cause duplicate operations (idempotency).
    @Test
    public void testIdempotentOperations() {
        TransactionManager tm = new TransactionManager();
        String txId = tm.beginTransaction();

        TestParticipant participant = new TestParticipant("p", true);
        // Register the same participant twice.
        tm.registerParticipant(txId, participant);
        tm.registerParticipant(txId, participant);

        tm.commitTransaction(txId);

        assertTrue(participant.isCommitted(), "Participant should be committed exactly once");
        assertFalse(participant.isRolledBack(), "Participant should not be rolled back");
    }
}