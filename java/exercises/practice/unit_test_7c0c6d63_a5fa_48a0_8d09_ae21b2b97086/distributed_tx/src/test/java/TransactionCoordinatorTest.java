import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.util.UUID;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

import static org.junit.jupiter.api.Assertions.*;

public class TransactionCoordinatorTest {
    
    private TransactionCoordinator coordinator;
    
    @BeforeEach
    public void setUp() {
        coordinator = new TransactionCoordinator();
    }
    
    @Test
    public void testBeginTransaction() {
        String transactionId = UUID.randomUUID().toString();
        assertTrue(coordinator.beginTransaction(transactionId));
        assertFalse(coordinator.beginTransaction(transactionId), "Should not be able to begin the same transaction twice");
        assertEquals(TransactionStatus.ACTIVE, coordinator.getTransactionStatus(transactionId));
    }
    
    @Test
    public void testEnlistService() {
        String transactionId = UUID.randomUUID().toString();
        ServiceEndpoint service = new MockServiceEndpoint(ServiceResponse.COMMIT);
        
        // Cannot enlist before transaction begins
        assertFalse(coordinator.enlistService(transactionId, service));
        
        coordinator.beginTransaction(transactionId);
        assertTrue(coordinator.enlistService(transactionId, service));
        // Cannot enlist the same service twice
        assertFalse(coordinator.enlistService(transactionId, service));
    }
    
    @Test
    public void testPrepareTransactionAllCommit() {
        String transactionId = UUID.randomUUID().toString();
        coordinator.beginTransaction(transactionId);
        
        ServiceEndpoint service1 = new MockServiceEndpoint(ServiceResponse.COMMIT);
        ServiceEndpoint service2 = new MockServiceEndpoint(ServiceResponse.COMMIT);
        ServiceEndpoint service3 = new MockServiceEndpoint(ServiceResponse.COMMIT);
        
        coordinator.enlistService(transactionId, service1);
        coordinator.enlistService(transactionId, service2);
        coordinator.enlistService(transactionId, service3);
        
        assertEquals(TransactionStatus.COMMIT, coordinator.prepareTransaction(transactionId));
        assertEquals(TransactionStatus.PREPARING, coordinator.getTransactionStatus(transactionId));
    }
    
    @Test
    public void testPrepareTransactionOneRollback() {
        String transactionId = UUID.randomUUID().toString();
        coordinator.beginTransaction(transactionId);
        
        ServiceEndpoint service1 = new MockServiceEndpoint(ServiceResponse.COMMIT);
        ServiceEndpoint service2 = new MockServiceEndpoint(ServiceResponse.ROLLBACK);
        ServiceEndpoint service3 = new MockServiceEndpoint(ServiceResponse.COMMIT);
        
        coordinator.enlistService(transactionId, service1);
        coordinator.enlistService(transactionId, service2);
        coordinator.enlistService(transactionId, service3);
        
        assertEquals(TransactionStatus.ROLLBACK, coordinator.prepareTransaction(transactionId));
        assertEquals(TransactionStatus.PREPARING, coordinator.getTransactionStatus(transactionId));
    }
    
    @Test
    public void testPrepareTransactionOneError() {
        String transactionId = UUID.randomUUID().toString();
        coordinator.beginTransaction(transactionId);
        
        ServiceEndpoint service1 = new MockServiceEndpoint(ServiceResponse.COMMIT);
        ServiceEndpoint service2 = new MockServiceEndpoint(ServiceResponse.ERROR);
        ServiceEndpoint service3 = new MockServiceEndpoint(ServiceResponse.COMMIT);
        
        coordinator.enlistService(transactionId, service1);
        coordinator.enlistService(transactionId, service2);
        coordinator.enlistService(transactionId, service3);
        
        assertEquals(TransactionStatus.UNKNOWN, coordinator.prepareTransaction(transactionId));
        assertEquals(TransactionStatus.PREPARING, coordinator.getTransactionStatus(transactionId));
    }
    
    @Test
    public void testCommitTransaction() {
        String transactionId = UUID.randomUUID().toString();
        coordinator.beginTransaction(transactionId);
        
        MockServiceEndpoint service1 = new MockServiceEndpoint(ServiceResponse.COMMIT);
        MockServiceEndpoint service2 = new MockServiceEndpoint(ServiceResponse.COMMIT);
        
        coordinator.enlistService(transactionId, service1);
        coordinator.enlistService(transactionId, service2);
        
        coordinator.prepareTransaction(transactionId);
        coordinator.commitTransaction(transactionId);
        
        assertEquals(TransactionStatus.COMMITTED, coordinator.getTransactionStatus(transactionId));
        assertTrue(service1.wasCommitCalled());
        assertTrue(service2.wasCommitCalled());
    }
    
