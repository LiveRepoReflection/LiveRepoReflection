import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.ArrayList;
import java.util.List;

public class TxKeyValueStoreTest {

    private TransactionalKeyValueStore store;

    @BeforeEach
    public void setup() {
        // Assume that the TransactionalKeyValueStore class has a no-arg constructor.
        store = new TransactionalKeyValueStore();
    }

    @Test
    public void testSingleTransactionCommit() {
        long txn = store.beginTransaction();
        store.put("key1", "value1", txn);
        store.put("key2", "value2", txn);

        // Within the same transaction, the changes should be visible.
        assertEquals("value1", store.get("key1", txn));
        assertEquals("value2", store.get("key2", txn));

        // Commit the transaction.
        store.commitTransaction(txn);

        // In a new transaction, the committed changes should be visible.
        long txn2 = store.beginTransaction();
        assertEquals("value1", store.get("key1", txn2));
        assertEquals("value2", store.get("key2", txn2));
        store.commitTransaction(txn2);
    }

    @Test
    public void testSingleTransactionAbort() {
        long txn = store.beginTransaction();
        store.put("key1", "value1", txn);
        store.put("key2", "value2", txn);

        // Within the same transaction, the changes are visible.
        assertEquals("value1", store.get("key1", txn));
        assertEquals("value2", store.get("key2", txn));

        // Abort the transaction.
        store.abortTransaction(txn);

        // A new transaction should not see the aborted changes.
        long txn2 = store.beginTransaction();
        assertNull(store.get("key1", txn2));
        assertNull(store.get("key2", txn2));
        store.commitTransaction(txn2);
    }

    @Test
    public void testSnapshotIsolation() {
        // Start two concurrent transactions.
        long txn1 = store.beginTransaction();
        long txn2 = store.beginTransaction();

        // In txn1, put a key.
        store.put("keyA", "valueA1", txn1);
        // In txn2, the key should not be visible yet.
        assertNull(store.get("keyA", txn2));

        // Commit txn1; txn2 should still have its snapshot.
        store.commitTransaction(txn1);
        assertNull(store.get("keyA", txn2));

        // Start a new transaction to see committed changes.
        long txn3 = store.beginTransaction();
        assertEquals("valueA1", store.get("keyA", txn3));
        store.commitTransaction(txn2);
        store.commitTransaction(txn3);
    }

    @Test
    public void testOverwriteWithinTransaction() {
        // Write an initial value.
        long txn1 = store.beginTransaction();
        store.put("keyB", "initial", txn1);
        store.commitTransaction(txn1);

        // Overwrite the value in a new transaction.
        long txn2 = store.beginTransaction();
        assertEquals("initial", store.get("keyB", txn2));
        store.put("keyB", "updated", txn2);
        // Within the same transaction, the new value is visible.
        assertEquals("updated", store.get("keyB", txn2));
        store.commitTransaction(txn2);

        // Verify the updated value in a new transaction.
        long txn3 = store.beginTransaction();
        assertEquals("updated", store.get("keyB", txn3));
        store.commitTransaction(txn3);
    }

    @Test
    public void testMultipleWritesSameTransaction() {
        long txn = store.beginTransaction();
        store.put("keyC", "first", txn);
        store.put("keyC", "second", txn);
        store.put("keyC", "final", txn);
        // The latest write should be visible in the same transaction.
        assertEquals("final", store.get("keyC", txn));
        store.commitTransaction(txn);

        long txn2 = store.beginTransaction();
        assertEquals("final", store.get("keyC", txn2));
        store.commitTransaction(txn2);
    }

    @Test
    public void testAbortPreventsVisibility() {
        long txn = store.beginTransaction();
        store.put("keyD", "temp", txn);
        assertEquals("temp", store.get("keyD", txn));
        store.abortTransaction(txn);

        // Verify that an aborted write is not visible in a new transaction.
        long txn2 = store.beginTransaction();
        assertNull(store.get("keyD", txn2));
        store.commitTransaction(txn2);
    }

    @Test
    public void testConcurrentTransactions() throws InterruptedException, ExecutionException {
        final int numThreads = 10;
        ExecutorService executor = Executors.newFixedThreadPool(numThreads);
        List<Callable<Void>> tasks = new ArrayList<>();
        final String key = "commonKey";

        // Commit an initial value to the key.
        long initTxn = store.beginTransaction();
        store.put(key, "init", initTxn);
        store.commitTransaction(initTxn);

        for (int i = 0; i < numThreads; i++) {
            final int threadNum = i;
            tasks.add(() -> {
                long txn = store.beginTransaction();
                String currentValue = store.get(key, txn);
                // Simulate processing delay.
                Thread.sleep(50);
                store.put(key, currentValue + "-" + threadNum, txn);
                store.commitTransaction(txn);
                return null;
            });
        }

        List<Future<Void>> futures = executor.invokeAll(tasks);
        for (Future<Void> future : futures) {
            future.get();
        }
        executor.shutdown();

        // In a new transaction, the final value should reflect one of the committed updates.
        long txnFinal = store.beginTransaction();
        String finalValue = store.get(key, txnFinal);
        assertTrue(finalValue.startsWith("init"));
        store.commitTransaction(txnFinal);
    }
}