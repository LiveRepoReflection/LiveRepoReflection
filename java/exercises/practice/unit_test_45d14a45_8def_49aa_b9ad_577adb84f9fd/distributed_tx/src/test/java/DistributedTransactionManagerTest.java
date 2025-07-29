package distributed_tx;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.assertEquals;
import java.util.List;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.concurrent.Callable;
import java.util.concurrent.Future;
import java.util.concurrent.Executors;
import java.util.concurrent.ExecutorService;

// The following tests assume the existence of the following production code classes/interfaces:
// - DistributedTransactionManager with a constructor DistributedTransactionManager(List<TransactionParticipant> participants, int timeoutMillis)
//   and method TransactionResult executeTransaction() throws Exception.
// - TransactionParticipant interface with methods:
//       boolean prepare() throws Exception;
//       void commit() throws Exception;
//       void rollback() throws Exception;
// - TransactionResult enum { COMMIT, ABORT }
//
// The tests below use dummy implementations of TransactionParticipant to simulate different scenarios.

public class DistributedTransactionManagerTest {

    private static final int DEFAULT_TIMEOUT = 2000;

    // Dummy participant that always succeeds in prepare and records commit/rollback calls.
    static class SuccessParticipant implements TransactionParticipant {
        private final String name;
        private boolean committed = false;
        private boolean rolledBack = false;
        private int prepareCount = 0;
        private int commitCount = 0;
        private int rollbackCount = 0;

        public SuccessParticipant(String name) {
            this.name = name;
        }

        @Override
        public boolean prepare() throws Exception {
            prepareCount++;
            return true;
        }

        @Override
        public void commit() throws Exception {
            commitCount++;
            committed = true;
        }

        @Override
        public void rollback() throws Exception {
            rollbackCount++;
            rolledBack = true;
        }

        public boolean isCommitted() {
            return committed;
        }

        public boolean isRolledBack() {
            return rolledBack;
        }

        public int getPrepareCount() {
            return prepareCount;
        }

        public int getCommitCount() {
            return commitCount;
        }

        public int getRollbackCount() {
            return rollbackCount;
        }
    }

    // Dummy participant that fails on prepare.
    static class FailureParticipant implements TransactionParticipant {
        private final String name;
        private boolean rolledBack = false;

        public FailureParticipant(String name) {
            this.name = name;
        }

        @Override
        public boolean prepare() throws Exception {
            throw new Exception("Prepare failed for participant: " + name);
        }

        @Override
        public void commit() throws Exception {
            // Should not be called in failure scenario.
        }

        @Override
        public void rollback() throws Exception {
            rolledBack = true;
        }

        public boolean isRolledBack() {
            return rolledBack;
        }
    }

    // Dummy participant to simulate a timeout by sleeping longer than allowed.
    static class TimeoutParticipant implements TransactionParticipant {
        private final String name;
        private final int delayMillis;
        private boolean rolledBack = false;

        public TimeoutParticipant(String name, int delayMillis) {
            this.name = name;
            this.delayMillis = delayMillis;
        }

        @Override
        public boolean prepare() throws Exception {
            Thread.sleep(delayMillis);
            return true;
        }

        @Override
        public void commit() throws Exception {
            // Should be called only if prepare succeeds before timeout.
        }

        @Override
        public void rollback() throws Exception {
            rolledBack = true;
        }

        public boolean isRolledBack() {
            return rolledBack;
        }
    }

    // Dummy participant to test idempotency by counting the number of operations invoked.
    static class CountingParticipant implements TransactionParticipant {
        private int prepareCount = 0;
        private int commitCount = 0;
        private int rollbackCount = 0;
        private boolean prepared = false;
        private boolean committed = false;
        private boolean rolledBack = false;

        @Override
        public synchronized boolean prepare() throws Exception {
            prepareCount++;
            if (!prepared) {
                prepared = true;
                return true;
            }
            // if already prepared, return same result without side effects
            return true;
        }

        @Override
        public synchronized void commit() throws Exception {
            commitCount++;
            if (!committed) {
                committed = true;
            }
        }

        @Override
        public synchronized void rollback() throws Exception {
            rollbackCount++;
            if (!rolledBack) {
                rolledBack = true;
            }
        }

        public int getPrepareCount() {
            return prepareCount;
        }

