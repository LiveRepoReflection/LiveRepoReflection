import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Assertions;

import java.util.List;
import java.util.ArrayList;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.TimeUnit;

// Assume that these interfaces/classes exist in the production code.
// The DistributedTransactionCoordinator is expected to implement the two-phase commit protocol.
// The ParticipantService interface is expected to have the methods: 
// boolean prepare(String transactionId);
// boolean commit(String transactionId);
// boolean rollback(String transactionId);

public class DistributedTxTest {

    private DistributedTransactionCoordinator coordinator;
    private AtomicInteger callCounter;

    @BeforeEach
    public void setup() {
        // Initialize the coordinator and call counter before each test.
        coordinator = new DistributedTransactionCoordinator();
        callCounter = new AtomicInteger(0);
    }

    // Test when all participants successfully prepare and commit.
    @Test
    public void testSuccessfulTransaction() {
        List<ParticipantService> participants = new ArrayList<>();
        participants.add(new SuccessParticipant());
        participants.add(new SuccessParticipant());
        participants.add(new SuccessParticipant());

        boolean result = coordinator.executeTransaction("tx-success", participants, 2000);
        Assertions.assertTrue(result, "Transaction should commit successfully when all participants succeed.");
    }

    // Test when one participant fails during prepare phase.
    @Test
    public void testPrepareFailure() {
        List<ParticipantService> participants = new ArrayList<>();
        participants.add(new SuccessParticipant());
        participants.add(new FailPrepareParticipant());
        participants.add(new SuccessParticipant());

        boolean result = coordinator.executeTransaction("tx-prepare-fail", participants, 2000);
        Assertions.assertFalse(result, "Transaction should rollback when a participant fails during prepare.");
    }

    // Test when one participant times out during prepare phase.
    @Test
    public void testPrepareTimeout() {
        List<ParticipantService> participants = new ArrayList<>();
        participants.add(new SuccessParticipant());
        participants.add(new TimeoutParticipant(3000)); // This participant will sleep 3000ms which is beyond our timeout.
        participants.add(new SuccessParticipant());

        boolean result = coordinator.executeTransaction("tx-timeout", participants, 1000);
        Assertions.assertFalse(result, "Transaction should rollback when a participant times out.");
    }

    // Test when one participant fails during commit phase.
    @Test
    public void testCommitFailure() {
        List<ParticipantService> participants = new ArrayList<>();
        participants.add(new SuccessParticipant());
        participants.add(new FailCommitParticipant());
        participants.add(new SuccessParticipant());

        boolean result = coordinator.executeTransaction("tx-commit-fail", participants, 2000);
        Assertions.assertFalse(result, "Transaction should rollback when a participant fails during commit.");
    }

    // Test idempotency by executing the same transaction more than once.
    @Test
    public void testIdempotentExecution() {
        List<ParticipantService> participants = new ArrayList<>();
        participants.add(new SuccessParticipant());
        participants.add(new SuccessParticipant());

        // First execution should commit.
        boolean firstResult = coordinator.executeTransaction("tx-idempotent", participants, 2000);
        // Simulate a duplicate execution for the same transaction id.
        boolean secondResult = coordinator.executeTransaction("tx-idempotent", participants, 2000);

        Assertions.assertTrue(firstResult, "First execution should commit successfully.");
        Assertions.assertTrue(secondResult, "Duplicate execution should be idempotent and return the same result.");
    }

    // Inner classes to simulate different participant behaviors.

    // A participant that always succeeds.
    private class SuccessParticipant implements ParticipantService {
        @Override
        public boolean prepare(String transactionId) {
            callCounter.incrementAndGet();
            return true;
        }
        @Override
        public boolean commit(String transactionId) {
            callCounter.incrementAndGet();
            return true;
        }
        @Override
        public boolean rollback(String transactionId) {
            callCounter.incrementAndGet();
            return true;
        }
    }

    // A participant that fails during the prepare phase.
    private class FailPrepareParticipant implements ParticipantService {
        @Override
        public boolean prepare(String transactionId) {
            callCounter.incrementAndGet();
            return false;
        }
        @Override
        public boolean commit(String transactionId) {
            callCounter.incrementAndGet();
            return true;
        }
        @Override
        public boolean rollback(String transactionId) {
            callCounter.incrementAndGet();
            return true;
        }
    }

    // A participant that introduces a delay to simulate a timeout in the prepare phase.
    private class TimeoutParticipant implements ParticipantService {
        private final long delayMillis;
        public TimeoutParticipant(long delayMillis) {
            this.delayMillis = delayMillis;
        }
        @Override
        public boolean prepare(String transactionId) {
            try {
                Thread.sleep(delayMillis);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            callCounter.incrementAndGet();
            return true;
        }
        @Override
        public boolean commit(String transactionId) {
            callCounter.incrementAndGet();
            return true;
        }
        @Override
        public boolean rollback(String transactionId) {
            callCounter.incrementAndGet();
            return true;
        }
    }

    // A participant that fails during the commit phase.
    private class FailCommitParticipant implements ParticipantService {
        @Override
        public boolean prepare(String transactionId) {
            callCounter.incrementAndGet();
            return true;
        }
        @Override
        public boolean commit(String transactionId) {
            callCounter.incrementAndGet();
            return false;
        }
        @Override
        public boolean rollback(String transactionId) {
            callCounter.incrementAndGet();
            return true;
        }
    }
}