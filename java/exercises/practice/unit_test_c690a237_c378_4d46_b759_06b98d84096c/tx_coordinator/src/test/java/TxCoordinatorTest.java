import org.junit.Test;
import org.junit.Before;
import static org.junit.Assert.*;

import java.util.*;
import java.util.concurrent.*;
import java.io.Serializable;

public class TxCoordinatorTest {

    private Coordinator coordinator;
    private final long TIMEOUT_MS = 1000;

    @Before
    public void setUp() {
        // For each test, the coordinator will be reinitialized.
        // The Coordinator class is assumed to have a constructor that accepts a list of BankServer instances and a timeout.
        coordinator = new Coordinator(TIMEOUT_MS);
    }

    // Test that a transaction commits successfully when all bank servers prepare successfully.
    @Test
    public void testSuccessfulTransaction() throws Exception {
        // Create two mock bank servers that always succeed in the prepare phase.
        MockBankServer bank1 = new MockBankServer(true, 0);
        MockBankServer bank2 = new MockBankServer(true, 0);
        List<BankServer> banks = Arrays.asList(bank1, bank2);

        // Create a transaction with operations targeted to each bank server.
        Map<BankServer, List<Operation>> ops = new HashMap<>();
        ops.put(bank1, Arrays.asList(new Operation("debit", 100)));
        ops.put(bank2, Arrays.asList(new Operation("credit", 100)));
        Transaction tx = new Transaction("tx1", ops);

        // Register the bank servers with the coordinator.
        coordinator.registerBankServers(banks);

        // Execute the transaction using the coordinator.
        boolean result = coordinator.executeTransaction(tx);
        assertTrue("Transaction should commit successfully", result);

        // Verify that commit was called on both bank servers and rollback was not invoked.
        assertTrue("Bank1 should have committed", bank1.isCommitCalled(tx.id));
        assertTrue("Bank2 should have committed", bank2.isCommitCalled(tx.id));
        assertFalse("Bank1 should not have rolled back", bank1.isRollbackCalled(tx.id));
        assertFalse("Bank2 should not have rolled back", bank2.isRollbackCalled(tx.id));
    }

    // Test that a transaction rolls back when one bank server fails during the prepare phase.
    @Test
    public void testFailedTransaction() throws Exception {
        // Create one bank server that succeeds and one that fails in the prepare phase.
        MockBankServer bank1 = new MockBankServer(true, 0);
        MockBankServer bank2 = new MockBankServer(false, 0);
        List<BankServer> banks = Arrays.asList(bank1, bank2);

        // Create a transaction with operations targeted to each bank server.
        Map<BankServer, List<Operation>> ops = new HashMap<>();
        ops.put(bank1, Arrays.asList(new Operation("debit", 50)));
        ops.put(bank2, Arrays.asList(new Operation("credit", 50)));
        Transaction tx = new Transaction("tx2", ops);

        coordinator.registerBankServers(banks);

        // Execute the transaction.
        boolean result = coordinator.executeTransaction(tx);
        assertFalse("Transaction should be rolled back", result);

        // Verify that rollback was called on both bank servers.
        assertTrue("Bank1 should have rolled back", bank1.isRollbackCalled(tx.id));
        assertTrue("Bank2 should have rolled back", bank2.isRollbackCalled(tx.id));
        assertFalse("Bank1 should not have committed", bank1.isCommitCalled(tx.id));
        assertFalse("Bank2 should not have committed", bank2.isCommitCalled(tx.id));
    }

    // Test that a transaction rolls back if any bank server times out during prepare.
    @Test
    public void testTimeoutTransaction() throws Exception {
        // Create one bank server that succeeds and one that delays beyond the timeout.
        MockBankServer bank1 = new MockBankServer(true, 0);
        // Delay longer than TIMEOUT_MS to trigger timeout in prepare.
        MockBankServer bank2 = new MockBankServer(true, TIMEOUT_MS + 500);
        List<BankServer> banks = Arrays.asList(bank1, bank2);

        Map<BankServer, List<Operation>> ops = new HashMap<>();
        ops.put(bank1, Arrays.asList(new Operation("debit", 75)));
        ops.put(bank2, Arrays.asList(new Operation("credit", 75)));
        Transaction tx = new Transaction("tx3", ops);

        coordinator.registerBankServers(banks);

        boolean result = coordinator.executeTransaction(tx);
        assertFalse("Transaction should be rolled back due to timeout", result);

        // Verify that rollback was called on both bank servers.
        assertTrue("Bank1 should have rolled back due to timeout", bank1.isRollbackCalled(tx.id));
        assertTrue("Bank2 should have rolled back due to timeout", bank2.isRollbackCalled(tx.id));
    }

