import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Assertions;

import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

public class DistributedTxTest {

    // Dummy TransactionState enum for testing expectations.
    enum TransactionState {
        PENDING,
        PREPARING,
        PREPARED,
        COMMITTING,
        COMMITTED,
        ROLLING_BACK,
        ROLLED_BACK,
        ABORTED
    }

    // Participant interface as defined in the problem statement.
    interface Participant {
        boolean prepare();
        void commit();
        void rollback();
    }

    // Dummy implementation of a participant that can simulate delays and failures.
    class DummyParticipant implements Participant {
        private final boolean shouldPrepareSucceed;
        private final long prepareDelayMillis;
        private volatile boolean commitCalled = false;
        private volatile boolean rollbackCalled = false;
        private final AtomicInteger commitCount = new AtomicInteger(0);
        private final AtomicInteger rollbackCount = new AtomicInteger(0);

        public DummyParticipant(boolean shouldPrepareSucceed, long prepareDelayMillis) {
            this.shouldPrepareSucceed = shouldPrepareSucceed;
            this.prepareDelayMillis = prepareDelayMillis;
        }

        @Override
        public boolean prepare() {
            try {
                Thread.sleep(prepareDelayMillis);
            } catch (InterruptedException ie) {
                Thread.currentThread().interrupt();
            }
            return shouldPrepareSucceed;
        }

        @Override
        public void commit() {
            commitCalled = true;
            commitCount.incrementAndGet();
        }

        @Override
        public void rollback() {
            rollbackCalled = true;
            rollbackCount.incrementAndGet();
        }

        public boolean isCommitCalled() {
            return commitCalled;
        }

        public boolean isRollbackCalled() {
            return rollbackCalled;
        }

        public int getCommitCount() {
            return commitCount.get();
        }

        public int getRollbackCount() {
            return rollbackCount.get();
        }
    }

    // A simplified Distributed Transaction Coordinator implementation for testing.
    // This dummy implementation simulates the 2PC protocol.
    class DistributedTxCoordinator {
        private final List<Participant> participants;
        private volatile TransactionState state = TransactionState.PENDING;
        // Timeout for each phase in milliseconds.
        private final long phaseTimeoutMillis;

        public DistributedTxCoordinator(List<Participant> participants, long phaseTimeoutMillis) {
            this.participants = participants;
            this.phaseTimeoutMillis = phaseTimeoutMillis;
        }

        public TransactionState executeTransaction() {
            state = TransactionState.PREPARING;
            ExecutorService executor = Executors.newFixedThreadPool(participants.size());
            try {
                List<Future<Boolean>> prepareFutures = new ArrayList<>();
                for (Participant p : participants) {
                    Future<Boolean> future = executor.submit(p::prepare);
                    prepareFutures.add(future);
                }

                for (Future<Boolean> f : prepareFutures) {
                    try {
                        boolean prepared = f.get(phaseTimeoutMillis, TimeUnit.MILLISECONDS);
                        if (!prepared) {
                            state = TransactionState.ABORTED;
                            rollbackParticipants();
                            executor.shutdownNow();
                            return TransactionState.ROLLED_BACK;
                        }
                    } catch (TimeoutException te) {
                        state = TransactionState.ABORTED;
                        rollbackParticipants();
                        executor.shutdownNow();
                        return TransactionState.ROLLED_BACK;
                    } catch (Exception e) {
                        state = TransactionState.ABORTED;
                        rollbackParticipants();
                        executor.shutdownNow();
                        return TransactionState.ROLLED_BACK;
                    }
                }
            } finally {
                // No matter what, ensure we shutdown the executor.
                executor.shutdown();
            }

            // If we reached here all prepares succeeded within timeout.
            state = TransactionState.PREPARED;
            state = TransactionState.COMMITTING;
            for (Participant p : participants) {
                try {
                    p.commit();
                } catch (Exception e) {
                    // Commit failures should be handled by idempotency.
                }
            }
            state = TransactionState.COMMITTED;
            return state;
        }

        private void rollbackParticipants() {
            state = TransactionState.ROLLING_BACK;
            for (Participant p : participants) {
                try {
                    p.rollback();
                } catch (Exception ignored) {
                }
            }
            state = TransactionState.ROLLED_BACK;
        }

        public TransactionState getState() {
            return state;
        }
    }

    private final long TIMEOUT_MS = 500;

    @Test
    public void testSuccessfulTransaction() {
        List<Participant> participants = new ArrayList<>();
        // All participants succeed immediately.
        participants.add(new DummyParticipant(true, 0));
        participants.add(new DummyParticipant(true, 0));
        DistributedTxCoordinator coordinator = new DistributedTxCoordinator(participants, TIMEOUT_MS);
        TransactionState finalState = coordinator.executeTransaction();
        Assertions.assertEquals(TransactionState.COMMITTED, finalState, "Transaction should be committed");
        // Verify that each participant had commit called.
        for (Participant p : participants) {
            DummyParticipant dp = (DummyParticipant) p;
            Assertions.assertTrue(dp.isCommitCalled(), "Commit should have been called on each participant");
            Assertions.assertEquals(1, dp.getCommitCount(), "Commit should be idempotent with single call");
        }
    }

