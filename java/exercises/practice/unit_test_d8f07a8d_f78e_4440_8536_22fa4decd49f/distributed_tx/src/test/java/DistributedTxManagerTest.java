import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.JUnit4;

import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

import static org.junit.Assert.*;

@RunWith(JUnit4.class)
public class DistributedTxManagerTest {
    
    private DistributedTxManager txManager;
    private MockService serviceA;
    private MockService serviceB;
    private MockService serviceC;
    private MockService flakyService;
    private MockService failingService;
    
    @Before
    public void setUp() {
        txManager = new DistributedTxManager();
        serviceA = new MockService("ServiceA");
        serviceB = new MockService("ServiceB");
        serviceC = new MockService("ServiceC");
        flakyService = new FlakyMockService("FlakyService");
        failingService = new FailingMockService("FailingService");
        
        txManager.registerService(serviceA.getServiceId(), serviceA);
        txManager.registerService(serviceB.getServiceId(), serviceB);
        txManager.registerService(serviceC.getServiceId(), serviceC);
        txManager.registerService(flakyService.getServiceId(), flakyService);
        txManager.registerService(failingService.getServiceId(), failingService);
    }
    
    @Test
    public void testSuccessfulTransaction() throws Exception {
        Map<String, Object> transactionData = new HashMap<>();
        transactionData.put(serviceA.getServiceId(), "DataA");
        transactionData.put(serviceB.getServiceId(), "DataB");
        
        String txId = txManager.beginTransaction(transactionData);
        boolean result = txManager.executeTransaction(txId);
        
        assertTrue("Transaction should complete successfully", result);
        assertEquals("DataA", serviceA.getCommittedData(txId));
        assertEquals("DataB", serviceB.getCommittedData(txId));
        assertNull("ServiceC should not have data", serviceC.getCommittedData(txId));
    }
    
    @Test
    public void testRollbackOnPrepareFailure() throws Exception {
        Map<String, Object> transactionData = new HashMap<>();
        transactionData.put(serviceA.getServiceId(), "DataA");
        transactionData.put(failingService.getServiceId(), "DataFail");
        
        String txId = txManager.beginTransaction(transactionData);
        boolean result = txManager.executeTransaction(txId);
        
        assertFalse("Transaction should fail", result);
        assertNull("ServiceA should have rolled back", serviceA.getCommittedData(txId));
        assertNull("FailingService should have no data", failingService.getCommittedData(txId));
    }
    
    @Test
    public void testRetryOnFlakyService() throws Exception {
        Map<String, Object> transactionData = new HashMap<>();
        transactionData.put(serviceA.getServiceId(), "DataA");
        transactionData.put(flakyService.getServiceId(), "DataFlaky");
        
        String txId = txManager.beginTransaction(transactionData);
        boolean result = txManager.executeTransaction(txId);
        
        assertTrue("Transaction should eventually succeed", result);
        assertEquals("DataA", serviceA.getCommittedData(txId));
        assertEquals("DataFlaky", flakyService.getCommittedData(txId));
    }
    
    @Test
    public void testConcurrentTransactions() throws Exception {
        int numTransactions = 10;
        ExecutorService executor = Executors.newFixedThreadPool(numTransactions);
        CountDownLatch latch = new CountDownLatch(numTransactions);
        AtomicInteger successCount = new AtomicInteger(0);
        
        for (int i = 0; i < numTransactions; i++) {
            final int txNum = i;
            executor.submit(() -> {
                try {
                    Map<String, Object> data = new HashMap<>();
                    data.put(serviceA.getServiceId(), "ConcurrentA" + txNum);
                    data.put(serviceB.getServiceId(), "ConcurrentB" + txNum);
                    
                    String txId = txManager.beginTransaction(data);
                    boolean success = txManager.executeTransaction(txId);
                    
                    if (success) {
                        successCount.incrementAndGet();
                        assertEquals("ConcurrentA" + txNum, serviceA.getCommittedData(txId));
                        assertEquals("ConcurrentB" + txNum, serviceB.getCommittedData(txId));
                    }
                } finally {
                    latch.countDown();
                }
            });
        }
        
        assertTrue("Timed out waiting for transactions to complete", 
                latch.await(30, TimeUnit.SECONDS));
        executor.shutdown();
        
        assertEquals("All transactions should succeed", numTransactions, successCount.get());
    }
    
    @Test
    public void testTransactionTimeout() throws Exception {
        MockService timeoutService = new TimeoutMockService("TimeoutService");
        txManager.registerService(timeoutService.getServiceId(), timeoutService);
        
        Map<String, Object> transactionData = new HashMap<>();
        transactionData.put(serviceA.getServiceId(), "DataA");
        transactionData.put(timeoutService.getServiceId(), "DataTimeout");
        
        String txId = txManager.beginTransaction(transactionData);
        boolean result = txManager.executeTransaction(txId);
        
        assertFalse("Transaction should fail due to timeout", result);
        assertNull("ServiceA should have rolled back", serviceA.getCommittedData(txId));
    }
    
