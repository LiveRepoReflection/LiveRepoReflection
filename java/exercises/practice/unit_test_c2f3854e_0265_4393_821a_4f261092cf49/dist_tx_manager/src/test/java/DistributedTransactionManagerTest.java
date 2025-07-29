import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;

import static org.junit.jupiter.api.Assertions.*;

public class DistributedTransactionManagerTest {

    private DistributedTransactionManager dtm;
    private MockShard[] shards;
    private static final int NUM_SHARDS = 3;

    @BeforeEach
    public void setup() {
        shards = new MockShard[NUM_SHARDS];
        for (int i = 0; i < NUM_SHARDS; i++) {
            shards[i] = new MockShard();
        }
        dtm = new DistributedTransactionManager(shards);
    }

    @Test
    public void testSuccessfulTransaction() {
        String txId = dtm.begin();
        assertNotNull(txId, "Transaction ID should not be null");
        
        List<Operation> operations = Arrays.asList(
            new Operation(0, OperationType.WRITE, "key1", "value1"),
            new Operation(1, OperationType.WRITE, "key2", "value2"),
            new Operation(2, OperationType.WRITE, "key3", "value3")
        );
        
        assertTrue(dtm.execute(txId, operations), "Transaction execution should succeed");
        assertTrue(dtm.commit(txId), "Transaction commit should succeed");
        
        assertEquals("value1", shards[0].read("key1"), "Value should have been written to shard 0");
        assertEquals("value2", shards[1].read("key2"), "Value should have been written to shard 1");
        assertEquals("value3", shards[2].read("key3"), "Value should have been written to shard 2");
    }

    @Test
    public void testRollbackTransaction() {
        String txId = dtm.begin();
        
        List<Operation> operations = Arrays.asList(
            new Operation(0, OperationType.WRITE, "key1", "value1"),
            new Operation(1, OperationType.WRITE, "key2", "value2")
        );
        
        assertTrue(dtm.execute(txId, operations), "Transaction execution should succeed");
        assertTrue(dtm.rollback(txId), "Transaction rollback should succeed");
        
        assertNull(shards[0].read("key1"), "Value should not exist in shard 0 after rollback");
        assertNull(shards[1].read("key2"), "Value should not exist in shard 1 after rollback");
    }

    @Test
    public void testTransactionConflict() {
        // Set up a conflict scenario in shard 0
        shards[0].setPrepareToFail(true);
        
        String txId = dtm.begin();
        
        List<Operation> operations = Arrays.asList(
            new Operation(0, OperationType.WRITE, "key1", "value1"),
            new Operation(1, OperationType.WRITE, "key2", "value2")
        );
        
        assertFalse(dtm.execute(txId, operations), "Transaction should fail due to conflict");
        
        // Verify that no changes were made
        assertNull(shards[0].read("key1"), "Value should not exist in shard 0 after conflict");
        assertNull(shards[1].read("key2"), "Value should not exist in shard 1 after conflict");
    }

    @Test
    public void testReadOnlyOptimization() {
        String txId = dtm.begin();
        
        List<Operation> operations = Arrays.asList(
            new Operation(0, OperationType.READ, "key1", null),
            new Operation(1, OperationType.READ, "key2", null)
        );
        
        // Setup some data to read
        shards[0].write("key1", "value1");
        shards[1].write("key2", "value2");
        
        assertTrue(dtm.execute(txId, operations), "Read-only transaction should succeed");
        assertTrue(dtm.commit(txId), "Read-only transaction commit should succeed");
        
        // Verify that the shards' prepare method was not called for read-only transactions
        assertEquals(0, shards[0].getPrepareCount(), "Prepare should not be called for read-only shard 0");
        assertEquals(0, shards[1].getPrepareCount(), "Prepare should not be called for read-only shard 1");
    }

    @Test
    public void testBatchOptimization() {
        String txId = dtm.begin();
        
        // Multiple operations on the same shard should be batched
        List<Operation> operations = Arrays.asList(
            new Operation(0, OperationType.WRITE, "key1", "value1"),
            new Operation(0, OperationType.WRITE, "key2", "value2"),
            new Operation(0, OperationType.WRITE, "key3", "value3"),
            new Operation(1, OperationType.WRITE, "key4", "value4")
        );
        
        assertTrue(dtm.execute(txId, operations), "Batched transaction should succeed");
        assertTrue(dtm.commit(txId), "Batched transaction commit should succeed");
        
        // Verify that prepare was called only once per shard
        assertEquals(1, shards[0].getPrepareCount(), "Prepare should be called exactly once for shard 0");
        assertEquals(1, shards[1].getPrepareCount(), "Prepare should be called exactly once for shard 1");
        
        // Verify the values were written
        assertEquals("value1", shards[0].read("key1"));
        assertEquals("value2", shards[0].read("key2"));
        assertEquals("value3", shards[0].read("key3"));
        assertEquals("value4", shards[1].read("key4"));
    }

