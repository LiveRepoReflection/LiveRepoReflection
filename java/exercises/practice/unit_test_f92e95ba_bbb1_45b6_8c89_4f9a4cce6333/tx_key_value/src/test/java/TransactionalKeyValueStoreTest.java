import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;

public class TransactionalKeyValueStoreTest {

    private TransactionalKeyValueStore store;

    @BeforeEach
    public void setUp() {
        store = new TransactionalKeyValueStore();
    }

    @Test
    public void testBeginTransactionReturnsUniqueId() {
        UUID txId1 = store.beginTransaction();
        UUID txId2 = store.beginTransaction();
        assertNotNull(txId1, "First transaction ID should not be null");
        assertNotNull(txId2, "Second transaction ID should not be null");
        assertNotEquals(txId1, txId2, "Transaction IDs should be unique");
    }

    @Test
    public void testSimpleReadWriteCommit() throws Exception {
        UUID txId = store.beginTransaction();

        // Initially, key does not exist.
        String value = store.read(txId, "key1");
        assertNull(value, "Initial read for non-existing key should return null");

        // Write a key value pair in the transaction.
        store.write(txId, "key1", "value1");

        // Read within the same transaction returns the new value.
        value = store.read(txId, "key1");
        assertEquals("value1", value, "Value within transaction must reflect the write");

        // Commit the transaction.
        store.commitTransaction(txId);

        // Start a new transaction to see the committed value.
        UUID txId2 = store.beginTransaction();
        value = store.read(txId2, "key1");
        assertEquals("value1", value, "Committed value must be visible in new transaction");
    }

    @Test
    public void testSnapshotIsolation() throws Exception {
        // Start transaction A and write a value.
        UUID txA = store.beginTransaction();
        store.write(txA, "sharedKey", "A_value");

        // Start transaction B after A begins but before A commits.
        UUID txB = store.beginTransaction();
        String readB = store.read(txB, "sharedKey");
        // Because of snapshot isolation, transaction B should not see A's uncommitted changes.
        assertNull(readB, "Transaction B must not see uncommitted changes from transaction A");

        // Commit transaction A.
        store.commitTransaction(txA);

        // Transaction B is still working on its snapshot and should not see the committed value.
        readB = store.read(txB, "sharedKey");
        assertNull(readB, "Transaction B's snapshot should not change even after A commits");

        // A new transaction C should see A's committed value.
        UUID txC = store.beginTransaction();
        String readC = store.read(txC, "sharedKey");
        assertEquals("A_value", readC, "New transaction should see committed value from A");
    }

    @Test
    public void testRollbackTransaction() throws Exception {
        // Write a value in a transaction then rollback.
        UUID txId = store.beginTransaction();
        store.write(txId, "key_rollback", "temp_value");

        // Before rollback, value should be visible inside the transaction.
        String value = store.read(txId, "key_rollback");
        assertEquals("temp_value", value, "Value must be visible inside the transaction before rollback");

        // Rollback the transaction.
        store.rollbackTransaction(txId);

        // A new transaction should not see the rolled back value.
        UUID txNew = store.beginTransaction();
        value = store.read(txNew, "key_rollback");
        assertNull(value, "Rolled back changes must not be visible in new transactions");
    }

    @Test
    public void testConcurrentWriteConflict() throws Exception {
        // Start two concurrent transactions.
        UUID tx1 = store.beginTransaction();
        UUID tx2 = store.beginTransaction();

        // Both transactions write to the same key.
        store.write(tx1, "conflictKey", "tx1_value");
        store.write(tx2, "conflictKey", "tx2_value");

        // Commit tx1 successfully.
        store.commitTransaction(tx1);

        // Attempt to commit tx2, expecting a conflict exception.
        Exception exception = assertThrows(ConflictException.class, new Executable() {
            @Override
            public void execute() throws Throwable {
                store.commitTransaction(tx2);
            }
        }, "Commit of tx2 should fail due to write conflict");

        String expectedMessage = "Write conflict detected";
        String actualMessage = exception.getMessage();
        assertTrue(actualMessage.contains(expectedMessage),
                "Exception message must contain the conflict message");
    }

    @Test
    public void testDoesNotMutateInputSnapshot() throws Exception {
        // Begin a transaction and read a key that does not exist.
        UUID txId = store.beginTransaction();
        String valueBefore = store.read(txId, "immutableKey");
        assertNull(valueBefore, "Initial read should return null");

        // Write a new value and read again in the same transaction.
        store.write(txId, "immutableKey", "newValue");
        String valueAfter = store.read(txId, "immutableKey");
        assertEquals("newValue", valueAfter, "Read after write within the transaction must be new value");

        // Start a new transaction and ensure it does not reflect the in-progress transaction's changes.
        UUID txIdNew = store.beginTransaction();
        String valueNewTx = store.read(txIdNew, "immutableKey");
        assertNull(valueNewTx, "New transaction must not see in-progress uncommitted changes");
    }
}