    // Test executing multiple transactions concurrently.
    @Test
    public void testConcurrentTransactions() throws Exception {
        // Create several bank servers that succeed.
        MockBankServer bank1 = new MockBankServer(true, 0);
        MockBankServer bank2 = new MockBankServer(true, 0);
        List<BankServer> banks = Arrays.asList(bank1, bank2);
        coordinator.registerBankServers(banks);

        int numTransactions = 10;
        ExecutorService executor = Executors.newFixedThreadPool(numTransactions);
        List<Future<Boolean>> futures = new ArrayList<>();
        List<Transaction> transactions = new ArrayList<>();

        for (int i = 0; i < numTransactions; i++) {
            String txId = "tx_concurrent_" + i;
            Map<BankServer, List<Operation>> ops = new HashMap<>();
            ops.put(bank1, Arrays.asList(new Operation("debit", 10 + i)));
            ops.put(bank2, Arrays.asList(new Operation("credit", 10 + i)));
            Transaction tx = new Transaction(txId, ops);
            transactions.add(tx);
            futures.add(executor.submit(() -> coordinator.executeTransaction(tx)));
        }

        executor.shutdown();
        executor.awaitTermination(5, TimeUnit.SECONDS);

        // Verify that all transactions committed successfully.
        for (Transaction tx : transactions) {
            assertTrue("Transaction " + tx.id + " should commit successfully", coordinator.getTransactionStatus(tx.id) == TransactionStatus.COMMITTED);
            assertTrue("Bank1 should have committed " + tx.id, bank1.isCommitCalled(tx.id));
            assertTrue("Bank2 should have committed " + tx.id, bank2.isCommitCalled(tx.id));
        }
    }

    // Test crash recovery: simulate persisting state, crashing and then recovering.
    @Test
    public void testCrashRecovery() throws Exception {
        // Create two mock bank servers that always succeed.
        MockBankServer bank1 = new MockBankServer(true, 0);
        MockBankServer bank2 = new MockBankServer(true, 0);
        List<BankServer> banks = Arrays.asList(bank1, bank2);
        coordinator.registerBankServers(banks);

        // Create a transaction but simulate a crash after prepare phase.
        Map<BankServer, List<Operation>> ops = new HashMap<>();
        ops.put(bank1, Arrays.asList(new Operation("debit", 200)));
        ops.put(bank2, Arrays.asList(new Operation("credit", 200)));
        Transaction tx = new Transaction("tx_recovery", ops);

        // Start the transaction in a separate thread and simulate crash recovery mid-operation.
        ExecutorService exec = Executors.newSingleThreadExecutor();
        Future<Boolean> future = exec.submit(() -> coordinator.executeTransaction(tx));

        // Simulate a crash by waiting a short moment and invoking coordinator.persistState(), then reinitializing.
        Thread.sleep(200);
        coordinator.persistState(); // Assume this persists the current state.
        coordinator = Coordinator.recover(TIMEOUT_MS); // Assume this static method recovers the coordinator.
        boolean result = future.get(5, TimeUnit.SECONDS);
        exec.shutdown();

        // The recovered coordinator should complete the transaction.
        assertTrue("Transaction should eventually commit after recovery", result);
        assertTrue("Bank1 should have committed after recovery", bank1.isCommitCalled(tx.id));
        assertTrue("Bank2 should have committed after recovery", bank2.isCommitCalled(tx.id));
    }

    // ----------- Supporting Mock Classes and Enums -----------------

    // Operation class simulates an operation on a bank account.
    public static class Operation implements Serializable {
        public final String type;
        public final int amount;

        public Operation(String type, int amount) {
            this.type = type;
            this.amount = amount;
        }
    }

    // Transaction holds the transaction id and mapping of BankServer to its list of operations.
    public static class Transaction implements Serializable {
        public final String id;
        public final Map<BankServer, List<Operation>> bankOperations;

