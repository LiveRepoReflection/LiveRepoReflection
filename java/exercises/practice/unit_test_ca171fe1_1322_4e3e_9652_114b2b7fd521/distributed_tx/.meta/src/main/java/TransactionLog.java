import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class TransactionLog {

    private final Map<String, String> log;

    public TransactionLog() {
        log = new ConcurrentHashMap<>();
    }

    public void addTransaction(String txid, String status) {
        log.put(txid, status);
    }

    public void updateTransactionStatus(String txid, String status) {
        log.put(txid, status);
    }

    public String getTransactionStatus(String txid) {
        return log.getOrDefault(txid, "unknown");
    }
}