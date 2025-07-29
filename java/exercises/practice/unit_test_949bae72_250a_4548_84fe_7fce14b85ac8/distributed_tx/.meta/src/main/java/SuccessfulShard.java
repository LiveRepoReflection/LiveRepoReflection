import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;

public class SuccessfulShard implements Shard {
    private ConcurrentMap<String, TransactionStatus> statusMap = new ConcurrentHashMap<>();

    @Override
    public boolean prepare(String transactionId, String data) {
        statusMap.put(transactionId, TransactionStatus.PREPARED);
        return true;
    }

    @Override
    public void commit(String transactionId) {
        statusMap.put(transactionId, TransactionStatus.COMMITTED);
    }

    @Override
    public void abort(String transactionId) {
        statusMap.put(transactionId, TransactionStatus.ABORTED);
    }

    @Override
    public TransactionStatus getStatus(String transactionId) {
        return statusMap.getOrDefault(transactionId, TransactionStatus.NONE);
    }
}