        public int getCommitCount() {
            return commitCount;
        }

        public int getRollbackCount() {
            return rollbackCount;
        }
    }

    @Test
    public void testSuccessfulTransaction() throws Exception {
        SuccessParticipant participant1 = new SuccessParticipant("p1");
        SuccessParticipant participant2 = new SuccessParticipant("p2");

        List<TransactionParticipant> participants = Arrays.asList(participant1, participant2);
        DistributedTransactionManager dtm = new DistributedTransactionManager(participants, DEFAULT_TIMEOUT);

        TransactionResult result = dtm.executeTransaction();

        assertEquals(TransactionResult.COMMIT, result, "Transaction should commit when all participants prepare successfully.");
        // Ensure commit was invoked on participants.
        assertEquals(1, participant1.getCommitCount(), "Participant1 commit should be called once.");
        assertEquals(1, participant2.getCommitCount(), "Participant2 commit should be called once.");
    }

    @Test
    public void testFailedTransactionDueToPrepareFailure() throws Exception {
        SuccessParticipant participant1 = new SuccessParticipant("p1");
        FailureParticipant participant2 = new FailureParticipant("p2");

        List<TransactionParticipant> participants = Arrays.asList(participant1, participant2);
        DistributedTransactionManager dtm = new DistributedTransactionManager(participants, DEFAULT_TIMEOUT);

        TransactionResult result = dtm.executeTransaction();

        assertEquals(TransactionResult.ABORT, result, "Transaction should abort when any participant fails in prepare.");
        // Participant1 should have rolled back.
        assertEquals(1, participant1.getRollbackCount(), "Participant1 rollback should be called once.");
    }

    @Test
    public void testTransactionTimeout() throws Exception {
        SuccessParticipant participant1 = new SuccessParticipant("p1");
        // Set delay longer than the manager timeout to trigger timeout.
        TimeoutParticipant participant2 = new TimeoutParticipant("p2", DEFAULT_TIMEOUT + 1000);

        List<TransactionParticipant> participants = Arrays.asList(participant1, participant2);
        // Use a shorter timeout value.
        DistributedTransactionManager dtm = new DistributedTransactionManager(participants, DEFAULT_TIMEOUT);

        TransactionResult result = dtm.executeTransaction();

        assertEquals(TransactionResult.ABORT, result, "Transaction should abort when a participant times out.");
        // Participant1 should have rolled back.
        assertEquals(1, participant1.getRollbackCount(), "Participant1 rollback should be called due to timeout.");
    }

    @Test
    public void testConcurrentTransactions() throws Exception {
        ExecutorService executor = Executors.newFixedThreadPool(5);
        List<Callable<TransactionResult>> tasks = new ArrayList<>();

        // Create 10 concurrent transactions
        for (int i = 0; i < 10; i++) {
            tasks.add(() -> {
                SuccessParticipant participant1 = new SuccessParticipant("concurrent_p1");
                SuccessParticipant participant2 = new SuccessParticipant("concurrent_p2");
                List<TransactionParticipant> participants = Arrays.asList(participant1, participant2);
                DistributedTransactionManager dtm = new DistributedTransactionManager(participants, DEFAULT_TIMEOUT);
                return dtm.executeTransaction();
            });
        }

        List<Future<TransactionResult>> results = executor.invokeAll(tasks);
        for (Future<TransactionResult> future : results) {
            assertEquals(TransactionResult.COMMIT, future.get(), "Each concurrent transaction should commit successfully.");
        }
        executor.shutdown();
    }

    @Test
    public void testIdempotency() throws Exception {
        CountingParticipant participant = new CountingParticipant();
        List<TransactionParticipant> participants = Arrays.asList(participant);
        DistributedTransactionManager dtm = new DistributedTransactionManager(participants, DEFAULT_TIMEOUT);

        // Execute transaction. The manager's logic should call prepare only once.
        TransactionResult result = dtm.executeTransaction();

        assertEquals(TransactionResult.COMMIT, result, "Transaction should commit successfully.");
        // Verify that prepare and commit were called only once despite potential duplicate messaging in recovery.
        assertEquals(1, participant.getPrepareCount(), "Prepare should be executed only once.");
        assertEquals(1, participant.getCommitCount(), "Commit should be executed only once.");
    }
}