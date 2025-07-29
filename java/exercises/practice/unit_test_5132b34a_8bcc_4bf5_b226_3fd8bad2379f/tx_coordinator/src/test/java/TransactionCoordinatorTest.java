import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.util.concurrent.*;
import java.util.*;

class MockParticipant implements Participant {
    private boolean shouldFailPrepare;
    private boolean shouldFailCommit;
    private boolean shouldFailRollback;
    private Set<String> preparedTransactions = new HashSet<>();
    private Set<String> committedTransactions = new HashSet<>();
    private Set<String> rolledbackTransactions = new HashSet<>();

    public MockParticipant(boolean failPrepare, boolean failCommit, boolean failRollback) {
        this.shouldFailPrepare = failPrepare;
        this.shouldFailCommit = failCommit;
        this.shouldFailRollback = failRollback;
    }

    @Override
    public boolean prepare(String transactionId) {
        if (shouldFailPrepare) return false;
        preparedTransactions.add(transactionId);
        return true;
    }

    @Override
    public void commit(String transactionId) {
        if (shouldFailCommit) throw new RuntimeException("Commit failed");
        if (!preparedTransactions.contains(transactionId)) {
            throw new IllegalStateException("Not prepared for commit");
        }
        committedTransactions.add(transactionId);
    }

    @Override
    public void rollback(String transactionId) {
        if (shouldFailRollback) throw new RuntimeException("Rollback failed");
        rolledbackTransactions.add(transactionId);
    }

    public boolean wasPreparedFor(String transactionId) {
        return preparedTransactions.contains(transactionId);
    }

    public boolean wasCommitted(String transactionId) {
        return committedTransactions.contains(transactionId);
    }

    public boolean wasRolledBack(String transactionId) {
        return rolledbackTransactions.contains(transactionId);
    }
}

public class TransactionCoordinatorTest {
    private TransactionCoordinator coordinator;

    @BeforeEach
    public void setUp() {
        coordinator = new TransactionCoordinator();
    }

    @Test
    public void testBeginTransactionGeneratesUniqueId() {
        String tx1 = coordinator.beginTransaction();
        String tx2 = coordinator.beginTransaction();
        assertNotNull(tx1);
        assertNotNull(tx2);
        assertNotEquals(tx1, tx2);
    }

    @Test
    public void testSuccessfulTransaction() {
        String txId = coordinator.beginTransaction();
        Participant p1 = new MockParticipant(false, false, false);
        Participant p2 = new MockParticipant(false, false, false);
        
        coordinator.enroll(txId, p1);
        coordinator.enroll(txId, p2);
        
        assertTrue(coordinator.commitTransaction(txId));
        assertTrue(((MockParticipant)p1).wasCommitted(txId));
        assertTrue(((MockParticipant)p2).wasCommitted(txId));
    }

    @Test
    public void testFailedPrepareTriggersRollback() {
        String txId = coordinator.beginTransaction();
        Participant p1 = new MockParticipant(false, false, false);
        Participant p2 = new MockParticipant(true, false, false);
        
        coordinator.enroll(txId, p1);
        coordinator.enroll(txId, p2);
        
        assertFalse(coordinator.commitTransaction(txId));
        assertTrue(((MockParticipant)p1).wasRolledBack(txId));
        assertTrue(((MockParticipant)p2).wasRolledBack(txId));
    }

    @Test
    public void testFailedCommitTriggersRollback() {
        String txId = coordinator.beginTransaction();
        Participant p1 = new MockParticipant(false, false, false);
        Participant p2 = new MockParticipant(false, true, false);
        
        coordinator.enroll(txId, p1);
        coordinator.enroll(txId, p2);
        
        assertFalse(coordinator.commitTransaction(txId));
        assertTrue(((MockParticipant)p1).wasRolledBack(txId));
    }

    @Test
    public void testRollbackTransaction() {
        String txId = coordinator.beginTransaction();
        Participant p1 = new MockParticipant(false, false, false);
        Participant p2 = new MockParticipant(false, false, false);
        
        coordinator.enroll(txId, p1);
        coordinator.enroll(txId, p2);
        
        assertTrue(coordinator.rollbackTransaction(txId));
        assertTrue(((MockParticipant)p1).wasRolledBack(txId));
        assertTrue(((MockParticipant)p2).wasRolledBack(txId));
    }

    @Test
    public void testConcurrentTransactions() throws InterruptedException, ExecutionException {
        int numTransactions = 10;
        ExecutorService executor = Executors.newFixedThreadPool(numTransactions);
        List<Future<Boolean>> results = new ArrayList<>();
        
        for (int i = 0; i < numTransactions; i++) {
            results.add(executor.submit(() -> {
                String txId = coordinator.beginTransaction();
                Participant p1 = new MockParticipant(false, false, false);
                Participant p2 = new MockParticipant(false, false, false);
                
                coordinator.enroll(txId, p1);
                coordinator.enroll(txId, p2);
                
                return coordinator.commitTransaction(txId);
            }));
        }
        
        for (Future<Boolean> result : results) {
            assertTrue(result.get());
        }
        executor.shutdown();
    }

    @Test
    public void testParticipantCannotBeEnrolledInMultipleTransactions() {
        String tx1 = coordinator.beginTransaction();
        String tx2 = coordinator.beginTransaction();
        Participant p = new MockParticipant(false, false, false);
        
        coordinator.enroll(tx1, p);
        assertThrows(IllegalStateException.class, () -> coordinator.enroll(tx2, p));
    }

    @Test
    public void testTransactionWithNoParticipants() {
        String txId = coordinator.beginTransaction();
        assertTrue(coordinator.commitTransaction(txId));
    }

    @Test
    public void testRollbackFailureHandling() {
        String txId = coordinator.beginTransaction();
        Participant p1 = new MockParticipant(false, false, true);
        
        coordinator.enroll(txId, p1);
        assertFalse(coordinator.rollbackTransaction(txId));
    }
}