    @Test
    public void testTransactionPrepareFailure() {
        List<Participant> participants = new ArrayList<>();
        // One participant fails prepare.
        participants.add(new DummyParticipant(true, 0));
        participants.add(new DummyParticipant(false, 0));
        DistributedTxCoordinator coordinator = new DistributedTxCoordinator(participants, TIMEOUT_MS);
        TransactionState finalState = coordinator.executeTransaction();
        Assertions.assertEquals(TransactionState.ROLLED_BACK, finalState, "Transaction should be rolled back on prepare failure");

        for (Participant p : participants) {
            DummyParticipant dp = (DummyParticipant) p;
            // For the one that succeeded prepare, rollback should be called.
            Assertions.assertTrue(dp.isRollbackCalled(), "Rollback should have been called on each participant after failure");
            Assertions.assertEquals(1, dp.getRollbackCount(), "Rollback call should be idempotent with single call");
        }
    }

    @Test
    public void testTransactionPrepareTimeout() {
        List<Participant> participants = new ArrayList<>();
        // One participant takes too long to prepare.
        participants.add(new DummyParticipant(true, TIMEOUT_MS + 200));
        participants.add(new DummyParticipant(true, 0));
        DistributedTxCoordinator coordinator = new DistributedTxCoordinator(participants, TIMEOUT_MS);
        TransactionState finalState = coordinator.executeTransaction();
        Assertions.assertEquals(TransactionState.ROLLED_BACK, finalState, "Transaction should be rolled back on timeout");

        for (Participant p : participants) {
            DummyParticipant dp = (DummyParticipant) p;
            Assertions.assertTrue(dp.isRollbackCalled(), "Rollback should have been called on each participant after timeout");
        }
    }

    @Test
    public void testIdempotencyOfCommit() {
        DummyParticipant dp = new DummyParticipant(true, 0);
        // Directly call commit multiple times to test idempotency.
        dp.commit();
        dp.commit();
        dp.commit();
        Assertions.assertTrue(dp.isCommitCalled(), "Commit should be called");
        Assertions.assertEquals(3, dp.getCommitCount(), "Participant commit should record all calls even if coordinator retries, so consumer must handle idempotency");
    }

    @Test
    public void testIdempotencyOfRollback() {
        DummyParticipant dp = new DummyParticipant(true, 0);
        // Directly call rollback multiple times to test idempotency.
        dp.rollback();
        dp.rollback();
        Assertions.assertTrue(dp.isRollbackCalled(), "Rollback should be called");
        Assertions.assertEquals(2, dp.getRollbackCount(), "Participant rollback should record all calls even if coordinator retries, so consumer must handle idempotency");
    }

    @Test
    public void testConcurrentTransactions() throws InterruptedException, ExecutionException {
        int numberOfTransactions = 10;
        ExecutorService executor = Executors.newFixedThreadPool(numberOfTransactions);
        List<Future<TransactionState>> futures = new ArrayList<>();

        for (int i = 0; i < numberOfTransactions; i++) {
            futures.add(executor.submit(() -> {
                List<Participant> parts = new ArrayList<>();
                // Using participants with immediate success.
                parts.add(new DummyParticipant(true, 0));
                parts.add(new DummyParticipant(true, 0));
                DistributedTxCoordinator coordinator = new DistributedTxCoordinator(parts, TIMEOUT_MS);
                return coordinator.executeTransaction();
            }));
        }
        for (Future<TransactionState> f : futures) {
            TransactionState state = f.get();
            Assertions.assertEquals(TransactionState.COMMITTED, state, "Each concurrent transaction should commit successfully");
        }
        executor.shutdown();
    }

    @Test
    @Timeout(5)
    public void testCoordinatorResilienceUnderLoad() throws InterruptedException {
        int concurrentTransactions = 50;
        ExecutorService executor = Executors.newFixedThreadPool(concurrentTransactions);
        CountDownLatch latch = new CountDownLatch(concurrentTransactions);
        List<DistributedTxCoordinator> coordinators = new ArrayList<>();

        for (int i = 0; i < concurrentTransactions; i++) {
            List<Participant> parts = new ArrayList<>();
            parts.add(new DummyParticipant(true, 0));
            parts.add(new DummyParticipant(true, 0));
            DistributedTxCoordinator coordinator = new DistributedTxCoordinator(parts, TIMEOUT_MS);
            coordinators.add(coordinator);
            executor.execute(() -> {
                coordinator.executeTransaction();
                latch.countDown();
            });
        }
        latch.await();
        for (DistributedTxCoordinator coordinator : coordinators) {
            Assertions.assertEquals(TransactionState.COMMITTED, coordinator.getState(), "Each transaction under load should be committed");
        }
        executor.shutdown();
    }
}