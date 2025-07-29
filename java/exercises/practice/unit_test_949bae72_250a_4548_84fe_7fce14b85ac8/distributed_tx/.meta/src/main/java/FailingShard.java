import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;

public class FailingShard implements Shard {
    private ConcurrentMap<String, TransactionStatus> statusMap = new ConcurrentHashMap<>();

    @Override
    public boolean prepare(String transactionId, String data) {
        statusMap.put(transactionId, TransactionStatus.ABORTED);
        return false;
    }

    @Override
    public void commit(String transactionId) {
        // No commit action for a failing shard.
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