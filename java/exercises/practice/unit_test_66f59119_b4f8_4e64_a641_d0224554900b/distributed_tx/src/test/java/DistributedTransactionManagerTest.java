package distributed_tx;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Assertions;

import java.util.concurrent.CompletionService;
import java.util.concurrent.Executors;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.ExecutorCompletionService;

public class DistributedTransactionManagerTest {

    @Test
    public void testSuccessfulTransaction() throws Exception {
        // Setup dummy participants that indicate a successful prepare phase.
        DummyParticipantA serviceA = new DummyParticipantA(true, false);
        DummyParticipantB serviceB = new DummyParticipantB(true, false);
        DistributedTransactionManager dtm = new DistributedTransactionManager();
        dtm.registerParticipant(serviceA);
        dtm.registerParticipant(serviceB);

        // Create a transaction to transfer funds.
        Transaction transaction = new Transaction("tx1", 100, "A", "B");
        TransactionResult result = dtm.executeTransaction(transaction);
        Assertions.assertEquals(TransactionStatus.COMMITTED, result.getStatus(), "Transaction should be committed");
    }

    @Test
    public void testAbortTransactionDueToPrepareFailure() throws Exception {
        // Setup one participant to fail during prepare phase (simulate insufficient funds or error).
        DummyParticipantA serviceA = new DummyParticipantA(true, false);
        DummyParticipantB serviceB = new DummyParticipantB(false, false);
        DistributedTransactionManager dtm = new DistributedTransactionManager();
        dtm.registerParticipant(serviceA);
        dtm.registerParticipant(serviceB);

        Transaction transaction = new Transaction("tx2", 200, "A", "B");
        TransactionResult result = dtm.executeTransaction(transaction);
        Assertions.assertEquals(TransactionStatus.ABORTED, result.getStatus(), "Transaction should be aborted due to a prepare failure");
    }

    @Test
    public void testTimeoutDuringPrepare() throws Exception {
        // Setup one participant to simulate a timeout by delaying response.
        DummyParticipantA serviceA = new DummyParticipantA(true, false);
        DummyParticipantB serviceB = new DummyParticipantB(true, true);  // simulate timeout scenario
        DistributedTransactionManager dtm = new DistributedTransactionManager();
        dtm.registerParticipant(serviceA);
        dtm.registerParticipant(serviceB);

        Transaction transaction = new Transaction("tx3", 150, "A", "B");
        TransactionResult result = dtm.executeTransaction(transaction);
        Assertions.assertEquals(TransactionStatus.ABORTED, result.getStatus(), "Transaction should be aborted due to timeout during prepare phase");
    }

    @Test
    public void testConcurrentTransactions() throws Exception {
        // Setup participants that commit successfully.
        DummyParticipantA serviceA = new DummyParticipantA(true, false);
        DummyParticipantB serviceB = new DummyParticipantB(true, false);
        DistributedTransactionManager dtm = new DistributedTransactionManager();
        dtm.registerParticipant(serviceA);
        dtm.registerParticipant(serviceB);

        ExecutorService executor = Executors.newFixedThreadPool(5);
        int numTransactions = 10;
        CompletionService<TransactionResult> completionService = new ExecutorCompletionService<>(executor);

        for (int i = 0; i < numTransactions; i++) {
            final int txId = i;
            completionService.submit(() -> {
                Transaction tx = new Transaction("tx-" + txId, 50 + txId, "A", "B");
                return dtm.executeTransaction(tx);
            });
        }

        int committedCount = 0;
        int abortedCount = 0;
        for (int i = 0; i < numTransactions; i++) {
            TransactionResult res = completionService.take().get();
            if (res.getStatus() == TransactionStatus.COMMITTED) {
                committedCount++;
            } else {
                abortedCount++;
            }
        }
        executor.shutdown();
        Assertions.assertEquals(numTransactions, committedCount, "All concurrent transactions should commit successfully");
    }

