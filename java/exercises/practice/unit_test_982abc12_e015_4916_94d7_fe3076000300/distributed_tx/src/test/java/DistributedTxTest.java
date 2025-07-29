package distributed_tx;

import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;
import java.util.*;
import java.util.concurrent.*;

// The following unit tests assume that the solution includes implementations for
// the following classes/interfaces:
// - Bank: an interface with methods prepare(String transactionId, String accountId, double amount),
//         commit(String transactionId, String accountId, double amount), and
//         rollback(String transactionId, String accountId, double amount).
// - TransactionOperation: a class representing an operation on a bank account, with a constructor
//         TransactionOperation(String accountId, double amount).
// - TransactionResult: a class representing the outcome of a transaction, with a method isCommitted()
//         returning true if the transaction committed and false if it was rolled back.
// - TransactionCoordinator: a class coordinating distributed transactions with constructors and methods:
//         TransactionCoordinator(List<Bank> banks) and TransactionCoordinator(List<Bank> banks, long timeoutMillis)
//         to set a transaction timeout, executeTransaction(String transactionId, Map<String, TransactionOperation> operations)
//         to execute a distributed transaction, getLeader() to return the current leader Bank, and
//         simulateLeaderFailure(Bank leader) to simulate the failure of the current leader.
// 
// These tests simulate various scenarios such as successful transactions, failures due to prepare issues,
// leader election recovery, transaction timeouts, and concurrent transaction processing.

public class DistributedTxTest {

    // A fake implementation of the Bank interface for testing purposes.
    private static class FakeBank implements Bank {
        private final String name;
        private final boolean prepareSuccess;
        private final long delayMillis;

        public FakeBank(String name, boolean prepareSuccess, long delayMillis) {
            this.name = name;
            this.prepareSuccess = prepareSuccess;
            this.delayMillis = delayMillis;
        }

        @Override
        public boolean prepare(String transactionId, String accountId, double amount) {
            try {
                Thread.sleep(delayMillis);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            return prepareSuccess;
        }

        @Override
        public boolean commit(String transactionId, String accountId, double amount) {
            return true;
        }

        @Override
        public boolean rollback(String transactionId, String accountId, double amount) {
            return true;
        }

        public String getName() {
            return name;
        }

        @Override
        public String toString() {
            return name;
        }
    }

    @Test
    public void testSuccessfulTransaction() {
        List<Bank> banks = new ArrayList<>();
        banks.add(new FakeBank("BankA", true, 0));
        banks.add(new FakeBank("BankB", true, 0));
        banks.add(new FakeBank("BankC", true, 0));

        TransactionCoordinator coordinator = new TransactionCoordinator(banks);
        Map<String, TransactionOperation> operations = new HashMap<>();
        operations.put("BankA", new TransactionOperation("account1", 100.0));
        operations.put("BankB", new TransactionOperation("account2", 150.0));
        operations.put("BankC", new TransactionOperation("account3", 200.0));

        TransactionResult result = coordinator.executeTransaction("tx_success", operations);
        assertTrue(result.isCommitted(), "Transaction should be committed successfully.");
    }

    @Test
    public void testFailedTransactionDueToPrepareFailure() {
        List<Bank> banks = new ArrayList<>();
        banks.add(new FakeBank("BankA", true, 0));
        // BankB fails to prepare
        banks.add(new FakeBank("BankB", false, 0));
        banks.add(new FakeBank("BankC", true, 0));

        TransactionCoordinator coordinator = new TransactionCoordinator(banks);
        Map<String, TransactionOperation> operations = new HashMap<>();
        operations.put("BankA", new TransactionOperation("account1", 100.0));
        operations.put("BankB", new TransactionOperation("account2", 150.0));
        operations.put("BankC", new TransactionOperation("account3", 200.0));

        TransactionResult result = coordinator.executeTransaction("tx_fail", operations);
        assertFalse(result.isCommitted(), "Transaction should be rolled back due to a prepare failure.");
    }

    @Test
    public void testLeaderElectionRecovery() {
        List<Bank> banks = new ArrayList<>();
        banks.add(new FakeBank("BankA", true, 0));
        banks.add(new FakeBank("BankB", true, 0));
        banks.add(new FakeBank("BankC", true, 0));

        TransactionCoordinator coordinator = new TransactionCoordinator(banks);
        // Initial leader election assumed to have taken place
        Bank initialLeader = coordinator.getLeader();
        assertNotNull(initialLeader, "An initial leader should be elected.");

        // Simulate leader failure and trigger a new election
        coordinator.simulateLeaderFailure(initialLeader);

        Bank newLeader = coordinator.getLeader();
        assertNotNull(newLeader, "A new leader should be elected after leader failure.");
        assertNotEquals(initialLeader, newLeader, "The new leader must be different from the failed leader.");
    }

    @Test
    @Timeout(5)
    public void testTimeoutTransaction() {
        List<Bank> banks = new ArrayList<>();
        // Simulate a slow bank to trigger timeout
        banks.add(new FakeBank("BankA", true, 0));
        banks.add(new FakeBank("BankB", true, 3000)); // delay of 3000ms
        banks.add(new FakeBank("BankC", true, 0));

        // Set transaction timeout to 2000ms
        TransactionCoordinator coordinator = new TransactionCoordinator(banks, 2000);
        Map<String, TransactionOperation> operations = new HashMap<>();
        operations.put("BankA", new TransactionOperation("account1", 100.0));
        operations.put("BankB", new TransactionOperation("account2", 150.0));
        operations.put("BankC", new TransactionOperation("account3", 200.0));

        TransactionResult result = coordinator.executeTransaction("tx_timeout", operations);
        assertFalse(result.isCommitted(), "Transaction should be rolled back due to timeout.");
    }

    @Test
    public void testConcurrentTransactions() throws InterruptedException, ExecutionException {
        List<Bank> banks = new ArrayList<>();
        banks.add(new FakeBank("BankA", true, 0));
        banks.add(new FakeBank("BankB", true, 0));
        banks.add(new FakeBank("BankC", true, 0));

        final TransactionCoordinator coordinator = new TransactionCoordinator(banks);
        ExecutorService executor = Executors.newFixedThreadPool(5);
        List<Callable<TransactionResult>> tasks = new ArrayList<>();

        for (int i = 0; i < 10; i++) {
            final int txnId = i;
            tasks.add(() -> {
                Map<String, TransactionOperation> ops = new HashMap<>();
                ops.put("BankA", new TransactionOperation("account1", 50.0 + txnId));
                ops.put("BankB", new TransactionOperation("account2", 70.0 + txnId));
                ops.put("BankC", new TransactionOperation("account3", 90.0 + txnId));
                return coordinator.executeTransaction("tx_concurrent_" + txnId, ops);
            });
        }

        List<Future<TransactionResult>> futures = executor.invokeAll(tasks);
        executor.shutdown();
        for (Future<TransactionResult> future : futures) {
            TransactionResult res = future.get();
            assertTrue(res.isCommitted(), "All concurrent transactions should be committed successfully.");
        }
    }
}