import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Disabled;
import static org.junit.jupiter.api.Assertions.*;
import java.util.Arrays;
import java.util.List;

public class TransactionOrchestratorTest {
    private TransactionOrchestrator orchestrator;
    private List<Transaction> successfulTransactions;
    private List<Transaction> failingTransactions;
    private List<Transaction> mixedTransactions;

    @BeforeEach
    public void setUp() {
        orchestrator = new TransactionOrchestrator();
        
        // Successful transactions
        successfulTransactions = Arrays.asList(
            new MockTransaction(true, true),
            new MockTransaction(true, true),
            new MockTransaction(true, true)
        );
        
        // Transactions with one failing commit
        failingTransactions = Arrays.asList(
            new MockTransaction(true, true),
            new MockTransaction(false, true),  // This will fail
            new MockTransaction(true, true)
        );
        
        // Transactions with one failing rollback
        mixedTransactions = Arrays.asList(
            new MockTransaction(true, true),
            new MockTransaction(false, false), // Commit fails, rollback fails
            new MockTransaction(true, true)
        );
    }

    @Test
    public void testAllSuccessfulTransactions() {
        TransactionResult result = orchestrator.execute(successfulTransactions);
        assertTrue(result.isSuccess());
        assertEquals(3, result.getTransactionStatuses().size());
        result.getTransactionStatuses().forEach(status -> {
            assertEquals(TransactionStatus.Status.COMMITTED, status.getStatus());
        });
    }

    @Disabled("Remove to run test")
    @Test
    public void testFailingCommitWithSuccessfulRollback() {
        TransactionResult result = orchestrator.execute(failingTransactions);
        assertFalse(result.isSuccess());
        assertEquals(3, result.getTransactionStatuses().size());
        
        assertEquals(TransactionStatus.Status.COMMITTED, result.getTransactionStatuses().get(0).getStatus());
        assertEquals(TransactionStatus.Status.COMMIT_FAILED, result.getTransactionStatuses().get(1).getStatus());
        assertEquals(TransactionStatus.Status.ROLLED_BACK, result.getTransactionStatuses().get(2).getStatus());
    }

    @Disabled("Remove to run test")
    @Test
    public void testFailingCommitWithFailingRollback() {
        TransactionResult result = orchestrator.execute(mixedTransactions);
        assertFalse(result.isSuccess());
        assertEquals(3, result.getTransactionStatuses().size());
        
        assertEquals(TransactionStatus.Status.COMMITTED, result.getTransactionStatuses().get(0).getStatus());
        assertEquals(TransactionStatus.Status.COMMIT_FAILED, result.getTransactionStatuses().get(1).getStatus());
        assertEquals(TransactionStatus.Status.ROLLBACK_FAILED, result.getTransactionStatuses().get(2).getStatus());
    }

    @Disabled("Remove to run test")
    @Test
    public void testEmptyTransactionList() {
        TransactionResult result = orchestrator.execute(List.of());
        assertTrue(result.isSuccess());
        assertTrue(result.getTransactionStatuses().isEmpty());
    }

    @Disabled("Remove to run test")
    @Test
    public void testNullTransactionList() {
        assertThrows(IllegalArgumentException.class, () -> {
            orchestrator.execute(null);
        });
    }
}

class MockTransaction implements Transaction {
    private final boolean commitSuccess;
    private final boolean rollbackSuccess;
    
    public MockTransaction(boolean commitSuccess, boolean rollbackSuccess) {
        this.commitSuccess = commitSuccess;
        this.rollbackSuccess = rollbackSuccess;
    }
    
    @Override
    public boolean commit() {
        return commitSuccess;
    }
    
    @Override
    public boolean rollback() {
        return rollbackSuccess;
    }
}