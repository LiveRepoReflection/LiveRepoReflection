import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

public class TransactionManager {

    private final Map<String, Transaction> transactions;
    private final TransactionLog transactionLog;

    public TransactionManager() {
        this.transactions = new ConcurrentHashMap<>();
        this.transactionLog = new TransactionLog();
    }

    public String begin() {
        String txid = UUID.randomUUID().toString();
        Transaction tx = new Transaction(txid);
        transactions.put(txid, tx);
        transactionLog.addTransaction(txid, tx.getStatus());
        return txid;
    }

    public void prepare(String txid, String service, String operationDetails) {
        Transaction tx = transactions.get(txid);
        if (tx == null) {
            return;
        }
        // Call ServiceProxy to simulate prepare phase.
        String result = ServiceProxy.prepare(service, operationDetails);
        tx.addServiceStatus(service, result);
        // Idempotently update if already failed.
        if (!"prepared".equals(result)) {
            tx.setOverallStatus("aborted");
            transactionLog.updateTransactionStatus(txid, "aborted");
        }
    }

    public void commit(String txid) {
        Transaction tx = transactions.get(txid);
        if (tx == null) {
            return;
        }
        // If already committed or aborted idempotently return.
        if ("committed".equals(tx.getStatus()) || "aborted".equals(tx.getStatus())) {
            return;
        }
        // Check if any service has failed.
        boolean allPrepared = tx.allServicesPrepared();
        if (!allPrepared) {
            // Abort if any service is not prepared.
            abort(txid);
            return;
        }
        // Issue commit for all services.
        for (String service : tx.getServices()) {
            ServiceProxy.commit(service, txid);
        }
        tx.setOverallStatus("committed");
        transactionLog.updateTransactionStatus(txid, "committed");
    }

    public void abort(String txid) {
        Transaction tx = transactions.get(txid);
        if (tx == null) {
            return;
        }
        // If already aborted or committed, do nothing.
        if ("aborted".equals(tx.getStatus())) {
            return;
        }
        // Issue abort for all services that have been prepared.
        for (String service : tx.getServices()) {
            ServiceProxy.abort(service, txid);
        }
        tx.setOverallStatus("aborted");
        transactionLog.updateTransactionStatus(txid, "aborted");
    }

    public String getTransactionStatus(String txid) {
        Transaction tx = transactions.get(txid);
        if (tx == null) {
            return "unknown";
        }
        return tx.getStatus();
    }
}