import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.util.Arrays;
import java.util.List;

public class DistributedTxTest {
    private Coordinator coordinator;
    private List<Participant> participants;
    
    @BeforeEach
    public void setUp() {
        coordinator = new Coordinator();
        participants = Arrays.asList(
            new MockParticipant(true),
            new MockParticipant(true),
            new MockParticipant(true)
        );
    }

    @Test
    public void testSuccessfulTransaction() {
        String txId = "tx1";
        coordinator.beginTransaction(txId, participants);
        assertTrue(coordinator.prepareTransaction(txId));
        coordinator.commitTransaction(txId);
    }

    @Test
    public void testFailedPreparePhase() {
        String txId = "tx2";
        List<Participant> mixedParticipants = Arrays.asList(
            new MockParticipant(true),
            new MockParticipant(false),
            new MockParticipant(true)
        );
        coordinator.beginTransaction(txId, mixedParticipants);
        assertFalse(coordinator.prepareTransaction(txId));
        coordinator.rollbackTransaction(txId);
    }

    @Test
    public void testConcurrentTransactions() {
        String tx1 = "tx3";
        String tx2 = "tx4";
        
        coordinator.beginTransaction(tx1, participants);
        coordinator.beginTransaction(tx2, participants);
        
        assertTrue(coordinator.prepareTransaction(tx1));
        assertTrue(coordinator.prepareTransaction(tx2));
        
        coordinator.commitTransaction(tx1);
        coordinator.commitTransaction(tx2);
    }

    @Test
    public void testCoordinatorRecovery() {
        String txId = "tx5";
        coordinator.beginTransaction(txId, participants);
        assertTrue(coordinator.prepareTransaction(txId));
        
        // Simulate crash
        Coordinator newCoordinator = new Coordinator();
        newCoordinator.recover();
        
        // Should complete the transaction
        assertDoesNotThrow(() -> newCoordinator.commitTransaction(txId));
    }

    @Test
    public void testParticipantFailure() {
        String txId = "tx6";
        List<Participant> unreliableParticipants = Arrays.asList(
            new MockParticipant(true),
            new MockParticipant(true, true), // Will fail during commit
            new MockParticipant(true)
        );
        
        coordinator.beginTransaction(txId, unreliableParticipants);
        assertTrue(coordinator.prepareTransaction(txId));
        assertThrows(RuntimeException.class, () -> coordinator.commitTransaction(txId));
    }

    private static class MockParticipant implements Participant {
        private final boolean prepareResult;
        private final boolean shouldFailOnCommit;
        
        public MockParticipant(boolean prepareResult) {
            this(prepareResult, false);
        }
        
        public MockParticipant(boolean prepareResult, boolean shouldFailOnCommit) {
            this.prepareResult = prepareResult;
            this.shouldFailOnCommit = shouldFailOnCommit;
        }
        
        @Override
        public boolean prepare(String transactionId) {
            return prepareResult;
        }
        
        @Override
        public void commit(String transactionId) {
            if (shouldFailOnCommit) {
                throw new RuntimeException("Participant failed during commit");
            }
        }
        
        @Override
        public void rollback(String transactionId) {
            // No-op for mock
        }
    }
}