    @Test
    public void testMixedSuccessAndFailure() throws Exception {
        // First transaction - should succeed
        Map<String, Object> successData = new HashMap<>();
        successData.put(serviceA.getServiceId(), "SuccessA");
        successData.put(serviceB.getServiceId(), "SuccessB");
        
        String successTxId = txManager.beginTransaction(successData);
        boolean successResult = txManager.executeTransaction(successTxId);
        
        assertTrue("First transaction should succeed", successResult);
        
        // Second transaction - should fail
        Map<String, Object> failureData = new HashMap<>();
        failureData.put(serviceA.getServiceId(), "FailureA");
        failureData.put(failingService.getServiceId(), "FailureData");
        
        String failureTxId = txManager.beginTransaction(failureData);
        boolean failureResult = txManager.executeTransaction(failureTxId);
        
        assertFalse("Second transaction should fail", failureResult);
        
        // Verify first transaction data is still intact
        assertEquals("SuccessA", serviceA.getCommittedData(successTxId));
        assertEquals("SuccessB", serviceB.getCommittedData(successTxId));
        
        // Verify second transaction data was rolled back
        assertNull("Failed transaction should have no committed data", 
                serviceA.getCommittedData(failureTxId));
    }
    
    @Test
    public void testTransactionWithAllServices() throws Exception {
        Map<String, Object> transactionData = new HashMap<>();
        transactionData.put(serviceA.getServiceId(), "AllA");
        transactionData.put(serviceB.getServiceId(), "AllB");
        transactionData.put(serviceC.getServiceId(), "AllC");
        
        String txId = txManager.beginTransaction(transactionData);
        boolean result = txManager.executeTransaction(txId);
        
        assertTrue("Transaction with all services should succeed", result);
        assertEquals("AllA", serviceA.getCommittedData(txId));
        assertEquals("AllB", serviceB.getCommittedData(txId));
        assertEquals("AllC", serviceC.getCommittedData(txId));
    }
    
    @Test
    public void testTransactionWithNoServices() throws Exception {
        Map<String, Object> emptyData = new HashMap<>();
        
        String txId = txManager.beginTransaction(emptyData);
        boolean result = txManager.executeTransaction(txId);
        
        assertTrue("Empty transaction should succeed", result);
    }
    
    @Test(expected = IllegalArgumentException.class)
    public void testInvalidServiceId() throws Exception {
        Map<String, Object> invalidData = new HashMap<>();
        invalidData.put("NonExistentService", "SomeData");
        
        txManager.beginTransaction(invalidData);
    }
    
    @Test
    public void testLargeTransaction() throws Exception {
        // Create a transaction with a large amount of data
        Map<String, Object> largeData = new HashMap<>();
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < 10000; i++) {
            sb.append("Large data content ");
        }
        String largeContent = sb.toString();
        
        largeData.put(serviceA.getServiceId(), largeContent);
        largeData.put(serviceB.getServiceId(), largeContent);
        
        String txId = txManager.beginTransaction(largeData);
        boolean result = txManager.executeTransaction(txId);
        
        assertTrue("Large transaction should succeed", result);
        assertEquals(largeContent, serviceA.getCommittedData(txId));
        assertEquals(largeContent, serviceB.getCommittedData(txId));
    }

    // Mock service implementations for testing
    
    private static class MockService implements TransactionParticipant {
        private final String serviceId;
        private final Map<String, Object> preparedData = new ConcurrentHashMap<>();
        private final Map<String, Object> committedData = new ConcurrentHashMap<>();
        
        public MockService(String serviceId) {
            this.serviceId = serviceId;
        }
        
        public String getServiceId() {
            return serviceId;
        }
        
        public Object getCommittedData(String txId) {
            return committedData.get(txId);
        }
        
        @Override
        public boolean prepare(String txId, Object data) {
            preparedData.put(txId, data);
            return true;
        }
        
        @Override
        public void commit(String txId) {
            Object data = preparedData.get(txId);
            if (data != null) {
                committedData.put(txId, data);
                preparedData.remove(txId);
            }
        }
        
        @Override
        public void rollback(String txId) {
            preparedData.remove(txId);
        }
    }
    
    private static class FailingMockService extends MockService {
        public FailingMockService(String serviceId) {
            super(serviceId);
        }
        
        @Override
        public boolean prepare(String txId, Object data) {
            // Always fail during prepare phase
            return false;
        }
    }
    
    private static class FlakyMockService extends MockService {
        private final AtomicInteger prepareAttempts = new AtomicInteger(0);
        
        public FlakyMockService(String serviceId) {
            super(serviceId);
        }
        
        @Override
        public boolean prepare(String txId, Object data) {
            int attempts = prepareAttempts.incrementAndGet();
            if (attempts <= 2) {
                // Fail on first two attempts
                return false;
            }
            // Succeed on third attempt
            return super.prepare(txId, data);
        }
    }
    
    private static class TimeoutMockService extends MockService {
        public TimeoutMockService(String serviceId) {
            super(serviceId);
        }
        
        @Override
        public boolean prepare(String txId, Object data) {
            try {
                // Simulate a timeout by sleeping
                Thread.sleep(10000);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            return true;
        }
    }
}