    @Test
    public void testDtmRecoveryAfterFailure() throws Exception {
        // Simulate a DTM failure after successful prepare but before commit decision.
        DummyParticipantA serviceA = new DummyParticipantA(true, false);
        DummyParticipantB serviceB = new DummyParticipantB(true, false);
        DistributedTransactionManager dtm = new DistributedTransactionManager();
        dtm.registerParticipant(serviceA);
        dtm.registerParticipant(serviceB);

        Transaction transaction = new Transaction("tx4", 120, "A", "B");
        // Start transaction and simulate sending prepare messages.
        dtm.startTransaction(transaction);
        // At this point, the DTM logs the prepare state.
        // Simulate failure by not sending the final commit/abort decision.
        // Recover the DTM.
        dtm.recover();
        TransactionResult result = dtm.getTransactionResult("tx4");
        Assertions.assertEquals(TransactionStatus.COMMITTED, result.getStatus(), "Recovered transaction should be committed if all participants had prepared successfully");
    }

    @Test
    public void testServiceFailureRecovery() throws Exception {
        // Setup a participant that simulates failure during the commit phase.
        DummyParticipantA serviceA = new DummyParticipantA(true, false);
        DummyParticipantB serviceB = new DummyParticipantB(true, false);
        serviceB.setSimulateCommitFailure(true);

        DistributedTransactionManager dtm = new DistributedTransactionManager();
        dtm.registerParticipant(serviceA);
        dtm.registerParticipant(serviceB);

        Transaction transaction = new Transaction("tx5", 100, "A", "B");
        TransactionResult result = dtm.executeTransaction(transaction);
        // Simulate service recovery; the participant using its persistent log should complete the commit.
        serviceB.recover(transaction);
        Assertions.assertEquals(TransactionStatus.COMMITTED, result.getStatus(), "Transaction should eventually commit after service recovery from commit failure");
    }

    // Dummy participant implementations for unit testing.
    // These classes simulate the behavior of real services participating in the distributed transaction.
    public static class DummyParticipantA implements Participant {
        private boolean prepareSuccess;
        private boolean simulateTimeout;

        public DummyParticipantA(boolean prepareSuccess, boolean simulateTimeout) {
            this.prepareSuccess = prepareSuccess;
            this.simulateTimeout = simulateTimeout;
        }

        @Override
        public ParticipantResponse prepare(Transaction transaction) throws InterruptedException {
            if (simulateTimeout) {
                // Delay response to simulate timeout scenario.
                Thread.sleep(5000);
            }
            return prepareSuccess ? ParticipantResponse.COMMIT : ParticipantResponse.ABORT;
        }

        @Override
        public void commit(Transaction transaction) {
            // Simulated commit action.
        }

        @Override
        public void abort(Transaction transaction) {
            // Simulated abort action.
        }

        @Override
        public void recover(Transaction transaction) {
            // Simulated recovery logic.
        }
    }

    public static class DummyParticipantB implements Participant {
        private boolean prepareSuccess;
        private boolean simulateTimeout;
        private boolean simulateCommitFailure = false;

        public DummyParticipantB(boolean prepareSuccess, boolean simulateTimeout) {
            this.prepareSuccess = prepareSuccess;
            this.simulateTimeout = simulateTimeout;
        }
        
        public void setSimulateCommitFailure(boolean simulateCommitFailure) {
            this.simulateCommitFailure = simulateCommitFailure;
        }

        @Override
        public ParticipantResponse prepare(Transaction transaction) throws InterruptedException {
            if (simulateTimeout) {
                Thread.sleep(5000);
            }
            return prepareSuccess ? ParticipantResponse.COMMIT : ParticipantResponse.ABORT;
        }

        @Override
        public void commit(Transaction transaction) {
            if (simulateCommitFailure) {
                throw new RuntimeException("Simulated commit failure");
            }
            // Simulated commit action.
        }

        @Override
        public void abort(Transaction transaction) {
            // Simulated abort action.
        }

        @Override
        public void recover(Transaction transaction) {
            // Simulated recovery logic.
        }
    }
}