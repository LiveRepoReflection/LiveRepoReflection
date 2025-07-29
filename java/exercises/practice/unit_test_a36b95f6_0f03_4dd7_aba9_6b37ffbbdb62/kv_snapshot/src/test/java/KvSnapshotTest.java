package kv_snapshot;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class KvSnapshotTest {

    // Assume the following interface and exceptions are defined in the project:
    // interface KVStore {
    //     int beginTransaction();
    //     String get(int transactionId, String key);
    //     void put(int transactionId, String key, String value);
    //     void commitTransaction(int transactionId) throws TransactionConflictException, InvalidTransactionException;
    //     void abortTransaction(int transactionId) throws InvalidTransactionException;
    // }
    //
    // class TransactionConflictException extends Exception {
    //     public TransactionConflictException(String message) {
    //         super(message);
    //     }
    // }
    //
    // class InvalidTransactionException extends Exception {
    //     public InvalidTransactionException(String message) {
    //         super(message);
    //     }
    // }
    //
    // Also assume there exists a concrete implementation KVStoreImpl of the KVStore interface.

    @Test
    public void testEmptyStoreGetReturnsNull() throws Exception {
        KVStore store = new KVStoreImpl();
        int txn = store.beginTransaction();
        assertNull(store.get(txn, "nonexistent"), "Getting a key that hasn't been set should return null.");
        store.abortTransaction(txn);
    }

    @Test
    public void testSingleTransactionCommit() throws Exception {
        KVStore store = new KVStoreImpl();
        int txn = store.beginTransaction();
        store.put(txn, "a", "alpha");
        store.commitTransaction(txn);

        int txn2 = store.beginTransaction();
        assertEquals("alpha", store.get(txn2, "a"), "Committed value should be visible in a new transaction.");
        store.abortTransaction(txn2);
    }

    @Test
    public void testAbortTransactionNotPersisted() throws Exception {
        KVStore store = new KVStoreImpl();
        int txn = store.beginTransaction();
        store.put(txn, "b", "beta");
        store.abortTransaction(txn);

        int txn2 = store.beginTransaction();
        assertNull(store.get(txn2, "b"), "Aborted transaction should not persist changes.");
        store.abortTransaction(txn2);
    }

    @Test
    public void testSnapshotIsolation() throws Exception {
        KVStore store = new KVStoreImpl();

        // Initialize key 'x' with value "v1"
        int txnInit = store.beginTransaction();
        store.put(txnInit, "x", "v1");
        store.commitTransaction(txnInit);

        // Begin transaction A which should get a snapshot of the current state.
        int txnA = store.beginTransaction();
        assertEquals("v1", store.get(txnA, "x"), "Transaction A should see the initial value 'v1' for key 'x'.");

        // Transaction B updates key 'x' and commits.
        int txnB = store.beginTransaction();
        store.put(txnB, "x", "v2");
        store.commitTransaction(txnB);

        // Transaction A continues to see the old snapshot.
        assertEquals("v1", store.get(txnA, "x"), "Transaction A should continue to see the initial value despite subsequent commits.");
        store.commitTransaction(txnA);

        // A new transaction should see the updated value.
        int txnC = store.beginTransaction();
        assertEquals("v2", store.get(txnC, "x"), "New transactions should see the updated value 'v2' for key 'x'.");
        store.abortTransaction(txnC);
    }

    @Test
    public void testConcurrentConflict() throws Exception {
        KVStore store = new KVStoreImpl();

        // Initialize key 'y' with "initial"
        int txnInit = store.beginTransaction();
        store.put(txnInit, "y", "initial");
        store.commitTransaction(txnInit);

        // Start two concurrent transactions
        int txn1 = store.beginTransaction();
        int txn2 = store.beginTransaction();

        // Both update key 'y'
        store.put(txn1, "y", "txn1");
        store.put(txn2, "y", "txn2");

        // Commit txn1 should succeed.
        store.commitTransaction(txn1);

        // Attempting to commit txn2 should trigger a conflict.
        Exception conflictException = assertThrows(TransactionConflictException.class, () -> {
            store.commitTransaction(txn2);
        });
        assertNotNull(conflictException.getMessage());

        // Validate that a new transaction sees the committed update from txn1.
        int txn3 = store.beginTransaction();
        assertEquals("txn1", store.get(txn3, "y"), "Committed value from txn1 should be visible.");
        store.abortTransaction(txn3);
    }

    @Test
    public void testInvalidTransactionOperations() throws Exception {
        KVStore store = new KVStoreImpl();

        // Committing an invalid transaction id should throw an exception.
        Exception commitException = assertThrows(InvalidTransactionException.class, () -> {
            store.commitTransaction(-1);
        });
        assertNotNull(commitException.getMessage());

        // Aborting an invalid transaction id should throw an exception.
        Exception abortException = assertThrows(InvalidTransactionException.class, () -> {
            store.abortTransaction(9999);
        });
        assertNotNull(abortException.getMessage());
    }

    @Test
    public void testMultipleTransactionsIsolation() throws Exception {
        KVStore store = new KVStoreImpl();

        // Setup initial state for keys 'a' and 'b'
        int initTxn = store.beginTransaction();
        store.put(initTxn, "a", "1");
        store.put(initTxn, "b", "2");
        store.commitTransaction(initTxn);

        // Start two concurrent transactions
        int t1 = store.beginTransaction();
        int t2 = store.beginTransaction();

        // Transaction t1 updates both keys.
        store.put(t1, "a", "10");
        store.put(t1, "b", "20");

        // Transaction t2 should see the original snapshot.
        assertEquals("1", store.get(t2, "a"), "t2 should see the initial value for key 'a'.");
        assertEquals("2", store.get(t2, "b"), "t2 should see the initial value for key 'b'.");

        // Commit t1.
        store.commitTransaction(t1);

        // t2 continues to see old snapshot even after t1's commit.
        assertEquals("1", store.get(t2, "a"), "t2 must continue to see its snapshot for key 'a'.");
        assertEquals("2", store.get(t2, "b"), "t2 must continue to see its snapshot for key 'b'.");
        store.commitTransaction(t2);

        // A new transaction should see the updated values.
        int t3 = store.beginTransaction();
        assertEquals("10", store.get(t3, "a"), "t3 should see the updated value for key 'a'.");
        assertEquals("20", store.get(t3, "b"), "t3 should see the updated value for key 'b'.");
        store.abortTransaction(t3);
    }
}