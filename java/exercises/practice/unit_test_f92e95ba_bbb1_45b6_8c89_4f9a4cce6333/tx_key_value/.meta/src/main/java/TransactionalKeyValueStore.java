import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

public class TransactionalKeyValueStore {

    private static class TransactionRecord {
        final UUID transactionId;
        final long snapshotVersion;
        final Map<String, String> writes = new HashMap<>();

        TransactionRecord(UUID transactionId, long snapshotVersion) {
            this.transactionId = transactionId;
            this.snapshotVersion = snapshotVersion;
        }
    }

    private final Map<UUID, TransactionRecord> transactions = new HashMap<>();
    private final Map<String, VersionedValue> store = new HashMap<>();
    private long globalVersion = 0L;

    public synchronized UUID beginTransaction() {
        UUID txId = UUID.randomUUID();
        long snapshot = globalVersion;
        TransactionRecord txRecord = new TransactionRecord(txId, snapshot);
        transactions.put(txId, txRecord);
        return txId;
    }

    public synchronized String read(UUID transactionId, String key) {
        TransactionRecord txRecord = transactions.get(transactionId);
        if (txRecord == null) {
            throw new IllegalArgumentException("Transaction not found: " + transactionId);
        }
        // Return the value from the transaction's local writes first, if present.
        if (txRecord.writes.containsKey(key)) {
            return txRecord.writes.get(key);
        }
        // Otherwise, return the value from the global store if its version is valid in the transaction's snapshot.
        VersionedValue versionedValue = store.get(key);
        if (versionedValue != null && versionedValue.version <= txRecord.snapshotVersion) {
            return versionedValue.value;
        }
        return null;
    }

    public synchronized void write(UUID transactionId, String key, String value) {
        TransactionRecord txRecord = transactions.get(transactionId);
        if (txRecord == null) {
            throw new IllegalArgumentException("Transaction not found: " + transactionId);
        }
        txRecord.writes.put(key, value);
    }

    public synchronized void commitTransaction(UUID transactionId) throws ConflictException {
        TransactionRecord txRecord = transactions.get(transactionId);
        if (txRecord == null) {
            throw new IllegalArgumentException("Transaction not found: " + transactionId);
        }
        // Check for write conflicts: if any key written has been updated after transaction's snapshot, throw conflict exception.
        for (String key : txRecord.writes.keySet()) {
            VersionedValue currentValue = store.get(key);
            if (currentValue != null && currentValue.version > txRecord.snapshotVersion) {
                transactions.remove(transactionId);
                throw new ConflictException("Write conflict detected for key: " + key);
            }
        }
        // Commit the writes and update the global version.
        for (Map.Entry<String, String> entry : txRecord.writes.entrySet()) {
            globalVersion++;
            store.put(entry.getKey(), new VersionedValue(entry.getValue(), globalVersion));
        }
        transactions.remove(transactionId);
    }

    public synchronized void rollbackTransaction(UUID transactionId) {
        if (!transactions.containsKey(transactionId)) {
            throw new IllegalArgumentException("Transaction not found: " + transactionId);
        }
        transactions.remove(transactionId);
    }
}