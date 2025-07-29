import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;

public class TransactionCoordinatorTest {

    enum TransactionStatus {
        NONE, PREPARED, COMMITTED, ABORTED
    }

    interface Shard {
        boolean prepare(String transactionId, String data);
        void commit(String transactionId);
        void abort(String transactionId);
        TransactionStatus getStatus(String transactionId);
    }

    class Coordinator {
        private List<Shard> shards;
        private int timeoutMillis;
        private Map<String, TransactionStatus> transactionLog = new ConcurrentHashMap<>();

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

    class SuccessfulShard implements Shard {
        private Map<String, TransactionStatus> statusMap = new ConcurrentHashMap<>();

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

    class FailingShard implements Shard {
        private Map<String, TransactionStatus> statusMap = new ConcurrentHashMap<>();

        @Override
        public boolean prepare(String transactionId, String data) {
            statusMap.put(transactionId, TransactionStatus.ABORTED);
            return false;
        }

        @Override
        public void commit(String transactionId) {
            // No commit action
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

    class SlowShard implements Shard {
        private Map<String, TransactionStatus> statusMap = new ConcurrentHashMap<>();
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

    @Test
    public void testSuccessfulTransaction() {
        String txId = "tx_success";
        String data = "update profile";
        List<Shard> shards = new ArrayList<>();
        shards.add(new SuccessfulShard());
        shards.add(new SuccessfulShard());
        shards.add(new SuccessfulShard());

        Coordinator coordinator = new Coordinator(shards, 500);
        boolean result = coordinator.executeTransaction(txId, data);

        assertTrue(result, "Transaction should succeed");
        assertEquals(TransactionStatus.COMMITTED, coordinator.getTransactionStatus(txId), "Transaction status should be COMMITTED");
        for (Shard shard : shards) {
            assertEquals(TransactionStatus.COMMITTED, shard.getStatus(txId), "Each shard should have COMMITTED status");
        }
    }

    @Test
    public void testFailedTransactionDueToPrepare() {
        String txId = "tx_fail";
        String data = "update profile";
        List<Shard> shards = new ArrayList<>();
        shards.add(new SuccessfulShard());
        shards.add(new FailingShard());
        shards.add(new SuccessfulShard());

        Coordinator coordinator = new Coordinator(shards, 500);
        boolean result = coordinator.executeTransaction(txId, data);

        assertFalse(result, "Transaction should fail");
        assertEquals(TransactionStatus.ABORTED, coordinator.getTransactionStatus(txId), "Transaction status should be ABORTED");
        for (Shard shard : shards) {
            assertEquals(TransactionStatus.ABORTED, shard.getStatus(txId), "Each shard should have ABORTED status");
        }
    }

    @Test
    public void testTransactionTimeout() {
        String txId = "tx_timeout";
        String data = "update profile";
        List<Shard> shards = new ArrayList<>();
        shards.add(new SuccessfulShard());
        shards.add(new SlowShard(600));
        shards.add(new SuccessfulShard());

        Coordinator coordinator = new Coordinator(shards, 500);
        boolean result = coordinator.executeTransaction(txId, data);

        assertFalse(result, "Transaction should timeout and fail");
        assertEquals(TransactionStatus.ABORTED, coordinator.getTransactionStatus(txId), "Transaction status should be ABORTED due to timeout");
        for (Shard shard : shards) {
            assertEquals(TransactionStatus.ABORTED, shard.getStatus(txId), "Each shard should have ABORTED status because of timeout");
        }
    }

    @Test
    public void testConcurrentTransactions() throws InterruptedException, ExecutionException {
        int numTransactions = 100;
        List<Shard> shards = new ArrayList<>();
        shards.add(new SuccessfulShard());
        shards.add(new SuccessfulShard());
        shards.add(new SuccessfulShard());

        Coordinator coordinator = new Coordinator(shards, 1000);
        ExecutorService executor = Executors.newFixedThreadPool(10);
        List<Future<Boolean>> futures = new ArrayList<>();

        for (int i = 0; i < numTransactions; i++) {
            final String txId = "tx_" + i;
            final String data = "data_" + i;
            Future<Boolean> future = executor.submit(() -> coordinator.executeTransaction(txId, data));
            futures.add(future);
        }

        int committedCount = 0;
        for (int i = 0; i < numTransactions; i++) {
            boolean result = futures.get(i).get();
            TransactionStatus status = coordinator.getTransactionStatus("tx_" + i);
            if (result && status == TransactionStatus.COMMITTED) {
                committedCount++;
            }
        }
        assertEquals(numTransactions, committedCount, "All concurrent transactions should be COMMITTED");
        executor.shutdown();
    }
}