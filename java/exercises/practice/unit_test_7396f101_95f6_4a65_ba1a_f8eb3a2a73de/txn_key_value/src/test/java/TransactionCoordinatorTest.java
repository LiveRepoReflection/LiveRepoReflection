import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicLong;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

class TransactionCoordinatorTest {

    private static final int NUM_NODES = 3;
    private TransactionCoordinator coordinator;
    
    @BeforeEach
    void setUp() {
        coordinator = new TransactionCoordinator(NUM_NODES);
    }

    @Test
    void beginTransaction_CreatesNewTransactionId() {
        long txId1 = coordinator.beginTransaction();
        long txId2 = coordinator.beginTransaction();
        
        assertThat(txId1).isLessThan(txId2);
    }

    @Test
    void basicReadWrite_SingleKey() {
        long txId = coordinator.beginTransaction();
        
        assertNull(coordinator.read(txId, "key1"));
        
        coordinator.write(txId, "key1", "value1");
        assertThat(coordinator.read(txId, "key1")).isEqualTo("value1");
        
        coordinator.commit(txId);
        
        // Read in a new transaction
        long newTxId = coordinator.beginTransaction();
        assertThat(coordinator.read(newTxId, "key1")).isEqualTo("value1");
    }

    @Test
    void readYourWrites_SameTransaction() {
        long txId = coordinator.beginTransaction();
        
        coordinator.write(txId, "key1", "value1");
        coordinator.write(txId, "key2", "value2");
        
        assertThat(coordinator.read(txId, "key1")).isEqualTo("value1");
        assertThat(coordinator.read(txId, "key2")).isEqualTo("value2");
        
        coordinator.commit(txId);
    }

    @Test
    void rollback_DiscardsChanges() {
        long txId = coordinator.beginTransaction();
        
        coordinator.write(txId, "key1", "value1");
        coordinator.write(txId, "key2", "value2");
        
        coordinator.rollback(txId);
        
        // After rollback, data should not be visible
        long newTxId = coordinator.beginTransaction();
        assertNull(coordinator.read(newTxId, "key1"));
        assertNull(coordinator.read(newTxId, "key2"));
    }

    @Test
    void snapshotIsolation_TransactionShouldNotSeeUpdatesFromOtherTransaction() {
        // First transaction
        long tx1 = coordinator.beginTransaction();
        coordinator.write(tx1, "key", "value1");
        coordinator.commit(tx1);
        
        // Second transaction starts
        long tx2 = coordinator.beginTransaction();
        assertThat(coordinator.read(tx2, "key")).isEqualTo("value1");
        
        // Third transaction updates value
        long tx3 = coordinator.beginTransaction();
        coordinator.write(tx3, "key", "value2");
        coordinator.commit(tx3);
        
        // Second transaction should still see old value due to snapshot isolation
        assertThat(coordinator.read(tx2, "key")).isEqualTo("value1");
        
        // New transaction should see the new value
        long tx4 = coordinator.beginTransaction();
        assertThat(coordinator.read(tx4, "key")).isEqualTo("value2");
    }

    @Test
    void writesAreVisible_AfterCommit() {
        long tx1 = coordinator.beginTransaction();
        coordinator.write(tx1, "key", "value1");
        
        // Before commit, other transactions shouldn't see the write
        long tx2 = coordinator.beginTransaction();
        assertNull(coordinator.read(tx2, "key"));
        
        // After commit, new transactions should see the write
        coordinator.commit(tx1);
        
        long tx3 = coordinator.beginTransaction();
        assertThat(coordinator.read(tx3, "key")).isEqualTo("value1");
    }

    @Test
    void concurrentWritesToDifferentKeys_ShouldSucceed() throws InterruptedException {
        CountDownLatch latch = new CountDownLatch(2);
        AtomicBoolean success = new AtomicBoolean(true);
        
        Thread t1 = new Thread(() -> {
            try {
                long txId = coordinator.beginTransaction();
                coordinator.write(txId, "key1", "t1_value");
                coordinator.commit(txId);
            } catch (Exception e) {
                success.set(false);
            } finally {
                latch.countDown();
            }
        });
        
        Thread t2 = new Thread(() -> {
            try {
                long txId = coordinator.beginTransaction();
                coordinator.write(txId, "key2", "t2_value");
                coordinator.commit(txId);
            } catch (Exception e) {
                success.set(false);
            } finally {
                latch.countDown();
            }
        });
        
        t1.start();
        t2.start();
        latch.await(5, TimeUnit.SECONDS);
        
        assertTrue(success.get());
        
        // Verify both values are committed
        long verifyTx = coordinator.beginTransaction();
        assertThat(coordinator.read(verifyTx, "key1")).isEqualTo("t1_value");
        assertThat(coordinator.read(verifyTx, "key2")).isEqualTo("t2_value");
    }

    @Test
    void transactionWithMultipleKeys_ShouldCommitAtomically() {
        long txId = coordinator.beginTransaction();
        
        coordinator.write(txId, "key1", "value1");
        coordinator.write(txId, "key2", "value2");
        coordinator.write(txId, "key3", "value3");
        
        coordinator.commit(txId);
        
        // All writes should be visible
        long newTxId = coordinator.beginTransaction();
        assertThat(coordinator.read(newTxId, "key1")).isEqualTo("value1");
        assertThat(coordinator.read(newTxId, "key2")).isEqualTo("value2");
        assertThat(coordinator.read(newTxId, "key3")).isEqualTo("value3");
    }

