import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;

public class SlowShard implements Shard {
    private ConcurrentMap<String, TransactionStatus> statusMap = new ConcurrentHashMap<>();
    private int delayMillis;

    public SlowShard(int delayMillis) {
        this.delayMillis = delayMillis;
    }

    @Override
    public boolean prepare(String transactionId, String data) {
        try {
            Thread.sleep(delayMillis);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
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