package distributed_tx;

import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;
import java.util.concurrent.*;
import java.util.*;

class DistributedTxTest {

    // A mock participant simulating a service in the transaction.
    static class MockParticipant {
        private final String name;
        private final boolean prepareSuccess;
        private final long delayInMillis; // simulate delay for timeout testing
        private boolean committed;
        private boolean rolledBack;

        public MockParticipant(String name, boolean prepareSuccess, long delayInMillis) {
            this.name = name;
            this.prepareSuccess = prepareSuccess;
            this.delayInMillis = delayInMillis;
            this.committed = false;
            this.rolledBack = false;
        }

        // Simulate the prepare phase.
        public boolean prepare() {
            if (delayInMillis > 0) {
                try {
                    Thread.sleep(delayInMillis);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    return false;
                }
            }
            return prepareSuccess;
        }

        public void commit() {
            this.committed = true;
        }

        public void rollback() {
            this.rolledBack = true;
        }

        public boolean isCommitted() {
            return committed;
        }

        public boolean isRolledBack() {
            return rolledBack;
        }

        public String getName() {
            return name;
        }
    }

    // Define a transaction operation interface that the Distributed Transaction Manager will use.
    interface TransactionOperation {
        boolean prepare();
        void commit();
        void rollback();
        void execute(); // Execute the actual operation logic.
    }

    // Adapter to wrap a MockParticipant as a TransactionOperation.
    static class ParticipantOperation implements TransactionOperation {
        private final MockParticipant participant;
        private final Runnable operation;

        public ParticipantOperation(MockParticipant participant, Runnable operation) {
            this.participant = participant;
            this.operation = operation;
        }

        @Override
        public boolean prepare() {
            return participant.prepare();
        }

        @Override
        public void commit() {
            participant.commit();
        }

        @Override
        public void rollback() {
            participant.rollback();
        }

        @Override
        public void execute() {
            operation.run();
        }
    }

    // A simplified in-memory Distributed Transaction Manager implementing a two-phase commit.
    // This mock implementation is used for testing purposes.
    static class DistributedTransactionManager {
        private final List<TransactionOperation> operations = new ArrayList<>();
        private final long phaseTimeoutMillis;

        public DistributedTransactionManager(long phaseTimeoutMillis) {
            this.phaseTimeoutMillis = phaseTimeoutMillis;
        }

        public void addOperation(TransactionOperation op) {
            operations.add(op);
        }

        // Executes the two-phase commit protocol.
        // Returns true if all participants commit, false if rolled back.
        public boolean executeTransaction() {
            ExecutorService executor = Executors.newFixedThreadPool(operations.size());
            try {
                // Prepare phase: execute each operation's prepare logic concurrently.
                List<Future<Boolean>> prepareResults = new ArrayList<>();
                for (TransactionOperation op : operations) {
                    Future<Boolean> future = executor.submit(() -> {
                        // Execute the operation's business logic, if any.
                        op.execute();
                        return op.prepare();
                    });
                    prepareResults.add(future);
                }

                // Wait for each participant to respond.
                for (Future<Boolean> future : prepareResults) {
                    try {
                        boolean prepared = future.get(phaseTimeoutMillis, TimeUnit.MILLISECONDS);
                        if (!prepared) {
                            rollbackAll();
                            return false;
                        }
                    } catch (TimeoutException | InterruptedException | ExecutionException e) {
                        rollbackAll();
                        return false;
                    }
                }

                // Commit phase: commit for each participant.
                for (TransactionOperation op : operations) {
                    op.commit();
                }
                return true;
            } finally {
                executor.shutdownNow();
            }
        }

        private void rollbackAll() {
            for (TransactionOperation op : operations) {
                op.rollback();
            }
        }
    }

