import java.util.ArrayList;
import java.util.List;

public class TransactionCoordinator {
    private long timeout = 2000; // default timeout in milliseconds
    private final List<Transaction> transactionLog = new ArrayList<>();

    public void setTimeout(long timeout) {
        this.timeout = timeout;
    }

    public CoordinatorResult processTransaction(Transaction tx) {
        boolean allPrepared = true;
        for (MicroserviceOperation op : tx.getOperations()) {
            try {
                if (!op.prepare(timeout)) {
                    allPrepared = false;
                    break;
                }
            } catch (InterruptedException e) {
                allPrepared = false;
                break;
            }
        }
        CoordinatorResult result;
        if (allPrepared) {
            for (MicroserviceOperation op : tx.getOperations()) {
                op.commit();
            }
            result = CoordinatorResult.COMMIT;
        } else {
            for (MicroserviceOperation op : tx.getOperations()) {
                op.rollback();
            }
            result = CoordinatorResult.ROLLBACK;
        }
        // Log the transaction for recovery purposes
        transactionLog.add(tx);
        return result;
    }

    public void reProcessTransaction(Transaction tx) {
        // Reapply commit to ensure idempotency and consistency
        for (MicroserviceOperation op : tx.getOperations()) {
            op.commit();
        }
    }

    public void saveTransactionLog(Transaction tx) {
        transactionLog.add(tx);
    }

    public void loadTransactionLog() {
        // In this simulation, transactionLog remains in-memory.
        // In a real-world scenario, logs would be loaded from persistent storage.
    }

    public CoordinatorResult recoverPendingTransactions() {
        CoordinatorResult finalResult = CoordinatorResult.COMMIT;
        for (Transaction tx : transactionLog) {
            CoordinatorResult res = processTransaction(tx);
            if (res == CoordinatorResult.ROLLBACK) {
                finalResult = CoordinatorResult.ROLLBACK;
            }
        }
        return finalResult;
    }
}