    @Test
    public void testRollbackTransaction() {
        String transactionId = UUID.randomUUID().toString();
        coordinator.beginTransaction(transactionId);
        
        MockServiceEndpoint service1 = new MockServiceEndpoint(ServiceResponse.COMMIT);
        MockServiceEndpoint service2 = new MockServiceEndpoint(ServiceResponse.ROLLBACK);
        
        coordinator.enlistService(transactionId, service1);
        coordinator.enlistService(transactionId, service2);
        
        coordinator.prepareTransaction(transactionId);
        coordinator.rollbackTransaction(transactionId);
        
        assertEquals(TransactionStatus.ROLLED_BACK, coordinator.getTransactionStatus(transactionId));
        assertTrue(service1.wasRollbackCalled());
        assertTrue(service2.wasRollbackCalled());
    }
    
    @Test
    public void testGetTransactionStatus() {
        String transactionId = UUID.randomUUID().toString();
        
        // Transaction doesn't exist
        assertEquals(TransactionStatus.UNKNOWN, coordinator.getTransactionStatus(transactionId));
        
        coordinator.beginTransaction(transactionId);
        assertEquals(TransactionStatus.ACTIVE, coordinator.getTransactionStatus(transactionId));
        
        ServiceEndpoint service = new MockServiceEndpoint(ServiceResponse.COMMIT);
        coordinator.enlistService(transactionId, service);
        
        coordinator.prepareTransaction(transactionId);
        assertEquals(TransactionStatus.PREPARING, coordinator.getTransactionStatus(transactionId));
        
        coordinator.commitTransaction(transactionId);
        assertEquals(TransactionStatus.COMMITTED, coordinator.getTransactionStatus(transactionId));
    }
    
    @Test
    public void testConcurrentTransactions() throws InterruptedException {
        int numThreads = 10;
        int numTransactionsPerThread = 10;
        CountDownLatch latch = new CountDownLatch(numThreads);
        ExecutorService executorService = Executors.newFixedThreadPool(numThreads);
        AtomicInteger successCount = new AtomicInteger(0);
        
        for (int i = 0; i < numThreads; i++) {
            executorService.submit(() -> {
                try {
                    for (int j = 0; j < numTransactionsPerThread; j++) {
                        String txId = UUID.randomUUID().toString();
                        if (coordinator.beginTransaction(txId)) {
                            ServiceEndpoint service1 = new MockServiceEndpoint(ServiceResponse.COMMIT);
                            ServiceEndpoint service2 = new MockServiceEndpoint(ServiceResponse.COMMIT);
                            
                            coordinator.enlistService(txId, service1);
                            coordinator.enlistService(txId, service2);
                            
                            TransactionStatus status = coordinator.prepareTransaction(txId);
                            if (status == TransactionStatus.COMMIT) {
                                coordinator.commitTransaction(txId);
                                successCount.incrementAndGet();
                            } else {
                                coordinator.rollbackTransaction(txId);
                            }
                        }
                    }
                } finally {
                    latch.countDown();
                }
            });
        }
        
        assertTrue(latch.await(30, TimeUnit.SECONDS), "Timeout waiting for threads to complete");
        executorService.shutdown();
        
        // Verify that the correct number of transactions were processed
        assertEquals(numThreads * numTransactionsPerThread, successCount.get());
    }
    
    @Test
    public void testTimeoutHandling() {
        String transactionId = UUID.randomUUID().toString();
        coordinator.beginTransaction(transactionId);
        
        // Create a service that will timeout during prepare
        ServiceEndpoint timeoutService = new TimeoutServiceEndpoint();
        coordinator.enlistService(transactionId, timeoutService);
        
        assertEquals(TransactionStatus.UNKNOWN, coordinator.prepareTransaction(transactionId));
    }
    
    // Mock implementation of ServiceEndpoint for testing
    private static class MockServiceEndpoint implements ServiceEndpoint {
        private final ServiceResponse response;
        private boolean commitCalled = false;
        private boolean rollbackCalled = false;
        
        public MockServiceEndpoint(ServiceResponse response) {
            this.response = response;
        }
        
        @Override
        public ServiceResponse prepare() {
            return response;
        }
        
        @Override
        public void commit() {
            commitCalled = true;
        }
        
        @Override
        public void rollback() {
            rollbackCalled = true;
        }
        
        public boolean wasCommitCalled() {
            return commitCalled;
        }
        
        public boolean wasRollbackCalled() {
            return rollbackCalled;
        }
    }
    
    // Service that simulates a timeout
    private static class TimeoutServiceEndpoint implements ServiceEndpoint {
        @Override
        public ServiceResponse prepare() {
            try {
                // Simulate a long running operation that exceeds timeout
                Thread.sleep(10000);
            } catch (InterruptedException e) {
                // Ignore
            }
            return ServiceResponse.COMMIT;
        }
        
        @Override
        public void commit() {
            // Do nothing
        }
        
        @Override
        public void rollback() {
            // Do nothing
        }
    }
}