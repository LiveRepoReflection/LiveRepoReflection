import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;
import java.util.*;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;

public class TransactionManagerTest {

    private TransactionManager transactionManager;
    private ParticipantService userService;
    private ParticipantService profileService;
    private ParticipantService notificationService;

    @BeforeEach
    public void setup() {
        transactionManager = new TransactionManager();
        userService = new MockParticipantService("UserService");
        profileService = new MockParticipantService("ProfileService");
        notificationService = new MockParticipantService("NotificationService");
    }

    @Test
    public void testSuccessfulTransaction() {
        // Setup a transaction
        String transactionId = transactionManager.beginTransaction();
        transactionManager.registerParticipant(transactionId, userService);
        transactionManager.registerParticipant(transactionId, profileService);
        transactionManager.registerParticipant(transactionId, notificationService);

        // Test transaction commit
        assertTrue(transactionManager.commitTransaction(transactionId), 
                "Transaction should commit successfully when all participants are prepared");

        // Verify state
        assertEquals(TransactionStatus.COMMITTED, transactionManager.getTransactionStatus(transactionId),
                "Transaction status should be COMMITTED after successful commit");
    }

    @Test
    public void testFailedPreparation() {
        // Setup a transaction
        String transactionId = transactionManager.beginTransaction();
        transactionManager.registerParticipant(transactionId, userService);
        transactionManager.registerParticipant(transactionId, new FailingParticipantService("FailingService"));
        transactionManager.registerParticipant(transactionId, notificationService);

        // Test transaction commit (should fail during preparation)
        assertFalse(transactionManager.commitTransaction(transactionId),
                "Transaction should fail when any participant fails to prepare");

        // Verify state
        assertEquals(TransactionStatus.ROLLED_BACK, transactionManager.getTransactionStatus(transactionId),
                "Transaction status should be ROLLED_BACK after failed preparation");
    }

    @Test
    public void testExplicitRollback() {
        // Setup a transaction
        String transactionId = transactionManager.beginTransaction();
        transactionManager.registerParticipant(transactionId, userService);
        transactionManager.registerParticipant(transactionId, profileService);

        // Test transaction rollback
        transactionManager.rollbackTransaction(transactionId);

        // Verify state
        assertEquals(TransactionStatus.ROLLED_BACK, transactionManager.getTransactionStatus(transactionId),
                "Transaction status should be ROLLED_BACK after explicit rollback");
    }

    @Test
    public void testNonExistentTransaction() {
        // Test non-existent transaction
        String invalidTransactionId = "non-existent-transaction";
        Exception exception = assertThrows(IllegalArgumentException.class, () -> {
            transactionManager.commitTransaction(invalidTransactionId);
        });

        assertTrue(exception.getMessage().contains("Transaction not found"),
                "Exception should indicate that transaction was not found");
    }

    @Test
    public void testCommitWithNoParticipants() {
        // Setup a transaction without participants
        String transactionId = transactionManager.beginTransaction();

        // Test transaction commit
        assertTrue(transactionManager.commitTransaction(transactionId),
                "Transaction with no participants should commit successfully");

        // Verify state
        assertEquals(TransactionStatus.COMMITTED, transactionManager.getTransactionStatus(transactionId),
                "Transaction status should be COMMITTED when there are no participants");
    }

    @Test
    public void testConcurrentTransactions() throws InterruptedException {
        // Create a latch to synchronize thread completion
        final int COUNT = 10;
        CountDownLatch latch = new CountDownLatch(COUNT);
        
        // Start multiple concurrent transactions
        for (int i = 0; i < COUNT; i++) {
            final int index = i;
            new Thread(() -> {
                try {
                    String txId = transactionManager.beginTransaction();
                    ParticipantService service1 = new MockParticipantService("Service1-" + index);
                    ParticipantService service2 = new MockParticipantService("Service2-" + index);
                    
                    transactionManager.registerParticipant(txId, service1);
                    transactionManager.registerParticipant(txId, service2);
                    
                    if (index % 5 == 0) {
                        // Occasionally fail a transaction
                        transactionManager.rollbackTransaction(txId);
                        assertEquals(TransactionStatus.ROLLED_BACK, 
                                transactionManager.getTransactionStatus(txId),
                                "Transaction should be rolled back");
                    } else {
                        boolean result = transactionManager.commitTransaction(txId);
                        assertTrue(result, "Transaction should commit successfully");
                        assertEquals(TransactionStatus.COMMITTED, 
                                transactionManager.getTransactionStatus(txId),
                                "Transaction should be committed");
                    }
                } finally {
                    latch.countDown();
                }
            }).start();
        }
        
        // Wait for all threads to complete
        assertTrue(latch.await(5, TimeUnit.SECONDS), "All transactions should complete within timeout");
    }

    @Test
    public void testTransactionTimeout() {
        // Configure transaction manager with a very short timeout
        TransactionManager timeoutManager = new TransactionManager(100); // 100ms timeout
        
        // Setup a transaction
        String transactionId = timeoutManager.beginTransaction();
        timeoutManager.registerParticipant(transactionId, new SlowParticipantService("SlowService", 500));
        
        // Test transaction commit (should timeout)
        assertFalse(timeoutManager.commitTransaction(transactionId),
                "Transaction should fail when a participant times out");
        
        // Verify state
        assertEquals(TransactionStatus.ROLLED_BACK, timeoutManager.getTransactionStatus(transactionId),
                "Transaction status should be ROLLED_BACK after timeout");
    }

    // Mock implementations for testing
    
    private static class MockParticipantService implements ParticipantService {
        private final String name;
        private final Map<String, String> data = new HashMap<>();
        private final Set<String> preparedTxs = new HashSet<>();
        private final Set<String> committedTxs = new HashSet<>();
        
        public MockParticipantService(String name) {
            this.name = name;
        }
        
        @Override
        public ParticipantStatus prepare(String transactionId) {
            preparedTxs.add(transactionId);
            return ParticipantStatus.PREPARED;
        }
        
        @Override
        public void commit(String transactionId) {
            if (!preparedTxs.contains(transactionId)) {
                throw new IllegalStateException("Cannot commit a transaction that wasn't prepared");
            }
            committedTxs.add(transactionId);
        }
        
        @Override
        public void rollback(String transactionId) {
            preparedTxs.remove(transactionId);
        }
        
        @Override
        public String getName() {
            return name;
        }
    }
    
    private static class FailingParticipantService implements ParticipantService {
        private final String name;
        
        public FailingParticipantService(String name) {
            this.name = name;
        }
        
        @Override
        public ParticipantStatus prepare(String transactionId) {
            return ParticipantStatus.ABORT;
        }
        
        @Override
        public void commit(String transactionId) {
            throw new IllegalStateException("Should never commit a failing service");
        }
        
        @Override
        public void rollback(String transactionId) {
            // No-op for failing service
        }
        
        @Override
        public String getName() {
            return name;
        }
    }
    
    private static class SlowParticipantService implements ParticipantService {
        private final String name;
        private final long delayMs;
        
        public SlowParticipantService(String name, long delayMs) {
            this.name = name;
            this.delayMs = delayMs;
        }
        
        @Override
        public ParticipantStatus prepare(String transactionId) {
            try {
                Thread.sleep(delayMs);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            return ParticipantStatus.PREPARED;
        }
        
        @Override
        public void commit(String transactionId) {
            // No-op for slow service
        }
        
        @Override
        public void rollback(String transactionId) {
            // No-op for slow service
        }
        
        @Override
        public String getName() {
            return name;
        }
    }
}