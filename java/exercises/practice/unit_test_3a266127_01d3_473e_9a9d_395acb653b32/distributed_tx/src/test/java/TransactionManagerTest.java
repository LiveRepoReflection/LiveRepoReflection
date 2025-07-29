import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;

import static org.junit.jupiter.api.Assertions.*;

public class TransactionManagerTest {

    private TransactionManager transactionManager;
    private MockService[] services;

    @BeforeEach
    public void setUp() {
        transactionManager = new TransactionManager();
        // Initialize 3 mock services
        services = new MockService[3];
        for (int i = 0; i < services.length; i++) {
            services[i] = new MockService(i);
        }
    }

    @Test
    @DisplayName("Test successful transaction commit with single operation")
    public void testSuccessfulCommitSingleOperation() {
        // Start a transaction
        long txId = transactionManager.beginTransaction();

        // Register a successful operation on service 0
        final int serviceId = 0;
        final String key = "testKey";
        final String value = "testValue";
        
        transactionManager.registerOperation(txId, serviceId, 
            () -> services[serviceId].setValue(key, value),
            () -> services[serviceId].removeValue(key));

        // Commit the transaction
        assertTrue(transactionManager.commitTransaction(txId));
        
        // Verify the operation was executed
        assertEquals(value, services[serviceId].getValue(key));
    }

    @Test
    @DisplayName("Test transaction rollback when operation fails")
    public void testRollbackWhenOperationFails() {
        // Start a transaction
        long txId = transactionManager.beginTransaction();

        // First operation succeeds
        final int service0 = 0;
        final String key1 = "key1";
        final String value1 = "value1";
        
        transactionManager.registerOperation(txId, service0, 
            () -> services[service0].setValue(key1, value1),
            () -> services[service0].removeValue(key1));

        // Second operation fails
        final int service1 = 1;
        final String key2 = "key2";
        
        transactionManager.registerOperation(txId, service1, 
            () -> services[service1].failOperation(),
            () -> true);

        // Commit should fail and trigger rollback
        assertFalse(transactionManager.commitTransaction(txId));
        
        // Verify first operation was rolled back
        assertNull(services[service0].getValue(key1));
    }

    @Test
    @DisplayName("Test manually triggered rollback")
    public void testManualRollback() {
        // Start a transaction
        long txId = transactionManager.beginTransaction();

        // Register some operations
        final int service0 = 0;
        final String key1 = "key1";
        final String value1 = "value1";
        
        transactionManager.registerOperation(txId, service0, 
            () -> services[service0].setValue(key1, value1),
            () -> services[service0].removeValue(key1));

        // Manually rollback transaction
        transactionManager.rollbackTransaction(txId);
        
        // Verify operation was not committed
        assertNull(services[service0].getValue(key1));
    }

    @Test
    @DisplayName("Test transaction isolation between multiple transactions")
    public void testTransactionIsolation() {
        // Start two transactions
        long tx1 = transactionManager.beginTransaction();
        long tx2 = transactionManager.beginTransaction();

        final int serviceId = 0;
        final String key = "isolationKey";
        
        // Register operations for both transactions on the same key
        transactionManager.registerOperation(tx1, serviceId, 
            () -> services[serviceId].setValue(key, "tx1Value"),
            () -> services[serviceId].removeValue(key));
            
        transactionManager.registerOperation(tx2, serviceId, 
            () -> services[serviceId].setValue(key, "tx2Value"),
            () -> services[serviceId].removeValue(key));

        // Commit first transaction
        assertTrue(transactionManager.commitTransaction(tx1));
        
        // Verify first transaction's value is set
        assertEquals("tx1Value", services[serviceId].getValue(key));
        
        // Commit second transaction
        assertTrue(transactionManager.commitTransaction(tx2));
        
        // Verify second transaction's value overrode the first
        assertEquals("tx2Value", services[serviceId].getValue(key));
    }

    @Test
    @DisplayName("Test complex transaction with multiple services")
    public void testComplexTransactionMultipleServices() {
        // Start a transaction
        long txId = transactionManager.beginTransaction();

        // Register operations on multiple services
        final String key1 = "key1";
        final String value1 = "value1";
        final String key2 = "key2";
        final String value2 = "value2";
        final String key3 = "key3";
        final String value3 = "value3";
        
        transactionManager.registerOperation(txId, 0, 
            () -> services[0].setValue(key1, value1),
            () -> services[0].removeValue(key1));
            
        transactionManager.registerOperation(txId, 1, 
            () -> services[1].setValue(key2, value2),
            () -> services[1].removeValue(key2));
            
        transactionManager.registerOperation(txId, 2, 
            () -> services[2].setValue(key3, value3),
            () -> services[2].removeValue(key3));

        // Commit the transaction
        assertTrue(transactionManager.commitTransaction(txId));
        
        // Verify all operations were executed
        assertEquals(value1, services[0].getValue(key1));
        assertEquals(value2, services[1].getValue(key2));
        assertEquals(value3, services[2].getValue(key3));
    }

