package distributed_tx;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.concurrent.*;
import java.util.*;

public class DistributedTxTest {
    private TransactionCoordinator coordinator;
    private BankBranch branch1;
    private BankBranch branch2;

    @BeforeEach
    public void setup() {
        // Initialize the transaction coordinator and bank branches.
        coordinator = new TransactionCoordinator();
        branch1 = new BankBranch("branch1");
        branch2 = new BankBranch("branch2");

        // Register the branches with the coordinator.
        coordinator.registerBranch(branch1);
        coordinator.registerBranch(branch2);

        // Create initial accounts with balances.
        branch1.createAccount("branch1_acc1", 1000.0);
        branch2.createAccount("branch2_acc1", 500.0);
    }

    @Test
    public void testSuccessfulTransaction() {
        // Transaction: Transfer 200 from branch1_acc1 to branch2_acc1.
        Transaction tx = new Transaction("tx1", "branch1_acc1", "branch2_acc1", 200.0);
        boolean result = coordinator.processTransaction(tx);

        assertTrue(result, "Transaction should complete successfully");

        // Verify account balances.
        double balanceSource = branch1.getAccountBalance("branch1_acc1");
        double balanceDestination = branch2.getAccountBalance("branch2_acc1");
        assertEquals(800.0, balanceSource, 0.001, "Source account should be debited by 200");
        assertEquals(700.0, balanceDestination, 0.001, "Destination account should be credited by 200");
    }

    @Test
    public void testInsufficientFunds() {
        // Create an account with insufficient funds.
        branch1.createAccount("branch1_acc2", 100.0);
        // Transaction: Attempt to transfer 200 from branch1_acc2 to branch2_acc1.
        Transaction tx = new Transaction("tx2", "branch1_acc2", "branch2_acc1", 200.0);
        boolean result = coordinator.processTransaction(tx);

        assertFalse(result, "Transaction should fail due to insufficient funds");

        // Verify that account balances remain unchanged.
        double balanceSource = branch1.getAccountBalance("branch1_acc2");
        double balanceDestination = branch2.getAccountBalance("branch2_acc1");
        assertEquals(100.0, balanceSource, 0.001, "Source balance must remain unchanged");
        assertEquals(500.0, balanceDestination, 0.001, "Destination balance must remain unchanged");
    }

    @Test
    public void testConcurrentTransactions() throws InterruptedException, ExecutionException {
        // Create additional accounts for concurrent transactions.
        branch1.createAccount("branch1_acc3", 1000.0);
        branch2.createAccount("branch2_acc3", 500.0);
        
        int numTransactions = 10;
        ExecutorService executor = Executors.newFixedThreadPool(4);
        List<Future<Boolean>> futures = new ArrayList<>();

        for (int i = 0; i < numTransactions; i++) {
            final int idx = i;
            futures.add(executor.submit(() -> {
                String txId = "ctx" + idx;
                // Alternate between two sets of accounts.
                if (idx % 2 == 0) {
                    Transaction tx = new Transaction(txId, "branch1_acc1", "branch2_acc1", 50.0);
                    return coordinator.processTransaction(tx);
                } else {
                    Transaction tx = new Transaction(txId, "branch1_acc3", "branch2_acc3", 50.0);
                    return coordinator.processTransaction(tx);
                }
            }));
        }
        executor.shutdown();
        executor.awaitTermination(5, TimeUnit.SECONDS);

        // Verify all concurrent transactions succeeded.
        for (Future<Boolean> future : futures) {
            assertTrue(future.get(), "All concurrent transactions should succeed");
        }

        // Verify the final balances.
        double balance1 = branch1.getAccountBalance("branch1_acc1");
        double balance2 = branch2.getAccountBalance("branch2_acc1");
        double balance3 = branch1.getAccountBalance("branch1_acc3");
        double balance4 = branch2.getAccountBalance("branch2_acc3");

        assertEquals(1000.0 - (numTransactions / 2) * 50.0, balance1, 0.001, "Incorrect balance for branch1_acc1");
        assertEquals(500.0 + (numTransactions / 2) * 50.0, balance2, 0.001, "Incorrect balance for branch2_acc1");
        assertEquals(1000.0 - (numTransactions / 2) * 50.0, balance3, 0.001, "Incorrect balance for branch1_acc3");
        assertEquals(500.0 + (numTransactions / 2) * 50.0, balance4, 0.001, "Incorrect balance for branch2_acc3");
    }

    @Test
    public void testBranchFailure() {
        // Simulate a branch failure using a specialized branch that always votes abort.
        BankBranch failingBranch = new FailingBankBranch("branch_fail");
        coordinator.registerBranch(failingBranch);
        failingBranch.createAccount("branch_fail_acc", 500.0);

        // Transaction: Transfer 100 from branch_fail_acc to branch2_acc1.
        Transaction tx = new Transaction("tx_fail", "branch_fail_acc", "branch2_acc1", 100.0);
        boolean result = coordinator.processTransaction(tx);

        assertFalse(result, "Transaction should fail due to branch failure");

        // Verify that balances remain unchanged.
        double balanceFail = failingBranch.getAccountBalance("branch_fail_acc");
        double balanceDest = branch2.getAccountBalance("branch2_acc1");
        assertEquals(500.0, balanceFail, 0.001, "Failing branch account balance must remain unchanged");
        assertEquals(500.0, balanceDest, 0.001, "Destination branch account balance must remain unchanged");
    }

    @Test
    public void testCoordinatorTimeout() {
        // Simulate a slow branch by using a specialized branch that delays response.
        BankBranch slowBranch = new SlowBankBranch("branch_slow", 3000); // Delay of 3000 milliseconds.
        coordinator.registerBranch(slowBranch);
        slowBranch.createAccount("branch_slow_acc", 1000.0);

        // Transaction: Transfer 100 from branch_slow_acc to branch2_acc1.
        Transaction tx = new Transaction("tx_timeout", "branch_slow_acc", "branch2_acc1", 100.0);
        long startTime = System.currentTimeMillis();
        boolean result = coordinator.processTransaction(tx);
        long elapsed = System.currentTimeMillis() - startTime;

        // Assuming the coordinator timeout is set below the delay, transaction should fail.
        assertFalse(result, "Transaction should fail due to branch timeout");
        assertTrue(elapsed < 3000, "Coordinator should timeout before branch responds");

        double balanceSlow = slowBranch.getAccountBalance("branch_slow_acc");
        double balanceDest = branch2.getAccountBalance("branch2_acc1");
        assertEquals(1000.0, balanceSlow, 0.001, "Slow branch account balance must remain unchanged");
        assertEquals(500.0, balanceDest, 0.001, "Destination branch account balance must remain unchanged");
    }

    // Helper subclass to simulate a branch that always votes abort to simulate a failure scenario.
    private static class FailingBankBranch extends BankBranch {
        public FailingBankBranch(String branchId) {
            super(branchId);
        }

        @Override
        public boolean prepare(Transaction tx) {
            // Simulate failure by always voting to abort.
            return false;
        }
    }

    // Helper subclass to simulate a branch that delays its prepare response.
    private static class SlowBankBranch extends BankBranch {
        private long delayMillis;

        public SlowBankBranch(String branchId, long delayMillis) {
            super(branchId);
            this.delayMillis = delayMillis;
        }

        @Override
        public boolean prepare(Transaction tx) {
            try {
                Thread.sleep(delayMillis);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            return super.prepare(tx);
        }
    }
}