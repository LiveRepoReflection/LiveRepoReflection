import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

import static org.junit.jupiter.api.Assertions.*;

// Assume that the solution provides these interfaces/classes:
// - interface BankService { boolean prepare(String transactionId, String accountId, double amount); boolean commit(String transactionId, String accountId, double amount); boolean rollback(String transactionId, String accountId, double amount); double getBalance(String accountId); }
// - class DistributedTxCoordinator { 
//       public DistributedTxCoordinator(Map<String, BankService> bankServices) { ... }
//       public boolean executeTransaction(String transactionId, List<TransactionOperation> operations) { ... }
//   }
// - class TransactionOperation { 
//       public TransactionOperation(String bankId, String accountId, double amount, boolean readOnly) { ... }
//       public String bankId; 
//       public String accountId; 
//       public double amount; 
//       public boolean readOnly;
//   }

public class DistributedTxCoordinatorTest {

    private FakeBankService bankA;
    private FakeBankService bankB;
    private FakeBankService readOnlyBank;
    private Map<String, BankService> bankServices;
    private DistributedTxCoordinator coordinator;

    @BeforeEach
    public void setUp() {
        bankA = new FakeBankService("accountA", 1000.0);
        bankB = new FakeBankService("accountB", 1000.0);
        readOnlyBank = new FakeBankService("readOnlyAccount", 500.0);

        bankServices = new HashMap<>();
        bankServices.put("BankA", bankA);
        bankServices.put("BankB", bankB);
        bankServices.put("ReadOnlyBank", readOnlyBank);

        // Coordinator should be instantiated with the mapping of bank identifiers to their BankService implementations.
        coordinator = new DistributedTxCoordinator(bankServices);
    }

    @Test
    public void testSuccessfulTransaction() {
        // Withdraw 100 from BankA and deposit 100 to BankB.
        List<TransactionOperation> operations = new ArrayList<>();
        operations.add(new TransactionOperation("BankA", bankA.getAccountId(), -100.0, false));
        operations.add(new TransactionOperation("BankB", bankB.getAccountId(), +100.0, false));

        String txId = UUID.randomUUID().toString();
        boolean result = coordinator.executeTransaction(txId, operations);
        assertTrue(result, "Transaction should succeed");

        // Check that balances are updated.
        assertEquals(900.0, bankA.getBalance(bankA.getAccountId()), 0.001);
        assertEquals(1100.0, bankB.getBalance(bankB.getAccountId()), 0.001);
    }

    @Test
    public void testPrepareFailure() {
        // Configure BankA to fail during prepare.
        bankA.setFailPrepare(true);

        List<TransactionOperation> operations = new ArrayList<>();
        operations.add(new TransactionOperation("BankA", bankA.getAccountId(), -200.0, false));
        operations.add(new TransactionOperation("BankB", bankB.getAccountId(), +200.0, false));

        String txId = UUID.randomUUID().toString();
        boolean result = coordinator.executeTransaction(txId, operations);
        assertFalse(result, "Transaction should fail due to prepare failure");

        // Balances should remain unchanged.
        assertEquals(1000.0, bankA.getBalance(bankA.getAccountId()), 0.001);
        assertEquals(1000.0, bankB.getBalance(bankB.getAccountId()), 0.001);
    }

    @Test
    public void testReadOnlyOptimization() {
        // For read-only operation, mark operation as readOnly.
        // Coordinator should skip calling prepare/commit on read-only banks.
        List<TransactionOperation> operations = new ArrayList<>();
        operations.add(new TransactionOperation("ReadOnlyBank", readOnlyBank.getAccountId(), 0.0, true));

        String txId = UUID.randomUUID().toString();
        boolean result = coordinator.executeTransaction(txId, operations);
        assertTrue(result, "Read-only transaction should succeed");

        // Verify that no prepare/commit calls were made for the read-only bank.
        assertEquals(0, readOnlyBank.getPrepareCount());
        assertEquals(0, readOnlyBank.getCommitCount());
    }

