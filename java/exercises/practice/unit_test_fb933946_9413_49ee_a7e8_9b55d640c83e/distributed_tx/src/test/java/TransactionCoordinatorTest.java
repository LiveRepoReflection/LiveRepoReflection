import org.junit.jupiter.api.*;
import java.util.*;
import java.util.concurrent.*;
import static org.junit.jupiter.api.Assertions.*;

class TransactionCoordinatorTest {

    // Dummy implementation for simulating a banking service participant.
    static class DummyParticipant {
        String serviceName;
        boolean prepared = false;
        boolean committed = false;
        boolean rolledBack = false;
        long responseDelay; // in milliseconds

        // Flag to simulate a failure during prepare.
        boolean failPrepare = false;

        public DummyParticipant(String serviceName) {
            this(serviceName, 0L, false);
        }

        public DummyParticipant(String serviceName, long responseDelay, boolean failPrepare) {
            this.serviceName = serviceName;
            this.responseDelay = responseDelay;
            this.failPrepare = failPrepare;
        }

        // Simulate the prepare phase.
        public synchronized String prepare() {
            try {
                if (responseDelay > 0) {
                    Thread.sleep(responseDelay);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            if (failPrepare) {
                return "abort";
            } else {
                prepared = true;
                return "prepared";
            }
        }

        // Simulate the commit phase.
        public synchronized void commit() {
            committed = true;
        }

        // Simulate the rollback phase.
        public synchronized void rollback() {
            rolledBack = true;
        }
    }

    // Dummy implementation of a Distributed Transaction Coordinator.
    // This coordinator implements a simplified two-phase commit protocol.
    static class DummyTransactionCoordinator {
        Map<String, List<DummyParticipant>> transactions = new ConcurrentHashMap<>();
        long timeoutMillis = 500; // default timeout for participant responses

        // Executes a transaction using the 2PC protocol.
        // Returns true if the transaction commits, false if it rolls back.
        public boolean executeTransaction(String transactionId, List<DummyParticipant> participants) {
            transactions.put(transactionId, participants);
            ExecutorService executor = Executors.newFixedThreadPool(participants.size());
            List<Future<String>> prepareFutures = new ArrayList<>();
            for (DummyParticipant p : participants) {
                Future<String> future = executor.submit(p::prepare);
                prepareFutures.add(future);
            }
            boolean allPrepared = true;
            for (Future<String> future : prepareFutures) {
                try {
                    String result = future.get(timeoutMillis, TimeUnit.MILLISECONDS);
                    if (!"prepared".equals(result)) {
                        allPrepared = false;
                    }
                } catch (TimeoutException e) {
                    allPrepared = false;
                } catch (Exception e) {
                    allPrepared = false;
                }
            }
            // Execute phase 2: commit if all participants are prepared, otherwise rollback.
            if (allPrepared) {
                for (DummyParticipant p : participants) {
                    p.commit();
                }
            } else {
                for (DummyParticipant p : participants) {
                    p.rollback();
                }
            }
            executor.shutdown();
            return allPrepared;
        }

        // Simulates recovery after a crash by re-executing pending transactions.
        // If participants were prepared, commits; otherwise, rolls back.
        public boolean recoverAndExecute(String transactionId) {
            List<DummyParticipant> participants = transactions.get(transactionId);
            if (participants == null) {
                return false;
            }
            boolean anyNotPrepared = participants.stream().anyMatch(p -> !p.prepared);
            if (anyNotPrepared) {
                for (DummyParticipant p : participants) {
                    p.rollback();
                }
                return false;
            } else {
                for (DummyParticipant p : participants) {
                    p.commit();
                }
                return true;
            }
        }
    }

    @Test
    public void testSuccessfulTransaction() {
        // All participants respond with 'prepared', so the transaction commits.
        DummyTransactionCoordinator coordinator = new DummyTransactionCoordinator();
        DummyParticipant p1 = new DummyParticipant("BankA");
        DummyParticipant p2 = new DummyParticipant("BankB");
        List<DummyParticipant> participants = Arrays.asList(p1, p2);

        boolean result = coordinator.executeTransaction("tx1", participants);
        assertTrue(result, "Transaction should commit successfully");
        assertTrue(p1.committed, "BankA should commit");
        assertTrue(p2.committed, "BankB should commit");
        assertFalse(p1.rolledBack, "BankA should not rollback");
        assertFalse(p2.rolledBack, "BankB should not rollback");
    }

    @Test
    public void testPreparationFailure() {
        // One participant fails during the prepare phase, forcing a rollback.
        DummyTransactionCoordinator coordinator = new DummyTransactionCoordinator();
        DummyParticipant p1 = new DummyParticipant("BankA");
        DummyParticipant p2 = new DummyParticipant("BankB", 0, true);
        List<DummyParticipant> participants = Arrays.asList(p1, p2);

        boolean result = coordinator.executeTransaction("tx2", participants);
        assertFalse(result, "Transaction should roll back due to preparation failure");
        assertFalse(p1.committed, "BankA should not commit");
        assertFalse(p2.committed, "BankB should not commit");
        assertTrue(p1.rolledBack, "BankA should rollback");
        assertTrue(p2.rolledBack, "BankB should rollback");
    }

    @Test
    public void testTimeout() {
        // One participant delays response beyond the timeout threshold, triggering rollback.
        DummyTransactionCoordinator coordinator = new DummyTransactionCoordinator();
        DummyParticipant p1 = new DummyParticipant("BankA");
        DummyParticipant p2 = new DummyParticipant("BankB", 600, false);
        List<DummyParticipant> participants = Arrays.asList(p1, p2);

        boolean result = coordinator.executeTransaction("tx3", participants);
        assertFalse(result, "Transaction should roll back due to timeout");
        assertFalse(p1.committed, "BankA should not commit due to timeout");
        assertFalse(p2.committed, "BankB should not commit due to timeout");
        assertTrue(p1.rolledBack, "BankA should rollback");
        assertTrue(p2.rolledBack, "BankB should rollback");
    }

    @Test
    public void testDuplicateCommitRollback() {
        // Test idempotency: Duplicate calls to commit or rollback should not alter the outcome.
        DummyTransactionCoordinator coordinator = new DummyTransactionCoordinator();
        DummyParticipant p1 = new DummyParticipant("BankA");
        DummyParticipant p2 = new DummyParticipant("BankB", 0, true);
        List<DummyParticipant> participants = Arrays.asList(p1, p2);

        boolean result = coordinator.executeTransaction("tx4", participants);
        assertFalse(result, "Transaction should roll back due to a failure");
        // Invoke duplicate rollback calls.
        p1.rollback();
        p1.rollback();
        p2.rollback();
        p2.rollback();
        assertTrue(p1.rolledBack, "BankA should remain rolled back");
        assertTrue(p2.rolledBack, "BankB should remain rolled back");
        assertFalse(p1.committed, "BankA should not commit");
        assertFalse(p2.committed, "BankB should not commit");
    }

    @Test
    public void testConcurrentTransactions() throws Exception {
        // Test handling multiple concurrent transactions.
        DummyTransactionCoordinator coordinator = new DummyTransactionCoordinator();
        final int numTransactions = 10;
        ExecutorService executorService = Executors.newFixedThreadPool(numTransactions);
        List<Callable<Boolean>> tasks = new ArrayList<>();

        for (int i = 0; i < numTransactions; i++) {
            final String txId = "tx_concurrent_" + i;
            tasks.add(() -> {
                DummyParticipant p1 = new DummyParticipant("BankA");
                DummyParticipant p2 = new DummyParticipant("BankB");
                List<DummyParticipant> participants = Arrays.asList(p1, p2);
                return coordinator.executeTransaction(txId, participants);
            });
        }
        List<Future<Boolean>> results = executorService.invokeAll(tasks);
        for (Future<Boolean> future : results) {
            assertTrue(future.get(), "Each concurrent transaction should commit successfully");
        }
        executorService.shutdown();
    }

    @Test
    public void testCrashRecovery() {
        // Simulate a crash and recovery scenario.
        DummyTransactionCoordinator coordinator = new DummyTransactionCoordinator();
        DummyParticipant p1 = new DummyParticipant("BankA");
        DummyParticipant p2 = new DummyParticipant("BankB");
        List<DummyParticipant> participants = Arrays.asList(p1, p2);
        // Simulate that participants have completed the prepare phase before the crash.
        p1.prepared = true;
        p2.prepared = true;
        // Persist the state for a transaction.
        coordinator.transactions.put("tx5", participants);
        // Simulate recovery and re-execution.
        boolean recoveredResult = coordinator.recoverAndExecute("tx5");
        assertTrue(recoveredResult, "Recovered transaction should commit successfully");
        assertTrue(p1.committed, "BankA should commit after recovery");
        assertTrue(p2.committed, "BankB should commit after recovery");
    }
}