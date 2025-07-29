import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicLong;

/**
 * The TransactionCoordinator is the main entry point for the distributed key-value store.
 * It manages transactions across multiple nodes and implements the two-phase commit protocol.
 */
public class TransactionCoordinator {
    private final Node[] nodes;
    private final AtomicLong timestampGenerator = new AtomicLong(1);
    private final Map<Long, Transaction> transactions = new ConcurrentHashMap<>();
    private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(2);
    private long transactionTimeoutMs = 30000; // Default: 30 seconds

    public TransactionCoordinator(int numNodes) {
        this.nodes = new Node[numNodes];
        for (int i = 0; i < numNodes; i++) {
            this.nodes[i] = new Node(i);
        }
        
        // Start the garbage collection process
        scheduler.scheduleAtFixedRate(this::runGarbageCollection, 
                10, 10, TimeUnit.SECONDS);
        
        // Start transaction timeout checker
        scheduler.scheduleAtFixedRate(this::checkTransactionTimeouts, 
                1, 1, TimeUnit.SECONDS);
    }

    /**
     * Begins a new transaction and returns the transaction ID.
     */
    public long beginTransaction() {
        long txId = timestampGenerator.getAndIncrement();
        Transaction tx = new Transaction(txId);
        transactions.put(txId, tx);
        return txId;
    }

    /**
     * Reads a value for the specified key within the given transaction.
     */
    public String read(long txId, String key) {
        Transaction tx = getActiveTransaction(txId);
        
        // Check if the key has been written in this transaction
        if (tx.writeset.containsKey(key)) {
            return tx.writeset.get(key);
        }
        
        // Determine which node holds this key
        Node node = getNodeForKey(key);
        
        // Read the value at this transaction's timestamp
        return node.read(key, tx.timestamp);
    }

    /**
     * Writes a value for the specified key within the given transaction.
     */
    public void write(long txId, String key, String value) {
        Transaction tx = getActiveTransaction(txId);
        tx.writeset.put(key, value);
        
        // Track which keys were written to which nodes for 2PC
        int nodeIndex = getNodeIndexForKey(key);
        tx.nodeWrites.computeIfAbsent(nodeIndex, k -> new HashMap<>())
                    .put(key, value);
    }

    /**
     * Commits the transaction using two-phase commit protocol.
     */
    public void commit(long txId) {
        Transaction tx = getActiveTransaction(txId);
        
        // Phase 1: Prepare
        boolean allPrepared = true;
        for (Map.Entry<Integer, Map<String, String>> entry : tx.nodeWrites.entrySet()) {
            int nodeIndex = entry.getKey();
            Map<String, String> nodeWrites = entry.getValue();
            
            if (!nodes[nodeIndex].prepare(tx.timestamp, nodeWrites)) {
                allPrepared = false;
                break;
            }
        }
        
        // Phase 2: Commit or Abort
        if (allPrepared) {
            for (Map.Entry<Integer, Map<String, String>> entry : tx.nodeWrites.entrySet()) {
                int nodeIndex = entry.getKey();
                nodes[nodeIndex].commit(tx.timestamp);
            }
            tx.state = TransactionState.COMMITTED;
        } else {
            // If prepare failed, abort the transaction
            for (Map.Entry<Integer, Map<String, String>> entry : tx.nodeWrites.entrySet()) {
                int nodeIndex = entry.getKey();
                nodes[nodeIndex].rollback(tx.timestamp);
            }
            tx.state = TransactionState.ABORTED;
            throw new RuntimeException("Transaction commit failed");
        }
    }

    /**
     * Rolls back the transaction.
     */
    public void rollback(long txId) {
        Transaction tx = getActiveTransaction(txId);
        
        // Rollback any prepared changes on nodes
        for (Map.Entry<Integer, Map<String, String>> entry : tx.nodeWrites.entrySet()) {
            int nodeIndex = entry.getKey();
            nodes[nodeIndex].rollback(tx.timestamp);
        }
        
        tx.state = TransactionState.ABORTED;
    }

    /**
     * Sets the transaction timeout in milliseconds.
     */
    public void setTransactionTimeoutMs(long timeoutMs) {
        this.transactionTimeoutMs = timeoutMs;
    }

    /**
     * Runs the garbage collection process to clean up old versions.
     * This is public for testing purposes.
     */
    public void runGarbageCollection() {
        // Find the oldest active transaction timestamp
        long oldestActiveTimestamp = Long.MAX_VALUE;
        
        for (Transaction tx : transactions.values()) {
            if (tx.state == TransactionState.ACTIVE && tx.timestamp < oldestActiveTimestamp) {
                oldestActiveTimestamp = tx.timestamp;
            }
        }
        
        // If there are no active transactions, use the current timestamp
        if (oldestActiveTimestamp == Long.MAX_VALUE) {
            oldestActiveTimestamp = timestampGenerator.get();
        }
        
        // Run garbage collection on each node
        for (Node node : nodes) {
            node.garbageCollect(oldestActiveTimestamp);
        }
    }

    /**
     * Checks for transaction timeouts and aborts any timed out transactions.
     */
    private void checkTransactionTimeouts() {
        long now = System.currentTimeMillis();
        List<Long> timedOutTxns = new ArrayList<>();
        
        for (Transaction tx : transactions.values()) {
            if (tx.state == TransactionState.ACTIVE && 
                    now - tx.startTimeMs > transactionTimeoutMs) {
                timedOutTxns.add(tx.timestamp);
            }
        }
        
        // Abort timed out transactions
        for (Long txId : timedOutTxns) {
            Transaction tx = transactions.get(txId);
            
            // Make sure another thread hasn't already handled this
            if (tx != null && tx.state == TransactionState.ACTIVE) {
                tx.state = TransactionState.ABORTED;
                
                // Rollback any prepared changes on nodes
                for (Map.Entry<Integer, Map<String, String>> entry : tx.nodeWrites.entrySet()) {
                    int nodeIndex = entry.getKey();
                    nodes[nodeIndex].rollback(tx.timestamp);
                }
            }
        }
    }

    /**
     * Gets the node that stores the specified key.
     */
    private Node getNodeForKey(String key) {
        int nodeIndex = getNodeIndexForKey(key);
        return nodes[nodeIndex];
    }

    /**
     * Gets the index of the node that stores the specified key.
     */
    private int getNodeIndexForKey(String key) {
        return Math.abs(key.hashCode() % nodes.length);
    }

    /**
     * Gets an active transaction by its ID, throws if it's not active.
     */
    private Transaction getActiveTransaction(long txId) {
        Transaction tx = transactions.get(txId);
        
        if (tx == null) {
            throw new IllegalArgumentException("Transaction " + txId + " does not exist");
        }
        
        if (tx.state == TransactionState.COMMITTED) {
            throw new IllegalStateException("Transaction " + txId + " is already committed");
        }
        
        if (tx.state == TransactionState.ABORTED) {
            throw new IllegalStateException("Transaction " + txId + " is aborted");
        }
        
        if (tx.state == TransactionState.ACTIVE && 
                System.currentTimeMillis() - tx.startTimeMs > transactionTimeoutMs) {
            tx.state = TransactionState.ABORTED;
            throw new IllegalStateException("Transaction " + txId + " has timed out");
        }
        
        return tx;
    }

    /**
     * Shutdown the coordinator's background threads.
     */
    public void shutdown() {
        scheduler.shutdownNow();
    }
}