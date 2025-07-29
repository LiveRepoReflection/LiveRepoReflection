package distributed_tx;

import java.util.List;
import java.util.ArrayList;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

public class TransactionCoordinator {

    private List<DataNode> dataNodes;
    private Map<String, Transaction> transactions;
    private long transactionTimeout;

    private static AtomicInteger transactionCounter = new AtomicInteger(0);
    private static ConcurrentHashMap<String, TransactionStatus> globalTransactionLog = new ConcurrentHashMap<>();

    public TransactionCoordinator() {
        this.dataNodes = new ArrayList<>();
        this.transactions = new ConcurrentHashMap<>();
        this.transactionTimeout = 3000; // default timeout in milliseconds
    }

    public void registerDataNode(DataNode node) {
        dataNodes.add(node);
    }

    public void setTransactionTimeout(long timeoutMillis) {
        this.transactionTimeout = timeoutMillis;
    }

    public Transaction startTransaction() {
        String txId = "TX" + transactionCounter.incrementAndGet();
        Transaction tx = new Transaction(txId);
        transactions.put(txId, tx);
        globalTransactionLog.put(txId, TransactionStatus.IN_FLIGHT);
        return tx;
    }

    public void commitTransaction(String txId) {
        Transaction tx = transactions.get(txId);
        if (tx == null) {
            return;
        }
        long overallStart = System.currentTimeMillis();
        boolean prepareSuccess = true;

        // Prepare Phase
        for (DataNode node : dataNodes) {
            try {
                long prepareStart = System.currentTimeMillis();
                boolean prepared = node.prepareTransaction(txId);
                long prepareEnd = System.currentTimeMillis();
                if ((prepareEnd - prepareStart) > transactionTimeout) {
                    prepareSuccess = false;
                    break;
                }
                if (!prepared) {
                    prepareSuccess = false;
                    break;
                }
            } catch (Exception e) {
                prepareSuccess = false;
                break;
            }
            if ((System.currentTimeMillis() - overallStart) > transactionTimeout) {
                prepareSuccess = false;
                break;
            }
        }

        // Commit Phase
        if (prepareSuccess) {
            for (DataNode node : dataNodes) {
                try {
                    node.commitTransaction(txId);
                } catch (Exception e) {
                    prepareSuccess = false;
                    break;
                }
            }
        }

        if (prepareSuccess) {
            globalTransactionLog.put(txId, TransactionStatus.COMMITTED);
        } else {
            abortTransaction(txId);
        }
    }

    public void abortTransaction(String txId) {
        for (DataNode node : dataNodes) {
            try {
                node.abortTransaction(txId);
            } catch (Exception e) {
                // Ignoring errors during abort process
            }
        }
        globalTransactionLog.put(txId, TransactionStatus.ABORTED);
    }

    public TransactionStatus getTransactionStatus(String txId) {
        TransactionStatus status = globalTransactionLog.get(txId);
        return status;
    }

    public void simulateFailure() {
        // Mark all in-flight transactions as aborted
        for (Map.Entry<String, TransactionStatus> entry : globalTransactionLog.entrySet()) {
            if (entry.getValue() == TransactionStatus.IN_FLIGHT) {
                globalTransactionLog.put(entry.getKey(), TransactionStatus.ABORTED);
            }
        }
        // Clear local state to simulate coordinator failure. 
        transactions.clear();
        dataNodes.clear();
    }

    public static TransactionCoordinator recover() {
        // In a real-world scenario, recovery would involve reading persistent logs.
        // Here, we simply create a new instance. The globalTransactionLog acts as our persisted state.
        return new TransactionCoordinator();
    }
}