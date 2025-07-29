package tx_coordinator;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.Arrays;
import java.util.List;

public class TxCoordinatorTest {

    // Dummy implementations for ParticipantService

    private static class SuccessfulParticipant implements ParticipantService {
        @Override
        public boolean prepare(String txId) {
            return true;
        }
        @Override
        public boolean commit(String txId) {
            return true;
        }
        @Override
        public boolean rollback(String txId) {
            return true;
        }
    }

    private static class FailingParticipant implements ParticipantService {
        @Override
        public boolean prepare(String txId) {
            return false;
        }
        @Override
        public boolean commit(String txId) {
            return false;
        }
        @Override
        public boolean rollback(String txId) {
            return true;
        }
    }

    private static class DelayedParticipant implements ParticipantService {
        private final long delayMillis;
        public DelayedParticipant(long delayMillis) {
            this.delayMillis = delayMillis;
        }
        @Override
        public boolean prepare(String txId) {
            try {
                Thread.sleep(delayMillis);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            return true;
        }
        @Override
        public boolean commit(String txId) {
            return true;
        }
        @Override
        public boolean rollback(String txId) {
            return true;
        }
    }

    // Test for a successful transaction where all participants vote to commit.
    @Test
    public void testSuccessfulTransaction() {
        List<ParticipantService> participants = Arrays.asList(
            new SuccessfulParticipant(),
            new SuccessfulParticipant(),
            new SuccessfulParticipant()
        );
        TxCoordinator coordinator = new TxCoordinator(participants, 1000);
        TransactionStatus status = coordinator.executeTransaction();
        assertEquals(TransactionStatus.COMMITTED, status, "Transaction should be committed when all participants succeed.");
    }

    // Test for a failure scenario where one participant fails during prepare.
    @Test
    public void testFailureDuringPrepare() {
        List<ParticipantService> participants = Arrays.asList(
            new SuccessfulParticipant(),
            new FailingParticipant(),
            new SuccessfulParticipant()
        );
        TxCoordinator coordinator = new TxCoordinator(participants, 1000);
        TransactionStatus status = coordinator.executeTransaction();
        assertEquals(TransactionStatus.ROLLED_BACK, status, "Transaction should be rolled back if any participant fails during prepare.");
    }

    // Test for a timeout scenario where one participant delays beyond the timeout threshold.
    @Test
    public void testTimeoutDuringPrepare() {
        // Timeout is set to 100ms, while one participant delays 200ms.
        List<ParticipantService> participants = Arrays.asList(
            new SuccessfulParticipant(),
            new DelayedParticipant(200),
            new SuccessfulParticipant()
        );
        TxCoordinator coordinator = new TxCoordinator(participants, 100);
        TransactionStatus status = coordinator.executeTransaction();
        assertEquals(TransactionStatus.ROLLED_BACK, status, "Transaction should be rolled back if a participant times out during prepare.");
    }

    // Test for idempotency: executing the transaction multiple times should consistently yield the same committed state.
    @Test
    public void testIdempotencyOnDuplicateMessages() {
        List<ParticipantService> participants = Arrays.asList(
            new SuccessfulParticipant(),
            new SuccessfulParticipant()
        );
        TxCoordinator coordinator = new TxCoordinator(participants, 1000);
        TransactionStatus firstRun = coordinator.executeTransaction();
        TransactionStatus secondRun = coordinator.executeTransaction();
        assertEquals(TransactionStatus.COMMITTED, firstRun, "First transaction execution should be committed.");
        assertEquals(TransactionStatus.COMMITTED, secondRun, "Duplicate transaction execution should remain committed due to idempotency.");
    }

    // Test concurrent transaction executions to ensure thread safety and correct handling of multiple transactions.
    @Test
    public void testConcurrentTransactions() throws InterruptedException {
        int numThreads = 10;
        Thread[] threads = new Thread[numThreads];
        TransactionStatus[] results = new TransactionStatus[numThreads];

        for (int i = 0; i < numThreads; i++) {
            final int index = i;
            threads[i] = new Thread(() -> {
                List<ParticipantService> participants = Arrays.asList(
                    new SuccessfulParticipant(),
                    new SuccessfulParticipant()
                );
                TxCoordinator coordinator = new TxCoordinator(participants, 1000);
                results[index] = coordinator.executeTransaction();
            });
            threads[i].start();
        }
        for (Thread t : threads) {
            t.join();
        }
        for (TransactionStatus status : results) {
            assertEquals(TransactionStatus.COMMITTED, status, "Every concurrent transaction should be committed when all participants succeed.");
        }
    }
}