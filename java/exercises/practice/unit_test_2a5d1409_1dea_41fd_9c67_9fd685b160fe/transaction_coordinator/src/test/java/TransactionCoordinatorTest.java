package transaction_coordinator;

import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Timeout;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

public class TransactionCoordinatorTest {

    private DistributedTransactionCoordinator coordinator;

    @BeforeEach
    public void setup() {
        coordinator = new DistributedTransactionCoordinator();
    }

    // A mock implementation of TransactionParticipant that always succeeds in prepare.
    private static class SuccessParticipant implements TransactionParticipant {
        private final String id;
        private final AtomicInteger commitCount = new AtomicInteger(0);
        private final AtomicInteger rollbackCount = new AtomicInteger(0);

        public SuccessParticipant(String id) {
            this.id = id;
        }

        @Override
        public boolean prepare(String txId, String operation) {
            return true;
        }

        @Override
        public void commit(String txId) {
            // Idempotency: only increment if first call.
            if (commitCount.get() == 0) {
                commitCount.incrementAndGet();
            }
        }

        @Override
        public void rollback(String txId) {
            if (rollbackCount.get() == 0) {
                rollbackCount.incrementAndGet();
            }
        }

        public int getCommitCount() {
            return commitCount.get();
        }

        public int getRollbackCount() {
            return rollbackCount.get();
        }
    }

    // A mock implementation of TransactionParticipant that fails during prepare.
    private static class FailParticipant implements TransactionParticipant {
        private final String id;

        public FailParticipant(String id) {
            this.id = id;
        }

        @Override
        public boolean prepare(String txId, String operation) {
            return false;
        }

        @Override
        public void commit(String txId) {
            throw new IllegalStateException("Commit should not be invoked on a failed participant.");
        }

        @Override
        public void rollback(String txId) {
            // No state change needed for rollback simulation.
        }
    }

    // A mock implementation of TransactionParticipant that simulates a delay (to trigger timeout).
    private static class SlowParticipant implements TransactionParticipant {
        private final String id;
        private final long delayMillis;

        public SlowParticipant(String id, long delayMillis) {
            this.id = id;
            this.delayMillis = delayMillis;
        }

        @Override
        public boolean prepare(String txId, String operation) {
            try {
                Thread.sleep(delayMillis);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            return true;
        }

        @Override
        public void commit(String txId) {
            // Commit does nothing extra.
        }

        @Override
        public void rollback(String txId) {
            // Rollback does nothing extra.
        }
    }

    // Test that all participants commit successfully when prepare phase is successful.
    @Test
    public void testSuccessfulCommit() {
        SuccessParticipant participant1 = new SuccessParticipant("P1");
        SuccessParticipant participant2 = new SuccessParticipant("P2");

        coordinator.registerParticipant("P1", participant1);
        coordinator.registerParticipant("P2", participant2);

        Map<String, String> operations = new HashMap<>();
        operations.put("P1", "updateAccount");
        operations.put("P2", "createOrder");
        TransactionRequest request = new TransactionRequest(operations);

        boolean result = coordinator.executeTransaction(request);
        assertTrue(result, "The transaction should be committed successfully.");

        // Verify commit was executed exactly once for each participant.
        assertEquals(1, participant1.getCommitCount(), "Participant P1 should commit exactly once.");
        assertEquals(1, participant2.getCommitCount(), "Participant P2 should commit exactly once.");
    }

    // Test that the transaction is aborted when any participant fails during prepare.
    @Test
    public void testAbortDueToPrepareFailure() {
        SuccessParticipant participant1 = new SuccessParticipant("P1");
        FailParticipant participant2 = new FailParticipant("P2");

        coordinator.registerParticipant("P1", participant1);
        coordinator.registerParticipant("P2", participant2);

        Map<String, String> operations = new HashMap<>();
        operations.put("P1", "processPayment");
        operations.put("P2", "reserveInventory");
        TransactionRequest request = new TransactionRequest(operations);

        boolean result = coordinator.executeTransaction(request);
        assertFalse(result, "The transaction should be aborted due to a prepare failure.");

        // Participant that succeeded in prepare should have had rollback invoked.
        assertEquals(0, participant1.getCommitCount(), "Participant P1 should not have committed on abort.");
    }

    // Test that a transaction is aborted due to timeout when a participant responds too slowly.
    @Test
    @Timeout(5)
    public void testAbortDueToTimeout() {
        SuccessParticipant participant1 = new SuccessParticipant("P1");
        // Slow participant with delay intended to exceed the coordinator's timeout threshold.
        SlowParticipant participant2 = new SlowParticipant("P2", 3000);

        coordinator.registerParticipant("P1", participant1);
        coordinator.registerParticipant("P2", participant2);

        Map<String, String> operations = new HashMap<>();
        operations.put("P1", "debitAccount");
        operations.put("P2", "updateInventory");
        TransactionRequest request = new TransactionRequest(operations);

        boolean result = coordinator.executeTransaction(request);
        assertFalse(result, "The transaction should be aborted due to a timeout in the prepare phase.");

        // Verify participant1 did not commit.
        assertEquals(0, participant1.getCommitCount(), "Participant P1 should not commit when the transaction is aborted.");
    }

    // Test multiple concurrent transactions to verify thread-safety and concurrency.
    @Test
    public void testConcurrentTransactions() throws InterruptedException, ExecutionException {
        int numTransactions = 10;
        ExecutorService executor = Executors.newFixedThreadPool(numTransactions);
        List<Future<Boolean>> futures = new ArrayList<>();

        for (int i = 0; i < numTransactions; i++) {
            final String pid1 = "P1_" + i;
            final String pid2 = "P2_" + i;
            SuccessParticipant participant1 = new SuccessParticipant(pid1);
            SuccessParticipant participant2 = new SuccessParticipant(pid2);
            coordinator.registerParticipant(pid1, participant1);
            coordinator.registerParticipant(pid2, participant2);

            Map<String, String> operations = new HashMap<>();
            operations.put(pid1, "op1");
            operations.put(pid2, "op2");
            final TransactionRequest request = new TransactionRequest(operations);

            Future<Boolean> future = executor.submit(() -> coordinator.executeTransaction(request));
            futures.add(future);
        }

        for (Future<Boolean> future : futures) {
            assertTrue(future.get(), "Each concurrent transaction should be committed successfully.");
        }

        executor.shutdown();
    }

    // Test to verify idempotency: even if multiple commit calls are issued, commit is only applied once.
    @Test
    public void testIdempotencyOnCommit() {
        SuccessParticipant participant1 = new SuccessParticipant("P1");

        coordinator.registerParticipant("P1", participant1);

        Map<String, String> operations = new HashMap<>();
        operations.put("P1", "updateProfile");
        TransactionRequest request = new TransactionRequest(operations);

        boolean result = coordinator.executeTransaction(request);
        assertTrue(result, "The transaction should be committed successfully.");

        // Simulate a duplicate commit call that might happen due to retries.
        participant1.commit("dummy_tx");

        assertEquals(1, participant1.getCommitCount(), "Commit operation must be idempotent and executed only once.");
    }
}