    @Test
    @Timeout(10)
    public void testConcurrentTransactions() throws InterruptedException, ExecutionException {
        // Run multiple transactions concurrently.
        int concurrentTransactions = 10;
        ExecutorService executor = Executors.newFixedThreadPool(concurrentTransactions);
        List<Callable<Boolean>> tasks = new ArrayList<>();

        // Reset bank balances
        bankA.setBalance(1000.0);
        bankB.setBalance(1000.0);

        for (int i = 0; i < concurrentTransactions; i++) {
            tasks.add(() -> {
                List<TransactionOperation> ops = new ArrayList<>();
                ops.add(new TransactionOperation("BankA", bankA.getAccountId(), -50.0, false));
                ops.add(new TransactionOperation("BankB", bankB.getAccountId(), +50.0, false));
                String txId = UUID.randomUUID().toString();
                return coordinator.executeTransaction(txId, ops);
            });
        }

        List<Future<Boolean>> results = executor.invokeAll(tasks);
        executor.shutdown();
        for (Future<Boolean> future : results) {
            assertTrue(future.get(), "Each concurrent transaction should succeed");
        }

        // Final balances should reflect the net transactions.
        assertEquals(1000.0 - concurrentTransactions * 50.0, bankA.getBalance(bankA.getAccountId()), 0.001);
        assertEquals(1000.0 + concurrentTransactions * 50.0, bankB.getBalance(bankB.getAccountId()), 0.001);
    }

    // FakeBankService implementation for testing purposes.
    // This class simulates a BankService with configurable behavior.
    private static class FakeBankService implements BankService {
        private final String accountId;
        private double balance;
        private volatile boolean failPrepare = false;
        private volatile boolean failCommit = false;
        private volatile boolean failRollback = false;

        private final AtomicInteger prepareCount = new AtomicInteger(0);
        private final AtomicInteger commitCount = new AtomicInteger(0);
        private final AtomicInteger rollbackCount = new AtomicInteger(0);

        public FakeBankService(String accountId, double balance) {
            this.accountId = accountId;
            this.balance = balance;
        }

        public String getAccountId() {
            return accountId;
        }

        public synchronized void setBalance(double balance) {
            this.balance = balance;
        }

        @Override
        public synchronized double getBalance(String accountId) {
            if (!this.accountId.equals(accountId)) {
                throw new IllegalArgumentException("Invalid account id");
            }
            return balance;
        }

        @Override
        public synchronized boolean prepare(String transactionId, String accountId, double amount) {
            if (!this.accountId.equals(accountId)) {
                throw new IllegalArgumentException("Invalid account id");
            }
            prepareCount.incrementAndGet();
            if (failPrepare) {
                return false;
            }
            // Check for sufficient funds for withdrawal
            if (amount < 0 && balance + amount < 0) {
                return false;
            }
            return true;
        }

        @Override
        public synchronized boolean commit(String transactionId, String accountId, double amount) {
            if (!this.accountId.equals(accountId)) {
                throw new IllegalArgumentException("Invalid account id");
            }
            commitCount.incrementAndGet();
            if (failCommit) {
                return false;
            }
            balance += amount;
            return true;
        }

        @Override
        public synchronized boolean rollback(String transactionId, String accountId, double amount) {
            if (!this.accountId.equals(accountId)) {
                throw new IllegalArgumentException("Invalid account id");
            }
            rollbackCount.incrementAndGet();
            if (failRollback) {
                return false;
            }
            // In a real implementation, rollback would undo any changes from a commit.
            // For simulation, assume rollback restores the previous balance.
            return true;
        }

        public int getPrepareCount() {
            return prepareCount.get();
        }

        public int getCommitCount() {
            return commitCount.get();
        }

        public int getRollbackCount() {
            return rollbackCount.get();
        }

        public void setFailPrepare(boolean fail) {
            this.failPrepare = fail;
        }

        public void setFailCommit(boolean fail) {
            this.failCommit = fail;
        }

        public void setFailRollback(boolean fail) {
            this.failRollback = fail;
        }
    }
}