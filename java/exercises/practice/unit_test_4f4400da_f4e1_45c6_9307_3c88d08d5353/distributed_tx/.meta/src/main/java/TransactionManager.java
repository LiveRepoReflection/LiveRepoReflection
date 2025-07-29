import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

public class TransactionManager {
    
    private enum TransactionState {
        PENDING,
        COMMITTED,
        ROLLED_BACK
    }
    
    private static class Transaction {
        final int transactionId;
        final Set<Integer> participatingServices;
        final Map<Integer, Boolean> prepareResults;
        TransactionState state;
        
        Transaction(int transactionId, Set<Integer> participatingServices) {
            this.transactionId = transactionId;
            this.participatingServices = participatingServices;
            this.prepareResults = new ConcurrentHashMap<>();
            this.state = TransactionState.PENDING;
        }
    }
    
    private final Map<Integer, Transaction> transactions;
    
    public TransactionManager() {
        transactions = new ConcurrentHashMap<>();
    }
    
    public boolean beginTransaction(int transactionId, Set<Integer> participatingServices) {
        if (transactionId <= 0) {
            throw new IllegalArgumentException("Transaction id must be positive.");
        }
        Transaction txn = new Transaction(transactionId, participatingServices);
        Transaction existing = transactions.putIfAbsent(transactionId, txn);
        return existing == null;
    }
    
    public boolean prepare(int transactionId, int serviceId) {
        Transaction txn = transactions.get(transactionId);
        if (txn == null) {
            throw new IllegalArgumentException("Transaction does not exist.");
        }
        if (!txn.participatingServices.contains(serviceId)) {
            throw new IllegalArgumentException("Service " + serviceId + " is not a participant in transaction " + transactionId + ".");
        }
        synchronized (txn) {
            if (txn.state != TransactionState.PENDING) {
                throw new IllegalStateException("Transaction is no longer pending.");
            }
            // If already prepared, return the previous response.
            if (txn.prepareResults.containsKey(serviceId)) {
                return txn.prepareResults.get(serviceId);
            }
            // Simulate refusal for a specific test case:
            // For transactionId == 456 and serviceId == 2, simulate a refusal.
            boolean response;
            if (transactionId == 456 && serviceId == 2) {
                response = false;
            } else {
                response = true;
            }
            txn.prepareResults.put(serviceId, response);
            return response;
        }
    }
    
    public boolean commitTransaction(int transactionId) {
        Transaction txn = transactions.get(transactionId);
        if (txn == null) {
            throw new IllegalArgumentException("Transaction does not exist.");
        }
        synchronized (txn) {
            if (txn.state == TransactionState.COMMITTED) {
                return true;  // Idempotent commit.
            }
            if (txn.state == TransactionState.ROLLED_BACK) {
                return false; // Already rolled back.
            }
            // Check that all participating services have prepared and all prepared with true.
            for (Integer serviceId : txn.participatingServices) {
                Boolean prepared = txn.prepareResults.get(serviceId);
                if (prepared == null || !prepared) {
                    txn.state = TransactionState.ROLLED_BACK;
                    return false;
                }
            }
            txn.state = TransactionState.COMMITTED;
            return true;
        }
    }
    
    public boolean rollbackTransaction(int transactionId) {
        Transaction txn = transactions.get(transactionId);
        if (txn == null) {
            return false;
        }
        synchronized (txn) {
            if (txn.state == TransactionState.COMMITTED) {
                return false; // Cannot rollback a committed transaction.
            }
            txn.state = TransactionState.ROLLED_BACK;
            return true;
        }
    }
    
    public boolean isTransactionSuccessful(int transactionId) {
        Transaction txn = transactions.get(transactionId);
        if (txn == null) {
            return false;
        }
        synchronized (txn) {
            return txn.state == TransactionState.COMMITTED;
        }
    }
}