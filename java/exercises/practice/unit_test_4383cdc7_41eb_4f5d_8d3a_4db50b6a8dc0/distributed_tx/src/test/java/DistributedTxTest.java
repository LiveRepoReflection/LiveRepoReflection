package distributed_tx;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.*;
import static org.junit.jupiter.api.Assertions.*;

// Dummy interfaces to simulate branch and transaction operations.
// These are assumed to be provided by the main project.
interface Branch {
    boolean prepare(String transactionId, Operation op);
    boolean commit(String transactionId);
    boolean rollback(String transactionId);
}

class Operation {
    private final String type; // "debit" or "credit"
    private final String account;
    private final int amount;
    
    public Operation(String type, String account, int amount) {
        this.type = type;
        this.account = account;
        this.amount = amount;
    }
    
    public String getType() {
        return type;
    }
    
    public String getAccount() {
        return account;
    }
    
    public int getAmount() {
        return amount;
    }
}

class Transaction {
    private final String transactionId;
    private final List<Operation> operations;
    
    public Transaction(String transactionId, List<Operation> operations) {
        this.transactionId = transactionId;
        this.operations = operations;
    }
    
    public String getTransactionId() {
        return transactionId;
    }
    
    public List<Operation> getOperations() {
        return operations;
    }
}

// Assume this is the distributed transaction coordinator implementation to be tested.
// It exposes methods to execute transactions and recover incomplete ones.
class DistributedTransactionCoordinator {
    // Executes a distributed transaction using the 2PC protocol.
    // Returns true if commit succeeded, and false if transaction was rolled back.
    public boolean executeTransaction(Transaction tx, List<Branch> branches) {
        List<Branch> preparedBranches = new ArrayList<>();
        // Phase 1: Prepare
        for (Branch branch : branches) {
            // For simplicity, assume one operation per branch (in real case, mapping needed)
            Operation op = tx.getOperations().get(0);
            boolean vote = branch.prepare(tx.getTransactionId(), op);
            if (vote) {
                preparedBranches.add(branch);
            } else {
                // Rollback all branches that voted yes.
                for (Branch prepared : preparedBranches) {
                    prepared.rollback(tx.getTransactionId());
                }
                // Log rollback if necessary.
                return false;
            }
        }
        // Phase 2: Commit
        boolean allCommitted = true;
        for (Branch branch : branches) {
            boolean commitResult = branch.commit(tx.getTransactionId());
            if (!commitResult) {
                allCommitted = false;
            }
        }
        // In a real system, inconsistent commit results would trigger recovery.
        return allCommitted;
    }
    
    // Recovery mechanism: scans logs and finalizes incomplete transactions.
    // For our test simulation, we assume recovery finalizes the given pending transaction.
    public boolean recover(Transaction tx, List<Branch> branches, boolean decisionToCommit) {
        if (decisionToCommit) {
            for (Branch branch : branches) {
                branch.commit(tx.getTransactionId());
            }
            return true;
        } else {
            for (Branch branch : branches) {
                branch.rollback(tx.getTransactionId());
            }
            return false;
        }
    }
}

public class DistributedTxTest {
    
    private DistributedTransactionCoordinator coordinator;
    
    @BeforeEach
    public void setUp() {
        coordinator = new DistributedTransactionCoordinator();
    }
    
    // A mock branch implementation to simulate branch behavior
    private static class MockBranch implements Branch {
        private boolean canPrepare;
        private boolean prepareCalled = false;
        private boolean commitCalled = false;
        private boolean rollbackCalled = false;
        
        public MockBranch(boolean canPrepare) {
            this.canPrepare = canPrepare;
        }
        
        @Override
        public boolean prepare(String transactionId, Operation op) {
            prepareCalled = true;
            return canPrepare;
        }
        
        @Override
        public boolean commit(String transactionId) {
            commitCalled = true;
            return true;
        }
        
        @Override
        public boolean rollback(String transactionId) {
            rollbackCalled = true;
            return true;
        }
        
        public boolean isPrepareCalled() {
            return prepareCalled;
        }
        
        public boolean isCommitCalled() {
            return commitCalled;
        }
        
        public boolean isRollbackCalled() {
            return rollbackCalled;
        }
    }
    
    @Test
    public void testSuccessfulTransaction() {
        // All branches will vote yes in the prepare phase.
        List<Branch> branches = new ArrayList<>();
        MockBranch branch1 = new MockBranch(true);
        MockBranch branch2 = new MockBranch(true);
        branches.add(branch1);
        branches.add(branch2);
        
        Operation op = new Operation("debit", "AccountA", 100);
        Transaction tx = new Transaction("tx1", Collections.singletonList(op));
        
        boolean result = coordinator.executeTransaction(tx, branches);
        
        assertTrue(result, "Transaction should commit successfully.");
        assertTrue(branch1.isPrepareCalled(), "Branch 1 should have received prepare call.");
        assertTrue(branch2.isPrepareCalled(), "Branch 2 should have received prepare call.");
        assertTrue(branch1.isCommitCalled(), "Branch 1 should have received commit call.");
        assertTrue(branch2.isCommitCalled(), "Branch 2 should have received commit call.");
        assertFalse(branch1.isRollbackCalled(), "Branch 1 should not have received rollback call.");
        assertFalse(branch2.isRollbackCalled(), "Branch 2 should not have received rollback call.");
    }
    
