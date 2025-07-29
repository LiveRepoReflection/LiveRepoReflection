import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

public class TransactionalKeyValueStore {

    private final Map<String, String> globalStore;
    private final Map<String, Transaction> transactions;
    private final Object commitLock;

    public TransactionalKeyValueStore() {
        this.globalStore = new ConcurrentHashMap<>();
        this.transactions = new ConcurrentHashMap<>();
        this.commitLock = new Object();
    }

    public String beginTransaction() {
        String txId = UUID.randomUUID().toString();
        Transaction tx = new Transaction(txId);
        transactions.put(txId, tx);
        return txId;
    }

    public String read(String txId, String key) {
        Transaction tx = transactions.get(txId);
        if (tx == null) {
            throw new IllegalStateException("Transaction not found");
        }
        // Return the locally written value if present
        if (tx.localWrites.containsKey(key)) {
            return tx.localWrites.get(key);
        }
        return globalStore.get(key);
    }

    public void write(String txId, String key, String value) {
        Transaction tx = transactions.get(txId);
        if (tx == null) {
            throw new IllegalStateException("Transaction not found");
        }
        tx.localWrites.put(key, value);
    }

    public void commitTransaction(String txId) {
        Transaction tx = transactions.get(txId);
        if (tx == null) {
            throw new IllegalStateException("Transaction not found");
        }
        synchronized (commitLock) {
            // Apply all writes atomically to the global store
            for (Map.Entry<String, String> entry : tx.localWrites.entrySet()) {
                globalStore.put(entry.getKey(), entry.getValue());
            }
        }
        transactions.remove(txId);
    }

    public void rollbackTransaction(String txId) {
        Transaction tx = transactions.get(txId);
        if (tx == null) {
            throw new IllegalStateException("Transaction not found");
        }
        // Simply discard the uncommitted changes
        transactions.remove(txId);
    }

    private static class Transaction {
        private final String transactionId;
        private final Map<String, String> localWrites;

        Transaction(String transactionId) {
            this.transactionId = transactionId;
            this.localWrites = new ConcurrentHashMap<>();
        }
    }
}