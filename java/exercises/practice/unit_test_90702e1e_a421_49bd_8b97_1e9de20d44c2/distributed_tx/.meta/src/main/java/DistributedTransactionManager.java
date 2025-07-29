package distributed_tx;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

public class DistributedTransactionManager {
    private final ServiceRegistry serviceRegistry;
    private final ConcurrentHashMap<String, Transaction> transactions = new ConcurrentHashMap<>();

    public DistributedTransactionManager(ServiceRegistry serviceRegistry) {
        this.serviceRegistry = serviceRegistry;
    }

    public String begin() {
        String txId = UUID.randomUUID().toString();
        Transaction tx = new Transaction(txId);
        transactions.put(txId, tx);
        TransactionLog.log(txId, "Transaction begun");
        return txId;
    }

    public void enlist(String txId, String service, String operation, String data) {
        Transaction tx = transactions.get(txId);
        if (tx == null) {
            throw new IllegalArgumentException("Transaction not found: " + txId);
        }
        tx.enlist(new Participant(service, operation, data));
        TransactionLog.log(txId, "Enlisted Participant: " + service + ", " + operation);
    }

    public boolean commit(String txId) {
        Transaction tx = transactions.get(txId);
        if (tx == null) {
            throw new IllegalArgumentException("Transaction not found: " + txId);
        }
        if (tx.getStatus() == Transaction.Status.COMMITTED) {
            return true;
        }
        if (tx.getStatus() == Transaction.Status.ROLLEDBACK) {
            return false;
        }
        tx.setStatus(Transaction.Status.COMMITTING);
        TransactionLog.log(txId, "Committing transaction");
        boolean success = true;
        for (Participant p : tx.getParticipants()) {
            if (!p.isExecuted()) {
                boolean executed = false;
                int retries = 3;
                while (retries > 0 && !executed) {
                    executed = serviceRegistry.execute(p.getService(), p.getOperation(), p.getData());
                    retries--;
                }
                if (!executed) {
                    success = false;
                    break;
                } else {
                    p.markExecuted();
                }
            }
        }
        if (success) {
            tx.setStatus(Transaction.Status.COMMITTED);
            TransactionLog.log(txId, "Transaction committed");
        } else {
            rollbackInternal(tx);
            tx.setStatus(Transaction.Status.ROLLEDBACK);
            TransactionLog.log(txId, "Transaction rolled back due to commit failure");
        }
        return success;
    }

    public boolean rollback(String txId) {
        Transaction tx = transactions.get(txId);
        if (tx == null) {
            throw new IllegalArgumentException("Transaction not found: " + txId);
        }
        if (tx.getStatus() == Transaction.Status.ROLLEDBACK) {
            return true;
        }
        if (tx.getStatus() == Transaction.Status.COMMITTED) {
            return false;
        }
        tx.setStatus(Transaction.Status.ROLLING_BACK);
        TransactionLog.log(txId, "Rolling back transaction");
        rollbackInternal(tx);
        tx.setStatus(Transaction.Status.ROLLEDBACK);
        TransactionLog.log(txId, "Transaction rolled back");
        return true;
    }

    private void rollbackInternal(Transaction tx) {
        List<Participant> list = tx.getParticipants();
        Collections.reverse(list);
        for (Participant p : list) {
            if (!p.isCompensated()) {
                serviceRegistry.compensate(p.getService(), p.getOperation(), p.getData());
                p.markCompensated();
            }
        }
    }
}

class Transaction {
    public enum Status {
        ONGOING,
        COMMITTING,
        COMMITTED,
        ROLLING_BACK,
        ROLLEDBACK
    }

    private final String txId;
    private final List<Participant> participants;
    private volatile Status status;

    public Transaction(String txId) {
        this.txId = txId;
        this.participants = new ArrayList<>();
        this.status = Status.ONGOING;
    }

    public String getTxId() {
        return txId;
    }

    public List<Participant> getParticipants() {
        return participants;
    }

    public synchronized void enlist(Participant p) {
        if (this.status != Status.ONGOING) {
            throw new IllegalStateException("Cannot enlist participant after commit/rollback started");
        }
        this.participants.add(p);
    }

    public Status getStatus() {
        return status;
    }

    public void setStatus(Status status) {
        this.status = status;
    }
}

class Participant {
    private final String service;
    private final String operation;
    private final String data;
    private boolean executed;
    private boolean compensated;

    public Participant(String service, String operation, String data) {
        this.service = service;
        this.operation = operation;
        this.data = data;
        this.executed = false;
        this.compensated = false;
    }

    public String getService() {
        return service;
    }

    public String getOperation() {
        return operation;
    }

    public String getData() {
        return data;
    }

    public synchronized boolean isExecuted() {
        return executed;
    }

    public synchronized void markExecuted() {
        executed = true;
    }

    public synchronized boolean isCompensated() {
        return compensated;
    }

    public synchronized void markCompensated() {
        compensated = true;
    }
}