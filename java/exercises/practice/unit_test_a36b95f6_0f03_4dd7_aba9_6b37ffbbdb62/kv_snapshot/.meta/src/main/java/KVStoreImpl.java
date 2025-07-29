package kv_snapshot;

import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.*;

public class KVStoreImpl implements KVStore {

    private static final int NODE_COUNT = 3;

    private final AtomicInteger transactionCounter = new AtomicInteger(0);
    private final AtomicInteger globalVersion = new AtomicInteger(0);
    private final ConcurrentHashMap<Integer, Transaction> activeTransactions = new ConcurrentHashMap<>();
    private final Node[] nodes = new Node[NODE_COUNT];

    public KVStoreImpl() {
        for (int i = 0; i < NODE_COUNT; i++) {
            nodes[i] = new Node();
        }
    }

    private int getNodeIndex(String key) {
        return Math.abs(key.hashCode()) % NODE_COUNT;
    }

    private Node getNode(String key) {
        return nodes[getNodeIndex(key)];
    }

    // Inner class to represent a transaction.
    private class Transaction {
        int transactionId;
        int snapshotVersion;
        HashMap<String, String> writes;
        boolean active;

        Transaction(int transactionId, int snapshotVersion) {
            this.transactionId = transactionId;
            this.snapshotVersion = snapshotVersion;
            this.writes = new HashMap<>();
            this.active = true;
        }
    }

    // Inner class to represent a node/shard.
    private class Node {
        // Mapping from key to a sorted map of version -> value.
        Map<String, TreeMap<Integer, String>> store;

        Node() {
            store = new HashMap<>();
        }
    }

    @Override
    public int beginTransaction() {
        int txnId = transactionCounter.incrementAndGet();
        int snapVersion = globalVersion.get();
        Transaction txn = new Transaction(txnId, snapVersion);
        activeTransactions.put(txnId, txn);
        return txnId;
    }

    @Override
    public String get(int transactionId, String key) throws InvalidTransactionException {
        Transaction txn = activeTransactions.get(transactionId);
        if (txn == null || !txn.active) {
            throw new InvalidTransactionException("Transaction " + transactionId + " is invalid or not active.");
        }
        // Check in the transaction's write buffer first.
        if (txn.writes.containsKey(key)) {
            return txn.writes.get(key);
        }
        // Retrieve the value from the corresponding node at the snapshot version.
        Node node = getNode(key);
        synchronized (node) {
            TreeMap<Integer, String> versions = node.store.get(key);
            if (versions == null) {
                return null;
            }
            Map.Entry<Integer, String> entry = versions.floorEntry(txn.snapshotVersion);
            if (entry == null) {
                return null;
            }
            return entry.getValue();
        }
    }

    @Override
    public void put(int transactionId, String key, String value) throws InvalidTransactionException {
        Transaction txn = activeTransactions.get(transactionId);
        if (txn == null || !txn.active) {
            throw new InvalidTransactionException("Transaction " + transactionId + " is invalid or not active.");
        }
        txn.writes.put(key, value);
    }

    @Override
    public void commitTransaction(int transactionId) throws TransactionConflictException, InvalidTransactionException {
        Transaction txn = activeTransactions.get(transactionId);
        if (txn == null || !txn.active) {
            throw new InvalidTransactionException("Transaction " + transactionId + " is invalid or not active.");
        }
        // Synchronize globally to perform commit atomically.
        synchronized (globalVersion) {
            // Check for write-write conflicts.
            for (Map.Entry<String, String> entry : txn.writes.entrySet()) {
                String key = entry.getKey();
                Node node = getNode(key);
                synchronized (node) {
                    TreeMap<Integer, String> versions = node.store.get(key);
                    if (versions != null && !versions.isEmpty()) {
                        int latestVersion = versions.lastKey();
                        if (latestVersion > txn.snapshotVersion) {
                            txn.active = false;
                            activeTransactions.remove(transactionId);
                            throw new TransactionConflictException("Conflict detected for key: " + key);
                        }
                    }
                }
            }
            // No conflicts found; proceed to commit.
            int newVersion = globalVersion.incrementAndGet();
            for (Map.Entry<String, String> entry : txn.writes.entrySet()) {
                String key = entry.getKey();
                String value = entry.getValue();
                Node node = getNode(key);
                synchronized (node) {
                    TreeMap<Integer, String> versions = node.store.get(key);
                    if (versions == null) {
                        versions = new TreeMap<>();
                        node.store.put(key, versions);
                    }
                    versions.put(newVersion, value);
                }
            }
            txn.active = false;
            activeTransactions.remove(transactionId);
        }
    }

    @Override
    public void abortTransaction(int transactionId) throws InvalidTransactionException {
        Transaction txn = activeTransactions.get(transactionId);
        if (txn == null || !txn.active) {
            throw new InvalidTransactionException("Transaction " + transactionId + " is invalid or not active.");
        }
        txn.active = false;
        activeTransactions.remove(transactionId);
    }
}