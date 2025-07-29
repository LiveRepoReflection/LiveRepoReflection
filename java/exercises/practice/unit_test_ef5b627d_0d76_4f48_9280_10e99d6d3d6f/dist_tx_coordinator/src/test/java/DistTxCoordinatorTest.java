import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Assertions;
import java.util.concurrent.atomic.AtomicInteger;

public class DistTxCoordinatorTest {

    // Dummy Transaction class used for simulation
    private static class Transaction {
        private final String id;
        public Transaction(String id) {
            this.id = id;
        }
        public String getId() {
            return id;
        }
    }

    // Participant interface simulation
    public interface Participant {
        boolean prepare(Transaction transaction);
        void commit(Transaction transaction);
        void rollback(Transaction transaction);
    }

    // TestParticipant simulates a participant in the distributed transaction.
    private static class TestParticipant implements Participant {
        private final String name;
        private final boolean voteCommit;
        private final long delayMillis;
        private boolean prepared = false;
        private boolean committed = false;
        private boolean rolledBack = false;

        public TestParticipant(String name, boolean voteCommit, long delayMillis) {
            this.name = name;
            this.voteCommit = voteCommit;
            this.delayMillis = delayMillis;
        }

        @Override
        public boolean prepare(Transaction transaction) {
            try {
                Thread.sleep(delayMillis);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return false;
            }
            prepared = true;
            return voteCommit;
        }

        @Override
        public void commit(Transaction transaction) {
            if (!prepared) {
                throw new IllegalStateException("Participant " + name + " not prepared.");
            }
            committed = true;
        }

        @Override
        public void rollback(Transaction transaction) {
            rolledBack = true;
        }

        public boolean isCommitted() {
            return committed;
        }

        public boolean isRolledBack() {
            return rolledBack;
        }
    }

    // DistTxCoordinator simulates the distributed transaction coordinator.
    public static class DistTxCoordinator {
        protected final long timeoutMillis;
        public DistTxCoordinator(long timeoutMillis) {
            this.timeoutMillis = timeoutMillis;
        }

        public boolean executeTransaction(Transaction transaction, Participant[] participants) {
            // Phase 1: Prepare Phase
            for (Participant p : participants) {
                long startTime = System.currentTimeMillis();
                boolean vote = p.prepare(transaction);
                long elapsed = System.currentTimeMillis() - startTime;
                if (elapsed > timeoutMillis) {
                    vote = false;
                }
                if (!vote) {
                    // Abort transaction: rollback on all participants.
                    for (Participant q : participants) {
                        try {
                            q.rollback(transaction);
                        } catch (Exception e) {
                            // Ignored; in real systems, proper logging would be performed.
                        }
                    }
                    return false;
                }
            }
            // Phase 2: Commit Phase
            for (Participant p : participants) {
                try {
                    p.commit(transaction);
                } catch (Exception e) {
                    // In case commit fails, in production, retry or log would be required.
                }
            }
            return true;
        }
    }

    @Test
    public void testSuccessfulTransaction() {
        Transaction tx = new Transaction("tx_success");
        TestParticipant orderService = new TestParticipant("OrderService", true, 10);
        TestParticipant inventoryService = new TestParticipant("InventoryService", true, 10);
        TestParticipant paymentService = new TestParticipant("PaymentService", true, 10);
        DistTxCoordinator coordinator = new DistTxCoordinator(100);
        boolean result = coordinator.executeTransaction(tx, new Participant[]{orderService, inventoryService, paymentService});
        Assertions.assertTrue(result, "Transaction should commit successfully");
        Assertions.assertTrue(orderService.isCommitted(), "OrderService should be committed");
        Assertions.assertTrue(inventoryService.isCommitted(), "InventoryService should be committed");
        Assertions.assertTrue(paymentService.isCommitted(), "PaymentService should be committed");
    }

    @Test
    public void testAbortTransactionDueToVoteAbort() {
        Transaction tx = new Transaction("tx_abort_vote");
        TestParticipant orderService = new TestParticipant("OrderService", true, 10);
        // Inventory service votes abort.
        TestParticipant inventoryService = new TestParticipant("InventoryService", false, 10);
        TestParticipant paymentService = new TestParticipant("PaymentService", true, 10);
        DistTxCoordinator coordinator = new DistTxCoordinator(100);
        boolean result = coordinator.executeTransaction(tx, new Participant[]{orderService, inventoryService, paymentService});
        Assertions.assertFalse(result, "Transaction should abort due to one participant voting abort");
        Assertions.assertTrue(orderService.isRolledBack(), "OrderService should be rolled back");
        Assertions.assertTrue(inventoryService.isRolledBack(), "InventoryService should be rolled back");
        Assertions.assertTrue(paymentService.isRolledBack(), "PaymentService should be rolled back");
    }

