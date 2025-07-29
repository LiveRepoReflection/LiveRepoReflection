import java.util.*;
import java.util.concurrent.*;

public class Coordinator {
    private List<Shard> shards;
    private int timeoutMillis;
    private ConcurrentMap<String, TransactionStatus> transactionLog = new ConcurrentHashMap<>();

    public Coordinator(List<Shard> shards, int timeoutMillis) {
        this.shards = shards;
        this.timeoutMillis = timeoutMillis;
    }

    public boolean executeTransaction(String transactionId, String data) {
        transactionLog.put(transactionId, TransactionStatus.NONE);
        ExecutorService executor = Executors.newFixedThreadPool(shards.size());
        List<Future<Boolean>> futures = new ArrayList<>();

        for (Shard shard : shards) {
            Future<Boolean> future = executor.submit(() -> shard.prepare(transactionId, data));
            futures.add(future);
        }

        boolean allPrepared = true;
        for (Future<Boolean> future : futures) {
            try {
                boolean result = future.get(timeoutMillis, TimeUnit.MILLISECONDS);
                if (!result) {
                    allPrepared = false;
                }
            } catch (Exception e) {
                allPrepared = false;
            }
        }

        if (allPrepared) {
            transactionLog.put(transactionId, TransactionStatus.PREPARED);
            for (Shard shard : shards) {
                shard.commit(transactionId);
            }
            transactionLog.put(transactionId, TransactionStatus.COMMITTED);
            executor.shutdown();
            return true;
        } else {
            transactionLog.put(transactionId, TransactionStatus.ABORTED);
            for (Shard shard : shards) {
                shard.abort(transactionId);
            }
            executor.shutdown();
            return false;
        }
    }

    public TransactionStatus getTransactionStatus(String transactionId) {
        return transactionLog.getOrDefault(transactionId, TransactionStatus.NONE);
    }
}