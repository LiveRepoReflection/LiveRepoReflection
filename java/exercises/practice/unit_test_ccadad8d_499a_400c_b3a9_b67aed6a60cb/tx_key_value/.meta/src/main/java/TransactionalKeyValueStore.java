import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

public class TransactionalKeyValueStore {
    private static final AtomicLong transactionIdGenerator = new AtomicLong(1);
    private static final AtomicLong commitVersionGenerator = new AtomicLong(0);
    private static final Object commitLock = new Object();

    private final ConcurrentHashMap<String, ValueEntry> globalStore = new ConcurrentHashMap<>();
    private final ConcurrentHashMap<Long, Transaction> activeTransactions = new ConcurrentHashMap<>();
    private final File walFile;
    private final Object walLock = new Object();

    public TransactionalKeyValueStore() {
        walFile = new File("tx_key_value_wal.log");
        try {
            if (!walFile.exists()) {
                walFile.createNewFile();
            }
        } catch (IOException e) {
            throw new RuntimeException("Failed to create WAL file", e);
        }
    }

    public long beginTransaction() {
        long txnId = transactionIdGenerator.getAndIncrement();
        long snapshotVersion = commitVersionGenerator.get();
        Transaction txn = new Transaction(txnId, snapshotVersion);
        activeTransactions.put(txnId, txn);
        return txnId;
    }

    public String get(String key, long transactionId) {
        Transaction txn = activeTransactions.get(transactionId);
        if (txn == null) {
            throw new IllegalArgumentException("Transaction does not exist");
        }
        if (txn.localWrites.containsKey(key)) {
            return txn.localWrites.get(key);
        }
        ValueEntry entry = globalStore.get(key);
        if (entry != null && entry.commitVersion <= txn.snapshotVersion) {
            return entry.value;
        }
        return null;
    }

    public void put(String key, String value, long transactionId) {
        Transaction txn = activeTransactions.get(transactionId);
        if (txn == null) {
            throw new IllegalArgumentException("Transaction does not exist");
        }
        txn.localWrites.put(key, value);
    }

    public void commitTransaction(long transactionId) {
        Transaction txn = activeTransactions.remove(transactionId);
        if (txn == null) {
            throw new IllegalArgumentException("Transaction does not exist");
        }
        synchronized (commitLock) {
            long newCommitVersion = commitVersionGenerator.incrementAndGet();
            synchronized (walLock) {
                try (FileWriter fw = new FileWriter(walFile, true)) {
                    for (Map.Entry<String, String> e : txn.localWrites.entrySet()) {
                        // Writing: commitVersion,transactionId,key,value
                        fw.write(newCommitVersion + "," + transactionId + "," + e.getKey() + "," + e.getValue() + "\n");
                    }
                    fw.flush();
                } catch (IOException ex) {
                    throw new RuntimeException("WAL write failed", ex);
                }
            }
            for (Map.Entry<String, String> e : txn.localWrites.entrySet()) {
                globalStore.put(e.getKey(), new ValueEntry(e.getValue(), newCommitVersion));
            }
        }
    }

    public void abortTransaction(long transactionId) {
        Transaction txn = activeTransactions.remove(transactionId);
        if (txn == null) {
            throw new IllegalArgumentException("Transaction does not exist");
        }
        // Aborting simply discards the local writes.
    }

    private static class ValueEntry {
        String value;
        long commitVersion;

        ValueEntry(String value, long commitVersion) {
            this.value = value;
            this.commitVersion = commitVersion;
        }
    }

    private static class Transaction {
        long transactionId;
        long snapshotVersion;
        ConcurrentHashMap<String, String> localWrites = new ConcurrentHashMap<>();

        Transaction(long transactionId, long snapshotVersion) {
            this.transactionId = transactionId;
            this.snapshotVersion = snapshotVersion;
        }
    }
}