    @Test
    void cannotUseTransactionAfterCommit() {
        long txId = coordinator.beginTransaction();
        coordinator.write(txId, "key", "value");
        coordinator.commit(txId);
        
        // Further operations on the committed transaction should fail
        assertThatThrownBy(() -> coordinator.read(txId, "key"))
            .isInstanceOf(IllegalStateException.class);
        
        assertThatThrownBy(() -> coordinator.write(txId, "key", "newValue"))
            .isInstanceOf(IllegalStateException.class);
        
        assertThatThrownBy(() -> coordinator.commit(txId))
            .isInstanceOf(IllegalStateException.class);
    }

    @Test
    void cannotUseTransactionAfterRollback() {
        long txId = coordinator.beginTransaction();
        coordinator.write(txId, "key", "value");
        coordinator.rollback(txId);
        
        // Further operations on the rolled back transaction should fail
        assertThatThrownBy(() -> coordinator.read(txId, "key"))
            .isInstanceOf(IllegalStateException.class);
        
        assertThatThrownBy(() -> coordinator.write(txId, "key", "newValue"))
            .isInstanceOf(IllegalStateException.class);
        
        assertThatThrownBy(() -> coordinator.commit(txId))
            .isInstanceOf(IllegalStateException.class);
    }

    @Test
    @Timeout(5) // 5 seconds timeout
    void transactionTimeout_ShouldRollbackAutomatically() throws InterruptedException {
        // Setup: configure a short timeout for test
        coordinator.setTransactionTimeoutMs(100); // 100ms timeout
        
        long txId = coordinator.beginTransaction();
        coordinator.write(txId, "key", "value");
        
        // Wait for the timeout to occur
        Thread.sleep(200);
        
        // Transaction should be automatically rolled back
        assertThatThrownBy(() -> coordinator.commit(txId))
            .isInstanceOf(IllegalStateException.class)
            .hasMessageContaining("timed out");
        
        // Verify the write was not persisted
        long newTxId = coordinator.beginTransaction();
        assertNull(coordinator.read(newTxId, "key"));
    }

    @Test
    void mvcc_OldVersionsAreGarbageCollected() throws InterruptedException {
        // This is hard to test definitively, but we can check that the implementation has a mechanism
        
        // First create some versions
        for (int i = 0; i < 5; i++) {
            long txId = coordinator.beginTransaction();
            coordinator.write(txId, "key", "value" + i);
            coordinator.commit(txId);
        }
        
        // Force garbage collection
        coordinator.runGarbageCollection();
        
        // We can't verify the internal state directly, but we can check that
        // after GC we still get the correct latest value
        long txId = coordinator.beginTransaction();
        assertThat(coordinator.read(txId, "key")).isEqualTo("value4");
    }

    @Test
    void distributedKeys_ShouldBeStoredOnCorrectNodes() {
        long txId = coordinator.beginTransaction();
        
        // Find keys that hash to different nodes
        String key0 = findKeyForNode(0);
        String key1 = findKeyForNode(1);
        String key2 = findKeyForNode(2);
        
        coordinator.write(txId, key0, "value0");
        coordinator.write(txId, key1, "value1");
        coordinator.write(txId, key2, "value2");
        
        coordinator.commit(txId);
        
        // Verify we can read all values
        long newTxId = coordinator.beginTransaction();
        assertThat(coordinator.read(newTxId, key0)).isEqualTo("value0");
        assertThat(coordinator.read(newTxId, key1)).isEqualTo("value1");
        assertThat(coordinator.read(newTxId, key2)).isEqualTo("value2");
    }

    @Test
    void concurrentReadsAndWrites_ShouldMaintainConsistentSnapshots() throws InterruptedException {
        // Write initial value
        long setupTx = coordinator.beginTransaction();
        coordinator.write(setupTx, "counter", "0");
        coordinator.commit(setupTx);
        
        // Start reader transaction
        long readerTx = coordinator.beginTransaction();
        assertThat(coordinator.read(readerTx, "counter")).isEqualTo("0");
        
        // Concurrent writes in separate threads
        int numWriters = 5;
        CountDownLatch writersComplete = new CountDownLatch(numWriters);
        
        for (int i = 0; i < numWriters; i++) {
            final int writerNum = i + 1;
            new Thread(() -> {
                try {
                    long writerTx = coordinator.beginTransaction();
                    String currentValue = coordinator.read(writerTx, "counter");
                    int newValue = Integer.parseInt(currentValue) + 1;
                    coordinator.write(writerTx, "counter", String.valueOf(newValue));
                    coordinator.commit(writerTx);
                } finally {
                    writersComplete.countDown();
                }
            }).start();
        }
        
        // Wait for writers to complete
        writersComplete.await(5, TimeUnit.SECONDS);
        
        // Reader transaction should still see original value due to snapshot isolation
        assertThat(coordinator.read(readerTx, "counter")).isEqualTo("0");
        
        // New transaction should see final result
        long finalTx = coordinator.beginTransaction();
        assertThat(coordinator.read(finalTx, "counter")).isEqualTo(String.valueOf(numWriters));
    }

    // Helper method to find a key that hashes to a specific node
    private String findKeyForNode(int targetNode) {
        int i = 0;
        while (true) {
            String key = "key" + i;
            if (Math.abs(key.hashCode() % NUM_NODES) == targetNode) {
                return key;
            }
            i++;
        }
    }
}