    @Test
    @Timeout(value = 10, unit = TimeUnit.SECONDS)
    public void testConcurrentTransactions() throws InterruptedException {
        final int numThreads = 5;
        final CountDownLatch latch = new CountDownLatch(numThreads);
        final ExecutorService executor = Executors.newFixedThreadPool(numThreads);
        final AtomicBoolean failed = new AtomicBoolean(false);
        
        for (int t = 0; t < numThreads; t++) {
            final int threadId = t;
            executor.submit(() -> {
                try {
                    // Each thread performs writes to all shards
                    String txId = dtm.begin();
                    List<Operation> operations = new ArrayList<>();
                    
                    for (int s = 0; s < NUM_SHARDS; s++) {
                        String key = "key_" + threadId + "_" + s;
                        String value = "value_" + threadId + "_" + s;
                        operations.add(new Operation(s, OperationType.WRITE, key, value));
                    }
                    
                    boolean executed = dtm.execute(txId, operations);
                    boolean committed = false;
                    if (executed) {
                        committed = dtm.commit(txId);
                    }
                    
                    if (!executed || !committed) {
                        failed.set(true);
                    }
                    
                } catch (Exception e) {
                    e.printStackTrace();
                    failed.set(true);
                } finally {
                    latch.countDown();
                }
            });
        }
        
        latch.await();
        executor.shutdown();
        
        assertFalse(failed.get(), "All concurrent transactions should complete successfully");
        
        // Verify all values were written correctly
        for (int t = 0; t < numThreads; t++) {
            for (int s = 0; s < NUM_SHARDS; s++) {
                String key = "key_" + t + "_" + s;
                String expectedValue = "value_" + t + "_" + s;
                assertEquals(expectedValue, shards[s].read(key), 
                        "Value for transaction " + t + " on shard " + s + " should match");
            }
        }
    }

    @Test
    public void testConcurrentConflictingTransactions() throws InterruptedException {
        // Let's simulate a conflict scenario between two transactions
        final ExecutorService executor = Executors.newFixedThreadPool(2);
        final CountDownLatch startLatch = new CountDownLatch(1);
        final CountDownLatch finishLatch = new CountDownLatch(2);
        
        // Make shard 0 introduce artificial delay during prepare to increase chance of conflict
        shards[0].setPrepareSleepMillis(100);
        
        // First transaction
        executor.submit(() -> {
            try {
                startLatch.await();
                String txId = dtm.begin();
                List<Operation> operations = Arrays.asList(
                    new Operation(0, OperationType.WRITE, "conflicted_key", "tx1_value")
                );
                boolean executed = dtm.execute(txId, operations);
                boolean committed = false;
                if (executed) {
                    committed = dtm.commit(txId);
                }
                
                if (committed) {
                    assertEquals("tx1_value", shards[0].read("conflicted_key"));
                }
            } catch (Exception e) {
                e.printStackTrace();
            } finally {
                finishLatch.countDown();
            }
        });
        
        // Second transaction
        executor.submit(() -> {
            try {
                startLatch.await();
                String txId = dtm.begin();
                List<Operation> operations = Arrays.asList(
                    new Operation(0, OperationType.WRITE, "conflicted_key", "tx2_value")
                );
                boolean executed = dtm.execute(txId, operations);
                boolean committed = false;
                if (executed) {
                    committed = dtm.commit(txId);
                }
                
                if (committed) {
                    assertEquals("tx2_value", shards[0].read("conflicted_key"));
                }
            } catch (Exception e) {
                e.printStackTrace();
            } finally {
                finishLatch.countDown();
            }
        });
        
        // Start both transactions at the same time
        startLatch.countDown();
        finishLatch.await();
        executor.shutdown();
        
        // Verify that exactly one transaction succeeded
        String value = shards[0].read("conflicted_key");
        assertNotNull(value, "One transaction should have succeeded");
        assertTrue(value.equals("tx1_value") || value.equals("tx2_value"), 
                "Value should be from one of the transactions");
    }

    // A mock implementation of the Shard interface for testing
    private static class MockShard implements Shard {
        private final java.util.Map<String, String> data = new java.util.HashMap<>();
        private final java.util.Map<String, List<Operation>> preparedTxs = new java.util.HashMap<>();
        private boolean prepareToFail = false;
        private int prepareCount = 0;
        private int prepareSleepMillis = 0;
        
        @Override
        public synchronized String read(String key) {
            return data.get(key);
        }
        
        @Override
        public synchronized boolean write(String key, String value) {
            data.put(key, value);
            return true;
        }
        
        @Override
        public synchronized boolean prepare(String transactionId, List<Operation> operations) {
            prepareCount++;
            
            if (prepareSleepMillis > 0) {
                try {
                    Thread.sleep(prepareSleepMillis);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }
            
            if (prepareToFail) {
                return false;
            }
            
            preparedTxs.put(transactionId, new ArrayList<>(operations));
            return true;
        }
        
        @Override
        public synchronized boolean commit(String transactionId) {
            List<Operation> operations = preparedTxs.remove(transactionId);
            if (operations == null) {
                return false;
            }
            
            for (Operation op : operations) {
                if (op.getOperationType() == OperationType.WRITE) {
                    data.put(op.getKey(), op.getValue());
                }
            }
            return true;
        }
        
        @Override
        public synchronized boolean rollback(String transactionId) {
            preparedTxs.remove(transactionId);
            return true;
        }
        
        public void setPrepareToFail(boolean prepareToFail) {
            this.prepareToFail = prepareToFail;
        }
        
        public int getPrepareCount() {
            return prepareCount;
        }
        
        public void setPrepareSleepMillis(int prepareSleepMillis) {
            this.prepareSleepMillis = prepareSleepMillis;
        }
    }
}