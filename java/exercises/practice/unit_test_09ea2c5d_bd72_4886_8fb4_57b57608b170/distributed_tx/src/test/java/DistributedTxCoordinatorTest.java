package distributed_tx;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.ArrayList;
import java.util.List;

/**
 * This unit test suite verifies the behavior of the distributed transaction coordinator,
 * ensuring correctness of the Two-Phase Commit protocol implementation covering various scenarios:
 * successful commit, vote abort, participant failures during prepare and commit phases, and coordinator recovery.
 *
 * NOTE: The test assumes that the following classes and interfaces exist in the main source package:
 * - TransactionCoordinator with methods:
 *       TransactionStatus coordinateTransaction(Transaction tx, List<Participant> participants) throws Exception;
 *       TransactionStatus recoverTransaction(String transactionId) throws Exception;
 * - Transaction with at least a constructor Transaction(String transactionId, double amount, String fromAccount, String toAccount)
 *       and a getter getTransactionId().
 * - Participant interface with methods:
 *       boolean prepare(Transaction tx) throws Exception;
 *       void commit(Transaction tx) throws Exception;
 *       void abort(Transaction tx) throws Exception;
 * - TransactionStatus enum with at least COMMITTED and ABORTED values.
 */
public class DistributedTxCoordinatorTest {

    private TransactionCoordinator coordinator;
    private Transaction sampleTransaction;

    @BeforeEach
    public void setup() {
        // Initialize the coordinator and a sample transaction.
        coordinator = new TransactionCoordinator();
        sampleTransaction = new Transaction("tx123", 100.0, "accountA", "accountB");
    }

    // A fake implementation of the Participant interface to simulate various participant behaviors.
    private static class FakeParticipant implements Participant {
        private boolean voteCommit;
        private boolean failOnPrepare;
        private boolean failOnCommit;
        private boolean committed = false;
        private boolean aborted = false;

        public FakeParticipant(boolean voteCommit, boolean failOnPrepare, boolean failOnCommit) {
            this.voteCommit = voteCommit;
            this.failOnPrepare = failOnPrepare;
            this.failOnCommit = failOnCommit;
        }

        @Override
        public boolean prepare(Transaction tx) throws Exception {
            if (failOnPrepare) {
                throw new Exception("Simulated failure during prepare phase");
            }
            return voteCommit;
        }

        @Override
        public void commit(Transaction tx) throws Exception {
            if (failOnCommit) {
                throw new Exception("Simulated failure during commit phase");
            }
            committed = true;
        }

        @Override
        public void abort(Transaction tx) throws Exception {
            aborted = true;
        }

        public boolean isCommitted() {
            return committed;
        }

        public boolean isAborted() {
            return aborted;
        }
    }

    @Test
    public void testSuccessfulTransactionCommit() throws Exception {
        // Create participants that all vote to commit.
        List<Participant> participants = new ArrayList<>();
        participants.add(new FakeParticipant(true, false, false));
        participants.add(new FakeParticipant(true, false, false));

        TransactionStatus status = coordinator.coordinateTransaction(sampleTransaction, participants);
        assertEquals(TransactionStatus.COMMITTED, status, "Transaction should be committed when all participants vote commit");

        // Verify that commit was invoked on all participants.
        for (Participant p : participants) {
            FakeParticipant fp = (FakeParticipant) p;
            assertTrue(fp.isCommitted(), "Participant should have executed commit operation");
        }
    }

    @Test
    public void testTransactionAbortDueToAbortVote() throws Exception {
        // One participant votes abort.
        List<Participant> participants = new ArrayList<>();
        participants.add(new FakeParticipant(true, false, false));
        participants.add(new FakeParticipant(false, false, false)); // votes to abort

        TransactionStatus status = coordinator.coordinateTransaction(sampleTransaction, participants);
        assertEquals(TransactionStatus.ABORTED, status, "Transaction should be aborted if any participant votes abort");

        // Verify that abort was invoked on all participants.
        for (Participant p : participants) {
            FakeParticipant fp = (FakeParticipant) p;
            assertTrue(fp.isAborted(), "Participant should have executed abort operation");
        }
    }

    @Test
    public void testPreparePhaseFailureResultsInAbort() throws Exception {
        // One participant fails during the prepare phase.
        List<Participant> participants = new ArrayList<>();
        participants.add(new FakeParticipant(true, false, false));
        participants.add(new FakeParticipant(true, true, false)); // fails during prepare

        TransactionStatus status = coordinator.coordinateTransaction(sampleTransaction, participants);
        assertEquals(TransactionStatus.ABORTED, status, "Transaction should be aborted if any participant fails during prepare");

        // Verify that participants that did not fail still receive an abort command.
        for (Participant p : participants) {
            FakeParticipant fp = (FakeParticipant) p;
            if (!fp.failOnPrepare) {
                assertTrue(fp.isAborted(), "Participant should abort if another participant fails during prepare");
            }
        }
    }

    @Test
    public void testCommitRetryOnParticipantFailure() throws Exception {
        // Create a participant that initially fails on commit but recovers on retry.
        FakeParticipant flakyParticipant = new FakeParticipant(true, false, true);
        List<Participant> participants = new ArrayList<>();
        participants.add(new FakeParticipant(true, false, false));
        participants.add(flakyParticipant);

        // First transaction attempt should result in a failure due to the flaky participant.
        Exception firstAttemptException = assertThrows(Exception.class, () -> {
            coordinator.coordinateTransaction(sampleTransaction, participants);
        }, "Expected exception due to commit failure from a participant");
        assertNotNull(firstAttemptException.getMessage());

        // Simulate the participant recovery by flipping the failure flag.
        flakyParticipant.failOnCommit = false;

        // Retry the transaction.
        TransactionStatus status = coordinator.coordinateTransaction(sampleTransaction, participants);
        assertEquals(TransactionStatus.COMMITTED, status, "Transaction should be committed after participant recovers on commit retry");

        // Verify that commit was invoked on all participants.
        for (Participant p : participants) {
            FakeParticipant fp = (FakeParticipant) p;
            assertTrue(fp.isCommitted(), "Participant should have executed commit after recovery and retry");
        }
    }

    @Test
    public void testCoordinatorRecovery() throws Exception {
        // Simulate a transaction that was in-flight during a coordinator failure.
        List<Participant> participants = new ArrayList<>();
        participants.add(new FakeParticipant(true, false, false));
        participants.add(new FakeParticipant(true, false, false));

        // Execute the transaction before a simulated crash, ensuring it logs the state.
        coordinator.coordinateTransaction(sampleTransaction, participants);

        // Simulate coordinator failure and subsequent recovery by instantiating a new coordinator that reloads the transaction log.
        TransactionCoordinator recoveredCoordinator = new TransactionCoordinator();
        TransactionStatus recoveredStatus = recoveredCoordinator.recoverTransaction(sampleTransaction.getTransactionId());
        assertEquals(TransactionStatus.COMMITTED, recoveredStatus, "Recovered transaction should reflect the committed state post-crash");
    }
}