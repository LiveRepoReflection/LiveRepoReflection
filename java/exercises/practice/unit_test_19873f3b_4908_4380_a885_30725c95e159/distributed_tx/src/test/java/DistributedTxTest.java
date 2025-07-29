package distributed_tx;

import org.junit.Assert;
import org.junit.Test;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;

public class DistributedTxTest {

    // Dummy Participant implementation for testing.
    // Assumes that the production code includes a Participant interface with the following methods:
    //  - boolean prepare();
    //  - void commit();
    //  - void rollback();
    class DummyParticipant implements Participant {
        private final boolean voteCommit;
        private final long prepareDelay; // in milliseconds

        public DummyParticipant(boolean voteCommit, long prepareDelay) {
            this.voteCommit = voteCommit;
            this.prepareDelay = prepareDelay;
        }

        @Override
        public boolean prepare() {
            try {
                Thread.sleep(prepareDelay);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            return voteCommit;
        }

        @Override
        public void commit() {
            // Simulate commit operation.
        }

        @Override
        public void rollback() {
            // Simulate rollback operation.
        }
    }

    // Test successful transaction where all participants vote commit.
    @Test
    public void testSuccessfulTransaction() {
        Coordinator coordinator = new Coordinator();
        coordinator.addParticipant(new DummyParticipant(true, 50));
        coordinator.addParticipant(new DummyParticipant(true, 50));
        coordinator.addParticipant(new DummyParticipant(true, 50));

        boolean result = coordinator.executeTransaction();
        Assert.assertTrue("Transaction should commit successfully", result);
    }

    // Test transaction abort when one participant votes abort.
    @Test
    public void testAbortTransaction() {
        Coordinator coordinator = new Coordinator();
        coordinator.addParticipant(new DummyParticipant(true, 50));
        coordinator.addParticipant(new DummyParticipant(false, 50));
        coordinator.addParticipant(new DummyParticipant(true, 50));

        boolean result = coordinator.executeTransaction();
        Assert.assertFalse("Transaction should abort due to one participant voting abort", result);
    }

    // Test transaction abort due to a participant timeout.
    @Test
    public void testParticipantTimeout() {
        Coordinator coordinator = new Coordinator();
        // Assuming the coordinator has a timeout threshold around 100ms.
        coordinator.addParticipant(new DummyParticipant(true, 50));
        coordinator.addParticipant(new DummyParticipant(true, 150)); // This participant will timeout.
        coordinator.addParticipant(new DummyParticipant(true, 50));

        boolean result = coordinator.executeTransaction();
        Assert.assertFalse("Transaction should abort due to participant timeout", result);
    }

    // Test concurrent transactions under load.
    @Test
    public void testConcurrentTransactions() throws InterruptedException, ExecutionException {
        final int concurrencyLevel = 5;
        ExecutorService executor = Executors.newFixedThreadPool(concurrencyLevel);

        Callable<Boolean> transactionTask = () -> {
            Coordinator coordinator = new Coordinator();
            coordinator.addParticipant(new DummyParticipant(true, 50));
            coordinator.addParticipant(new DummyParticipant(true, 50));
            return coordinator.executeTransaction();
        };

        Future<Boolean>[] futures = new Future[concurrencyLevel];
        for (int i = 0; i < concurrencyLevel; i++) {
            futures[i] = executor.submit(transactionTask);
        }

        for (int i = 0; i < concurrencyLevel; i++) {
            Assert.assertTrue("Concurrent transaction " + i + " should commit successfully", futures[i].get());
        }
        executor.shutdown();
    }

    // Test coordinator recovery after a simulated failure during transaction execution.
    @Test
    public void testCoordinatorRecovery() {
        Coordinator coordinator = new Coordinator();
        coordinator.addParticipant(new DummyParticipant(true, 50));
        coordinator.addParticipant(new DummyParticipant(true, 50));

        ExecutorService executor = Executors.newSingleThreadExecutor();
        Future<Boolean> future = executor.submit(() -> coordinator.executeTransaction());

        // Simulate coordinator failure shortly after the prepare phase using a separate thread.
        try {
            Thread.sleep(100);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        coordinator.simulateFailure();

        // Simulate coordinator recovery.
        coordinator.recover();

        try {
            boolean result = future.get(500, TimeUnit.MILLISECONDS);
            Assert.assertTrue("Transaction should commit successfully after coordinator recovery", result);
        } catch (Exception e) {
            Assert.fail("Coordinator recovery failed: " + e.getMessage());
        } finally {
            executor.shutdown();
        }
    }
}