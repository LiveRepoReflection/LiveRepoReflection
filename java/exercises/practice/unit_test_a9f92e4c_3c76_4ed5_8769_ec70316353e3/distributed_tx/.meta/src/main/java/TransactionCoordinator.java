import java.util.Set;
import java.util.HashSet;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.ScheduledFuture;
import java.util.concurrent.TimeUnit;

public class TransactionCoordinator {
    
    private final ConcurrentMap<UUID, Transaction> transactions;
    private final ScheduledExecutorService scheduler;
    // Timeout in seconds for a transaction to complete voting.
    private static final int TIMEOUT_SECONDS = 10;
    
    public TransactionCoordinator() {
        this.transactions = new ConcurrentHashMap<>();
        this.scheduler = Executors.newScheduledThreadPool(1);
    }
    
    public void startTransaction(UUID transactionId, Set<Integer> involvedNodes) {
        if (transactionId == null || involvedNodes == null || involvedNodes.isEmpty()) {
            throw new IllegalArgumentException("Invalid transactionId or involvedNodes");
        }
        // Create a copy of involved nodes to avoid external modifications.
        Transaction transaction = new Transaction(transactionId, new HashSet<>(involvedNodes));
        // Schedule a timeout task that will abort the transaction if not all votes are received within TIMEOUT_SECONDS.
        ScheduledFuture<?> timeoutTask = scheduler.schedule(() -> {
            transaction.timeout();
        }, TIMEOUT_SECONDS, TimeUnit.SECONDS);
        transaction.setTimeoutTask(timeoutTask);
        transactions.put(transactionId, transaction);
    }
    
    public void receiveVote(UUID transactionId, int nodeId, boolean vote) {
        Transaction txn = transactions.get(transactionId);
        if (txn == null) {
            return;
        }
        txn.processVote(nodeId, vote);
    }
    
    public void handleNodeFailure(int nodeId) {
        // Iterate over all ongoing transactions and process node failure.
        for (Transaction txn : transactions.values()) {
            txn.processFailure(nodeId);
        }
    }
    
    public TransactionState getTransactionState(UUID transactionId) {
        Transaction txn = transactions.get(transactionId);
        if (txn == null) {
            throw new IllegalArgumentException("Transaction not found");
        }
        return txn.getState();
    }
    
    // Inner class to represent a Transaction.
    private static class Transaction {
        private final UUID transactionId;
        private final Set<Integer> involvedNodes;
        private final ConcurrentMap<Integer, Boolean> votes;
        private TransactionState state;
        private ScheduledFuture<?> timeoutTask;
        
        public Transaction(UUID transactionId, Set<Integer> involvedNodes) {
            this.transactionId = transactionId;
            this.involvedNodes = involvedNodes;
            this.votes = new ConcurrentHashMap<>();
            this.state = TransactionState.INITIATED;
        }
        
        public synchronized void setTimeoutTask(ScheduledFuture<?> task) {
            this.timeoutTask = task;
        }
        
        public synchronized TransactionState getState() {
            return state;
        }
        
        public synchronized void processVote(int nodeId, boolean vote) {
            // Ignore vote if transaction is no longer in INITIATED state.
            if (state != TransactionState.INITIATED) {
                return;
            }

            // If the node is not part of this transaction, ignore.
            if (!involvedNodes.contains(nodeId)) {
                return;
            }

            // Check for idempotency: if vote already recorded and the same, return.
            if (votes.containsKey(nodeId)) {
                if (votes.get(nodeId) == vote) {
                    return;
                }
            }
            votes.put(nodeId, vote);
            
            // If any node votes false, abort the transaction.
            if (!vote) {
                state = TransactionState.ABORTED;
                cancelTimeout();
                return;
            }
            
            // If all nodes have voted, determine outcome.
            if (votes.keySet().containsAll(involvedNodes)) {
                // All votes received, and since none are false, commit the transaction.
                state = TransactionState.COMMITTED;
                cancelTimeout();
            }
        }
        
        public synchronized void processFailure(int nodeId) {
            // If transaction already concluded, do nothing.
            if (state != TransactionState.INITIATED) {
                return;
            }
            // If a node involved fails before voting, abort the transaction.
            if (involvedNodes.contains(nodeId) && !votes.containsKey(nodeId)) {
                state = TransactionState.ABORTED;
                cancelTimeout();
            }
        }
        
        public synchronized void timeout() {
            // If transaction has not reached a terminal state upon timeout, abort it.
            if (state == TransactionState.INITIATED) {
                state = TransactionState.ABORTED;
            }
        }
        
        private synchronized void cancelTimeout() {
            if (timeoutTask != null) {
                timeoutTask.cancel(false);
            }
        }
    }
}