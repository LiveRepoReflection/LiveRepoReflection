package distributed_tx;

import java.util.*;
import java.util.concurrent.*;

public class TransactionManager {

    private final Map<UUID, Transaction> transactions;
    private final ExecutorService executor;
    private final long prepareTimeoutMs = 50;

    public TransactionManager() {
        transactions = new ConcurrentHashMap<>();
        executor = Executors.newCachedThreadPool();
    }

    public UUID begin(List<Microservice> services) {
        UUID txnId = UUID.randomUUID();
        Transaction txn = new Transaction(txnId, services);
        transactions.put(txnId, txn);
        txn.state = TransactionState.INIT;
        return txnId;
    }

    public boolean commit(UUID transactionId) {
        Transaction txn = transactions.get(transactionId);
        if (txn == null) {
            return false;
        }
        txn.state = TransactionState.PREPARING;

        List<Future<String>> futures = new ArrayList<>();
        for (Microservice ms : txn.services) {
            Future<String> future = executor.submit(() -> ms.prepare(transactionId));
            futures.add(future);
        }

        boolean allPrepared = true;
        for (Future<String> future : futures) {
            try {
                String result = future.get(prepareTimeoutMs, TimeUnit.MILLISECONDS);
                if (!"prepared".equalsIgnoreCase(result)) {
                    allPrepared = false;
                    break;
                }
            } catch (Exception e) {
                allPrepared = false;
                break;
            }
        }

        if (!allPrepared) {
            txn.state = TransactionState.ROLLING_BACK;
            for (Microservice ms : txn.services) {
                try {
                    ms.rollback(transactionId);
                } catch (Exception e) {
                    // Ignored as microservices are assumed idempotent for rollback.
                }
            }
            txn.state = TransactionState.ROLLEDBACK;
            return false;
        } else {
            txn.state = TransactionState.COMMITTING;
            for (Microservice ms : txn.services) {
                try {
                    ms.commit(transactionId);
                } catch (Exception e) {
                    // Ignored as microservices are assumed idempotent for commit.
                }
            }
            txn.state = TransactionState.COMMITTED;
            return true;
        }
    }

    public boolean rollback(UUID transactionId) {
        Transaction txn = transactions.get(transactionId);
        if (txn == null) {
            return false;
        }
        txn.state = TransactionState.ROLLING_BACK;
        for (Microservice ms : txn.services) {
            try {
                ms.rollback(transactionId);
            } catch (Exception e) {
                // Ignored, as microservices are idempotent.
            }
        }
        txn.state = TransactionState.ROLLEDBACK;
        return true;
    }

    public void recover() {
        // In a real-world scenario, the transaction log would be read from durable storage.
        // Here we iterate through in-memory transactions and rollback those that are incomplete.
        for (Transaction txn : transactions.values()) {
            if (txn.state != TransactionState.COMMITTED && txn.state != TransactionState.ROLLEDBACK) {
                txn.state = TransactionState.ROLLING_BACK;
                for (Microservice ms : txn.services) {
                    try {
                        ms.rollback(txn.transactionId);
                    } catch (Exception e) {
                        // Ignored during recovery.
                    }
                }
                txn.state = TransactionState.ROLLEDBACK;
            }
        }
    }

    private static class Transaction {
        private final UUID transactionId;
        private final List<Microservice> services;
        private TransactionState state;

        public Transaction(UUID transactionId, List<Microservice> services) {
            this.transactionId = transactionId;
            this.services = services;
            this.state = TransactionState.INIT;
        }
    }

    private enum TransactionState {
        INIT, PREPARING, COMMITTING, COMMITTED, ROLLING_BACK, ROLLEDBACK
    }
}