        public Transaction(String id, Map<BankServer, List<Operation>> bankOperations) {
            this.id = id;
            this.bankOperations = bankOperations;
        }
    }

    // Enum to represent the status of a transaction.
    public enum TransactionStatus {
        COMMITTED,
        ROLLEDBACK,
        PENDING
    }

    // BankServer interface as expected by the coordinator.
    public interface BankServer {
        boolean prepare(String transactionId, List<Operation> operations) throws Exception;
        void commit(String transactionId);
        void rollback(String transactionId);
    }

    // MockBankServer simulates a bank server with controllable behavior for testing.
    public static class MockBankServer implements BankServer {
        private final boolean prepareSuccess;
        private final long responseDelayMs;
        // Maps to track which transactions had commit or rollback called.
        private final Map<String, Boolean> commitMap = new ConcurrentHashMap<>();
        private final Map<String, Boolean> rollbackMap = new ConcurrentHashMap<>();

        public MockBankServer(boolean prepareSuccess, long responseDelayMs) {
            this.prepareSuccess = prepareSuccess;
            this.responseDelayMs = responseDelayMs;
        }

        @Override
        public boolean prepare(String transactionId, List<Operation> operations) throws Exception {
            if (responseDelayMs > 0) {
                Thread.sleep(responseDelayMs);
            }
            return prepareSuccess;
        }

        @Override
        public void commit(String transactionId) {
            commitMap.put(transactionId, true);
        }

        @Override
        public void rollback(String transactionId) {
            rollbackMap.put(transactionId, true);
        }

        public boolean isCommitCalled(String transactionId) {
            return commitMap.getOrDefault(transactionId, false);
        }

        public boolean isRollbackCalled(String transactionId) {
            return rollbackMap.getOrDefault(transactionId, false);
        }
    }

    // Stub Coordinator class to simulate the 2PC coordinator.
    // This class is expected to be part of the main solution in production.
    public static class Coordinator {
        private final long timeoutMs;
        private final List<BankServer> bankServers = new CopyOnWriteArrayList<>();
        // Maintain transaction statuses.
        private final ConcurrentMap<String, TransactionStatus> transactionStatusMap = new ConcurrentHashMap<>();

        public Coordinator(long timeoutMs) {
            this.timeoutMs = timeoutMs;
        }

        public void registerBankServers(List<BankServer> servers) {
            bankServers.clear();
            bankServers.addAll(servers);
        }

        // Executes the transaction using a two-phase commit protocol.
        public boolean executeTransaction(Transaction tx) {
            transactionStatusMap.put(tx.id, TransactionStatus.PENDING);
            ExecutorService exec = Executors.newFixedThreadPool(bankServers.size());
            List<Future<Boolean>> futures = new ArrayList<>();

            // Phase 1: Prepare
            for (BankServer bank : bankServers) {
                List<Operation> ops = tx.bankOperations.get(bank);
                Callable<Boolean> task = () -> bank.prepare(tx.id, ops);
                futures.add(exec.submit(task));
            }

            boolean allPrepared = true;
            for (Future<Boolean> future : futures) {
                try {
                    boolean res = future.get(timeoutMs, TimeUnit.MILLISECONDS);
                    if (!res) {
                        allPrepared = false;
                        break;
                    }
                } catch (Exception e) {
                    allPrepared = false;
                    break;
                }
            }

            // Phase 2: Commit or Rollback
            if (allPrepared) {
                for (BankServer bank : bankServers) {
                    bank.commit(tx.id);
                }
                transactionStatusMap.put(tx.id, TransactionStatus.COMMITTED);
                exec.shutdown();
                return true;
            } else {
                for (BankServer bank : bankServers) {
                    bank.rollback(tx.id);
                }
                transactionStatusMap.put(tx.id, TransactionStatus.ROLLEDBACK);
                exec.shutdown();
                return false;
            }
        }

        // Returns the status of a given transaction.
        public TransactionStatus getTransactionStatus(String transactionId) {
            return transactionStatusMap.get(transactionId);
        }

        // Simulates persisting the coordinator's state.
        public void persistState() {
            // In a real implementation, the state would be written to persistent storage.
        }

        // Simulates recovering the coordinator's state after a crash.
        public static Coordinator recover(long timeoutMs) {
            // In a real implementation, state would be loaded from persistent storage.
            return new Coordinator(timeoutMs);
        }
    }
}