    @Test
    void testSuccessfulTransaction() {
        DistributedTransactionManager dtm = new DistributedTransactionManager(1000);

        MockParticipant participant1 = new MockParticipant("Inventory", true, 0);
        MockParticipant participant2 = new MockParticipant("Payment", true, 0);
        MockParticipant participant3 = new MockParticipant("Order", true, 0);

        dtm.addOperation(new ParticipantOperation(participant1, () -> {}));
        dtm.addOperation(new ParticipantOperation(participant2, () -> {}));
        dtm.addOperation(new ParticipantOperation(participant3, () -> {}));

        boolean result = dtm.executeTransaction();
        assertTrue(result, "Transaction should commit successfully.");
        assertTrue(participant1.isCommitted(), "Inventory participant should be committed.");
        assertTrue(participant2.isCommitted(), "Payment participant should be committed.");
        assertTrue(participant3.isCommitted(), "Order participant should be committed.");
        assertFalse(participant1.isRolledBack(), "Inventory participant should not be rolled back.");
        assertFalse(participant2.isRolledBack(), "Payment participant should not be rolled back.");
        assertFalse(participant3.isRolledBack(), "Order participant should not be rolled back.");
    }

    @Test
    void testFailedTransactionDueToPrepare() {
        DistributedTransactionManager dtm = new DistributedTransactionManager(1000);

        MockParticipant participant1 = new MockParticipant("Inventory", true, 0);
        // This participant fails in the prepare phase.
        MockParticipant participant2 = new MockParticipant("Payment", false, 0);
        MockParticipant participant3 = new MockParticipant("Order", true, 0);

        dtm.addOperation(new ParticipantOperation(participant1, () -> {}));
        dtm.addOperation(new ParticipantOperation(participant2, () -> {}));
        dtm.addOperation(new ParticipantOperation(participant3, () -> {}));

        boolean result = dtm.executeTransaction();
        assertFalse(result, "Transaction should roll back due to a prepare failure.");
        assertTrue(participant1.isRolledBack(), "Inventory participant should be rolled back.");
        assertTrue(participant2.isRolledBack(), "Payment participant should be rolled back.");
        assertTrue(participant3.isRolledBack(), "Order participant should be rolled back.");
        assertFalse(participant1.isCommitted(), "Inventory participant should not be committed.");
        assertFalse(participant2.isCommitted(), "Payment participant should not be committed.");
        assertFalse(participant3.isCommitted(), "Order participant should not be committed.");
    }

    @Test
    void testTransactionTimeout() {
        // Set a timeout of 500ms; introduce a delay greater than that in one participant.
        DistributedTransactionManager dtm = new DistributedTransactionManager(500);

        // This participant simulates a delay causing a timeout.
        MockParticipant participant1 = new MockParticipant("Inventory", true, 600);
        MockParticipant participant2 = new MockParticipant("Payment", true, 0);

        dtm.addOperation(new ParticipantOperation(participant1, () -> {}));
        dtm.addOperation(new ParticipantOperation(participant2, () -> {}));

        boolean result = dtm.executeTransaction();
        assertFalse(result, "Transaction should be rolled back due to prepare timeout.");
        assertTrue(participant1.isRolledBack(), "Inventory participant should be rolled back.");
        assertTrue(participant2.isRolledBack(), "Payment participant should be rolled back.");
    }

    @Test
    void testConcurrentTransactions() throws InterruptedException {
        int numTransactions = 10;
        ExecutorService executor = Executors.newFixedThreadPool(numTransactions);
        List<Future<Boolean>> futures = new ArrayList<>();

        for (int i = 0; i < numTransactions; i++) {
            futures.add(executor.submit(() -> {
                DistributedTransactionManager dtm = new DistributedTransactionManager(1000);
                MockParticipant participant1 = new MockParticipant("Inventory", true, 0);
                MockParticipant participant2 = new MockParticipant("Payment", true, 0);
                MockParticipant participant3 = new MockParticipant("Order", true, 0);

                dtm.addOperation(new ParticipantOperation(participant1, () -> {}));
                dtm.addOperation(new ParticipantOperation(participant2, () -> {}));
                dtm.addOperation(new ParticipantOperation(participant3, () -> {}));

                return dtm.executeTransaction();
            }));
        }

        int successCount = 0;
        for (Future<Boolean> future : futures) {
            try {
                if (future.get(2, TimeUnit.SECONDS)) {
                    successCount++;
                }
            } catch (Exception e) {
                // Exception handling: treat as failure.
            }
        }
        executor.shutdownNow();
        assertEquals(numTransactions, successCount, "All concurrent transactions should commit successfully.");
    }
}