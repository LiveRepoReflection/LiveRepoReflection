package distributed_tx;

import java.util.*;
import java.util.concurrent.*;

public class DistributedTransactionManager {
    private final List<TransactionOperation> operations = new ArrayList<>();
    private final long phaseTimeoutMillis;
    private final String transactionId;
    private final Map<String, String> transactionLog = new ConcurrentHashMap<>();

    public DistributedTransactionManager(long phaseTimeoutMillis) {
        this.phaseTimeoutMillis = phaseTimeoutMillis;
        this.transactionId = UUID.randomUUID().toString();
        transactionLog.put(transactionId, "INIT");
    }

    public void addOperation(TransactionOperation op) {
        operations.add(op);
    }

    public boolean executeTransaction() {
        transactionLog.put(transactionId, "PREPARING");
        ExecutorService executor = Executors.newFixedThreadPool(operations.size());
        try {
            List<Future<Boolean>> prepareResults = new ArrayList<>();
            for (TransactionOperation op : operations) {
                Future<Boolean> future = executor.submit(() -> {
                    op.execute();
                    return op.prepare();
                });
                prepareResults.add(future);
            }
            for (Future<Boolean> future : prepareResults) {
                try {
                    boolean prepared = future.get(phaseTimeoutMillis, TimeUnit.MILLISECONDS);
                    if (!prepared) {
                        rollbackAll();
                        return false;
                    }
                } catch (TimeoutException | InterruptedException | ExecutionException e) {
                    rollbackAll();
                    return false;
                }
            }
            transactionLog.put(transactionId, "COMMITTING");
            for (TransactionOperation op : operations) {
                op.commit();
            }
            transactionLog.put(transactionId, "COMPLETED");
            return true;
        } finally {
            executor.shutdownNow();
        }
    }

    private void rollbackAll() {
        transactionLog.put(transactionId, "ROLLING_BACK");
        for (TransactionOperation op : operations) {
            op.rollback();
        }
        transactionLog.put(transactionId, "COMPLETED");
    }

    public String getTransactionState() {
        return transactionLog.get(transactionId);
    }
}