    @Test
    public void testFailedTransactionDueToPrepareFailure() {
        // One branch will vote no in the prepare phase.
        List<Branch> branches = new ArrayList<>();
        MockBranch branch1 = new MockBranch(true);
        MockBranch branch2 = new MockBranch(false);
        branches.add(branch1);
        branches.add(branch2);
        
        Operation op = new Operation("credit", "AccountB", 200);
        Transaction tx = new Transaction("tx2", Collections.singletonList(op));
        
        boolean result = coordinator.executeTransaction(tx, branches);
        
        assertFalse(result, "Transaction should be rolled back due to prepare failure.");
        assertTrue(branch1.isPrepareCalled(), "Branch 1 should have received prepare call.");
        assertTrue(branch2.isPrepareCalled(), "Branch 2 should have received prepare call.");
        // Because branch2 failed, branch1 should receive a rollback.
        assertTrue(branch1.isRollbackCalled(), "Branch 1 should have received rollback call.");
        // Since branch2 failed in prepare, commit should not be called.
        assertFalse(branch2.isCommitCalled(), "Branch 2 should not have received commit call.");
    }
    
    @Test
    public void testRecoveryMechanismCommitDecision() {
        // Simulate an incomplete transaction that needs recovery.
        List<Branch> branches = new ArrayList<>();
        MockBranch branch1 = new MockBranch(true);
        MockBranch branch2 = new MockBranch(true);
        branches.add(branch1);
        branches.add(branch2);
        
        Operation op = new Operation("debit", "AccountC", 150);
        Transaction tx = new Transaction("tx3", Collections.singletonList(op));
        
        // Simulate recovery where decision is to commit.
        boolean recoveryResult = coordinator.recover(tx, branches, true);
        
        assertTrue(recoveryResult, "Recovery should commit the transaction.");
        assertTrue(branch1.isCommitCalled(), "Branch 1 should have received commit call during recovery.");
        assertTrue(branch2.isCommitCalled(), "Branch 2 should have received commit call during recovery.");
    }
    
    @Test
    public void testRecoveryMechanismRollbackDecision() {
        // Simulate an incomplete transaction that needs recovery.
        List<Branch> branches = new ArrayList<>();
        MockBranch branch1 = new MockBranch(true);
        MockBranch branch2 = new MockBranch(true);
        branches.add(branch1);
        branches.add(branch2);
        
        Operation op = new Operation("credit", "AccountD", 250);
        Transaction tx = new Transaction("tx4", Collections.singletonList(op));
        
        // Simulate recovery where decision is to rollback.
        boolean recoveryResult = coordinator.recover(tx, branches, false);
        
        assertFalse(recoveryResult, "Recovery should rollback the transaction.");
        assertTrue(branch1.isRollbackCalled(), "Branch 1 should have received rollback call during recovery.");
        assertTrue(branch2.isRollbackCalled(), "Branch 2 should have received rollback call during recovery.");
    }
    
    @Test
    @Timeout(5)
    public void testConcurrentTransactions() throws InterruptedException, ExecutionException {
        // Test that the coordinator can handle multiple concurrent transactions.
        int numTransactions = 10;
        ExecutorService executor = Executors.newFixedThreadPool(numTransactions);
        List<Callable<Boolean>> tasks = new ArrayList<>();
        
        for (int i = 0; i < numTransactions; i++) {
            final String txId = "ctx_" + i;
            tasks.add(() -> {
                // For each transaction, create two branches that succeed.
                List<Branch> branches = new ArrayList<>();
                MockBranch branch1 = new MockBranch(true);
                MockBranch branch2 = new MockBranch(true);
                branches.add(branch1);
                branches.add(branch2);
                
                Operation op = new Operation("debit", "AccountConcurrent", 50);
                Transaction tx = new Transaction(txId, Collections.singletonList(op));
                return coordinator.executeTransaction(tx, branches);
            });
        }
        
        List<Future<Boolean>> futures = executor.invokeAll(tasks);
        for (Future<Boolean> future : futures) {
            assertTrue(future.get(), "Each concurrent transaction should commit successfully.");
        }
        executor.shutdown();
        assertTrue(executor.awaitTermination(5, TimeUnit.SECONDS), "Executor did not shut down in time.");
    }
}