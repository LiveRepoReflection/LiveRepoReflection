package distributed_tx;

import java.util.*;
import java.util.concurrent.*;

public class TransactionManager {

    private final Map<String, Service> services;
    private final Map<String, Transaction> transactions;
    private final ExecutorService executor;
    private final long prepareTimeoutMillis;

    public TransactionManager() {
        this.services = new ConcurrentHashMap<>();
        this.transactions = new ConcurrentHashMap<>();
        this.executor = Executors.newCachedThreadPool();
        this.prepareTimeoutMillis = 2000; // default timeout of 2000ms for prepare phase
    }

    public String beginTransaction() {
        String txId = UUID.randomUUID().toString();
        Transaction tx = new Transaction(txId);
        transactions.put(txId, tx);
        return txId;
    }

    public void registerService(Service service) {
        services.put(service.getName(), service);
    }

    public void addOperation(String transactionId, Operation op) {
        Transaction tx = transactions.get(transactionId);
        if (tx == null) {
            throw new IllegalArgumentException("Transaction not found: " + transactionId);
        }
        if (!services.containsKey(op.getServiceName())) {
            throw new IllegalArgumentException("Service not registered: " + op.getServiceName());
        }
        tx.addOperation(op);
    }

    public void executeTransaction(String transactionId) {
        Transaction tx = transactions.get(transactionId);
        if (tx == null) {
            throw new IllegalArgumentException("Transaction not found: " + transactionId);
        }
        synchronized (tx) {
            if (tx.getStatus() != TransactionStatus.PENDING) {
                // Transaction already executed; idempotent execution.
                return;
            }
            List<Operation> ops = tx.getOperations();
            Set<String> participantNames = new HashSet<>();
            for (Operation op : ops) {
                participantNames.add(op.getServiceName());
            }
            List<Service> participants = new ArrayList<>();
            for (String name : participantNames) {
                Service service = services.get(name);
                if (service != null) {
                    participants.add(service);
                }
            }

            boolean prepareSuccess = true;
            // Phase 1: Prepare
            for (Operation op : ops) {
                Service service = services.get(op.getServiceName());
                try {
                    Future<Boolean> future = executor.submit(() -> service.prepare(transactionId, op));
                    boolean result = future.get(prepareTimeoutMillis, TimeUnit.MILLISECONDS);
                    if (!result) {
                        prepareSuccess = false;
                        break;
                    }
                } catch (Exception e) {
                    prepareSuccess = false;
                    break;
                }
            }

            // Phase 2: Commit or Rollback based on prepare outcome.
            if (prepareSuccess) {
                for (Service service : participants) {
                    try {
                        service.commit(transactionId);
                    } catch (Exception e) {
                        // In a full system, additional recovery logic would be applied.
                    }
                }
                tx.setStatus(TransactionStatus.COMMITTED);
            } else {
                for (Service service : participants) {
                    try {
                        service.rollback(transactionId);
                    } catch (Exception e) {
                        // In a full system, additional recovery/retry logic would be applied.
                    }
                }
                tx.setStatus(TransactionStatus.ROLLEDBACK);
            }
        }
    }

    public TransactionStatus getTransactionStatus(String transactionId) {
        Transaction tx = transactions.get(transactionId);
        if (tx == null) {
            throw new IllegalArgumentException("Transaction not found: " + transactionId);
        }
        return tx.getStatus();
    }

    // Internal transaction representation.
    private static class Transaction {
        private final String transactionId;
        private final List<Operation> operations;
        private TransactionStatus status;

        public Transaction(String transactionId) {
            this.transactionId = transactionId;
            this.operations = new ArrayList<>();
            this.status = TransactionStatus.PENDING;
        }

        public void addOperation(Operation op) {
            operations.add(op);
        }

        public List<Operation> getOperations() {
            return operations;
        }

        public TransactionStatus getStatus() {
            return status;
        }

        public void setStatus(TransactionStatus status) {
            this.status = status;
        }
    }
}