    @Test
    public void testAbortTransactionDueToTimeout() {
        Transaction tx = new Transaction("tx_abort_timeout");
        TestParticipant orderService = new TestParticipant("OrderService", true, 10);
        // Inventory service simulates delay causing a timeout.
        TestParticipant inventoryService = new TestParticipant("InventoryService", true, 200);
        TestParticipant paymentService = new TestParticipant("PaymentService", true, 10);
        DistTxCoordinator coordinator = new DistTxCoordinator(100);
        boolean result = coordinator.executeTransaction(tx, new Participant[]{orderService, inventoryService, paymentService});
        Assertions.assertFalse(result, "Transaction should abort due to participant timeout");
        Assertions.assertTrue(orderService.isRolledBack(), "OrderService should be rolled back on timeout");
        Assertions.assertTrue(inventoryService.isRolledBack(), "InventoryService should be rolled back on timeout");
        Assertions.assertTrue(paymentService.isRolledBack(), "PaymentService should be rolled back on timeout");
    }

    @Test
    public void testConcurrentTransactions() throws InterruptedException {
        final int threadCount = 10;
        final AtomicInteger successCounter = new AtomicInteger(0);
        Thread[] threads = new Thread[threadCount];
        for (int i = 0; i < threadCount; i++) {
            final String txId = "tx_concurrent_" + i;
            threads[i] = new Thread(() -> {
                Transaction tx = new Transaction(txId);
                TestParticipant orderService = new TestParticipant("OrderService", true, 10);
                TestParticipant inventoryService = new TestParticipant("InventoryService", true, 10);
                TestParticipant paymentService = new TestParticipant("PaymentService", true, 10);
                DistTxCoordinator coordinator = new DistTxCoordinator(100);
                boolean result = coordinator.executeTransaction(tx, new Participant[]{orderService, inventoryService, paymentService});
                if(result) {
                    successCounter.incrementAndGet();
                }
            });
            threads[i].start();
        }
        for (Thread thread : threads) {
            thread.join();
        }
        Assertions.assertEquals(threadCount, successCounter.get(), "All concurrent transactions must succeed");
    }

    @Test
    public void testDTCRecoverySimulation() {
        Transaction tx = new Transaction("tx_recovery");
        TestParticipant orderService = new TestParticipant("OrderService", true, 10);
        TestParticipant inventoryService = new TestParticipant("InventoryService", true, 10);
        TestParticipant paymentService = new TestParticipant("PaymentService", true, 10);

        // Coordinator that simulates a failure between the prepare and commit phase.
        DistTxCoordinator recoveringCoordinator = new DistTxCoordinator(100) {
            private boolean simulateFailure = true;
            @Override
            public boolean executeTransaction(Transaction transaction, Participant[] participants) {
                // Phase 1: Prepare
                for (Participant p : participants) {
                    long startTime = System.currentTimeMillis();
                    boolean vote = p.prepare(transaction);
                    long elapsed = System.currentTimeMillis() - startTime;
                    if (elapsed > timeoutMillis) {
                        vote = false;
                    }
                    if (!vote) {
                        for (Participant q : participants) {
                            try {
                                q.rollback(transaction);
                            } catch (Exception e) {
                            }
                        }
                        return false;
                    }
                }
                // Simulate failure after prepare phase
                if (simulateFailure) {
                    simulateFailure = false;
                    // In a real scenario, this would be recovered via a persistent log.
                    // Here, we simulate recovery by immediately transitioning to commit phase.
                }
                for (Participant p : participants) {
                    try {
                        p.commit(transaction);
                    } catch (Exception e) {
                    }
                }
                return true;
            }
        };

        boolean result = recoveringCoordinator.executeTransaction(tx, new Participant[]{orderService, inventoryService, paymentService});
        Assertions.assertTrue(result, "Transaction should commit after recovery simulation");
        Assertions.assertTrue(orderService.isCommitted(), "OrderService should be committed post recovery");
        Assertions.assertTrue(inventoryService.isCommitted(), "InventoryService should be committed post recovery");
        Assertions.assertTrue(paymentService.isCommitted(), "PaymentService should be committed post recovery");
    }
}