    @Test
    @DisplayName("Test error handling during commit")
    public void testErrorHandlingDuringCommit() {
        // Start a transaction
        long txId = transactionManager.beginTransaction();

        // Register operation that throws exception
        final int serviceId = 0;
        
        transactionManager.registerOperation(txId, serviceId, 
            () -> { throw new RuntimeException("Simulated error during execution"); },
            () -> true);

        // Commit should handle the exception and return false
        assertFalse(transactionManager.commitTransaction(txId));
    }

    @Test
    @DisplayName("Test error handling during rollback")
    public void testErrorHandlingDuringRollback() {
        // Start a transaction
        long txId = transactionManager.beginTransaction();

        // First operation succeeds
        final int service0 = 0;
        final String key = "key";
        final String value = "value";
        
        transactionManager.registerOperation(txId, service0, 
            () -> services[service0].setValue(key, value),
            () -> services[service0].removeValue(key));

        // Second operation throws exception during rollback
        final int service1 = 1;
        
        transactionManager.registerOperation(txId, service1, 
            () -> services[service1].failOperation(),
            () -> { throw new RuntimeException("Simulated error during rollback"); });

        // Commit should fail but not throw exception
        assertFalse(transactionManager.commitTransaction(txId));
        
        // Verify first operation was still rolled back despite error in second rollback
        assertNull(services[service0].getValue(key));
    }

    @Test
    @DisplayName("Test idempotency of rollback operations")
    public void testRollbackIdempotency() {
        // Start a transaction
        long txId = transactionManager.beginTransaction();

        // Create a counter to track rollback calls
        AtomicInteger rollbackCounter = new AtomicInteger(0);
        
        final int serviceId = 0;
        final String key = "key";
        final String value = "value";
        
        // Register operation with a rollback that counts calls
        transactionManager.registerOperation(txId, serviceId, 
            () -> services[serviceId].setValue(key, value),
            () -> {
                rollbackCounter.incrementAndGet();
                services[serviceId].removeValue(key);
                return true;
            });

        // Register failing operation to trigger rollback
        transactionManager.registerOperation(txId, 1, 
            () -> false,
            () -> true);

        // Commit should fail and trigger rollback
        assertFalse(transactionManager.commitTransaction(txId));
        
        // Manually trigger rollback again to test idempotency
        transactionManager.rollbackTransaction(txId);
        
        // Verify rollback was only executed once
        assertEquals(1, rollbackCounter.get());
    }

    @Test
    @DisplayName("Test concurrent transaction processing")
    public void testConcurrentTransactions() throws Exception {
        final int numThreads = 10;
        final int numTransactionsPerThread = 10;
        final ExecutorService executor = Executors.newFixedThreadPool(numThreads);
        final CountDownLatch latch = new CountDownLatch(numThreads);
        final AtomicBoolean failureDetected = new AtomicBoolean(false);
        
        List<Future<?>> futures = new ArrayList<>();
        
        for (int t = 0; t < numThreads; t++) {
            final int threadId = t;
            futures.add(executor.submit(() -> {
                try {
                    for (int i = 0; i < numTransactionsPerThread; i++) {
                        // Start a new transaction
                        long txId = transactionManager.beginTransaction();
                        
                        // Register operations on multiple services
                        final String key = "thread" + threadId + "_tx" + i;
                        final String value = "value_" + threadId + "_" + i;
                        
                        transactionManager.registerOperation(txId, threadId % services.length, 
                            () -> services[threadId % services.length].setValue(key, value),
                            () -> services[threadId % services.length].removeValue(key));
                        
                        // Randomly decide to commit or rollback
                        if (Math.random() > 0.3) {
                            transactionManager.commitTransaction(txId);
                        } else {
                            transactionManager.rollbackTransaction(txId);
                        }
                    }
                } catch (Exception e) {
                    failureDetected.set(true);
                    e.printStackTrace();
                } finally {
                    latch.countDown();
                }
            }));
        }
        
        // Wait for all threads to complete
        latch.await();
        executor.shutdown();
        
        // Check for failures
        assertFalse(failureDetected.get(), "One or more transactions failed unexpectedly");
        
        // Verify the transaction manager can still be used
        long finalTxId = transactionManager.beginTransaction();
        final String finalKey = "finalTest";
        final String finalValue = "finalValue";
        
        transactionManager.registerOperation(finalTxId, 0, 
            () -> services[0].setValue(finalKey, finalValue),
            () -> services[0].removeValue(finalKey));
            
        assertTrue(transactionManager.commitTransaction(finalTxId));
        assertEquals(finalValue, services[0].getValue(finalKey));
    }

    // Mock implementation of a service for testing purposes
    private static class MockService {
        private final int id;
        private final java.util.Map<String, String> data = new java.util.concurrent.ConcurrentHashMap<>();
        
        public MockService(int id) {
            this.id = id;
        }
        
        public boolean setValue(String key, String value) {
            data.put(key, value);
            return true;
        }
        
        public boolean removeValue(String key) {
            data.remove(key);
            return true;
        }
        
        public String getValue(String key) {
            return data.get(key);
        }
        
        public boolean failOperation() {
            return false;
        }
    }
}