import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

public class TransactionCoordinatorTest {

    private TransactionCoordinator coordinator;

    @BeforeEach
    public void setUp() {
        coordinator = new TransactionCoordinator();
    }

    // A FakeShard that always succeeds in prepare and records commit and rollback calls.
    private static class FakeShard implements Shard {
        private final List<String> log = Collections.synchronizedList(new ArrayList<>());

        @Override
        public boolean prepare(String transactionId) {
            log.add("prepare:" + transactionId);
            return true;
        }

        @Override
        public void commit(String transactionId) {
            log.add("commit:" + transactionId);
        }

        @Override
        public void rollback(String transactionId) {
            log.add("rollback:" + transactionId);
        }

        public List<String> getLog() {
            return log;
        }
    }

    // A FakeShard that fails prepare.
    private static class FakeShardFailPrepare implements Shard {
        private final List<String> log = Collections.synchronizedList(new ArrayList<>());

        @Override
        public boolean prepare(String transactionId) {
            log.add("prepare:false:" + transactionId);
            return false;
        }

        @Override
        public void commit(String transactionId) {
            log.add("commit:" + transactionId);
        }

        @Override
        public void rollback(String transactionId) {
            log.add("rollback:" + transactionId);
        }

        public List<String> getLog() {
            return log;
        }
    }

    // A FakeShard that simulates commit failures a fixed number of times before succeeding.
    private static class FakeShardCommitRetry implements Shard {
        private final List<String> log = Collections.synchronizedList(new ArrayList<>());
        private final AtomicInteger commitAttempts = new AtomicInteger(0);
        private final int failTimes;

        public FakeShardCommitRetry(int failTimes) {
            this.failTimes = failTimes;
        }

        @Override
        public boolean prepare(String transactionId) {
            log.add("prepare:" + transactionId);
            return true;
        }

        @Override
        public void commit(String transactionId) {
            int attempt = commitAttempts.incrementAndGet();
            if (attempt <= failTimes) {
                log.add("commit:fail:" + transactionId + ":" + attempt);
                throw new RuntimeException("Simulated commit failure on attempt " + attempt);
            }
            log.add("commit:success:" + transactionId + ":" + attempt);
        }

        @Override
        public void rollback(String transactionId) {
            log.add("rollback:" + transactionId);
        }

        public List<String> getLog() {
            return log;
        }
    }

    // A FakeShard that simulates rollback failures a fixed number of times before succeeding.
    private static class FakeShardRollbackRetry implements Shard {
        private final List<String> log = Collections.synchronizedList(new ArrayList<>());
        private final AtomicInteger rollbackAttempts = new AtomicInteger(0);
        private final int failTimes;

        public FakeShardRollbackRetry(int failTimes) {
            this.failTimes = failTimes;
        }

        @Override
        public boolean prepare(String transactionId) {
            log.add("prepare:false:" + transactionId);
            return false;
        }

        @Override
        public void commit(String transactionId) {
            log.add("commit:" + transactionId);
        }

        @Override
        public void rollback(String transactionId) {
            int attempt = rollbackAttempts.incrementAndGet();
            if (attempt <= failTimes) {
                log.add("rollback:fail:" + transactionId + ":" + attempt);
                throw new RuntimeException("Simulated rollback failure on attempt " + attempt);
            }
            log.add("rollback:success:" + transactionId + ":" + attempt);
        }

        public List<String> getLog() {
            return log;
        }
    }

    @Test
    public void testSuccessfulTransaction() {
        String txId = "tx1";
        FakeShard shard1 = new FakeShard();
        FakeShard shard2 = new FakeShard();

        coordinator.beginTransaction(txId);
        coordinator.enlistShard(txId, shard1);
        coordinator.enlistShard(txId, shard2);

        // Prepare should succeed.
        boolean prepareResult = coordinator.prepareTransaction(txId);
        assertTrue(prepareResult);

        // Commit the transaction.
        coordinator.commitTransaction(txId);

        // Verify that commit was called on both shards.
        List<String> log1 = shard1.getLog();
        List<String> log2 = shard2.getLog();

        assertTrue(log1.contains("prepare:" + txId));
        assertTrue(log2.contains("prepare:" + txId));
        assertTrue(log1.contains("commit:" + txId));
        assertTrue(log2.contains("commit:" + txId));
    }

    @Test
    public void testPrepareFailureTransaction() {
        String txId = "tx2";
        FakeShard shard1 = new FakeShard();
        FakeShardFailPrepare shardFail = new FakeShardFailPrepare();
        FakeShard shard2 = new FakeShard();

        coordinator.beginTransaction(txId);
        coordinator.enlistShard(txId, shard1);
        coordinator.enlistShard(txId, shardFail);
        coordinator.enlistShard(txId, shard2);

        // Prepare should fail because one shard returns false.
        boolean prepareResult = coordinator.prepareTransaction(txId);
        assertFalse(prepareResult);

        // Rollback the transaction.
        coordinator.rollbackTransaction(txId);

        List<String> log1 = shard1.getLog();
        List<String> logFail = shardFail.getLog();
        List<String> log2 = shard2.getLog();

        assertTrue(log1.contains("prepare:" + txId));
        assertTrue(logFail.contains("prepare:false:" + txId));
        assertTrue(log2.contains("prepare:" + txId));

        assertTrue(log1.contains("rollback:" + txId));
        assertTrue(logFail.contains("rollback:" + txId));
        assertTrue(log2.contains("rollback:" + txId));
    }

    @Test
    public void testCommitRetry() {
        String txId = "tx3";
        // This shard will fail twice on commit before succeeding.
        FakeShardCommitRetry shardRetry = new FakeShardCommitRetry(2);

        coordinator.beginTransaction(txId);
        coordinator.enlistShard(txId, shardRetry);

        // Prepare should succeed.
        boolean prepareResult = coordinator.prepareTransaction(txId);
        assertTrue(prepareResult);

        // Commit the transaction. The coordinator should retry commit until success.
        coordinator.commitTransaction(txId);

        List<String> log = shardRetry.getLog();
        long failCount = log.stream().filter(s -> s.startsWith("commit:fail:")).count();
        long successCount = log.stream().filter(s -> s.startsWith("commit:success:")).count();

        assertEquals(2, failCount);
        assertEquals(1, successCount);
    }

    @Test
    public void testRollbackRetry() {
        String txId = "tx4";
        // This shard will fail twice on rollback before succeeding.
        FakeShardRollbackRetry shardRollbackRetry = new FakeShardRollbackRetry(2);

        coordinator.beginTransaction(txId);
        coordinator.enlistShard(txId, shardRollbackRetry);

        // Prepare should fail.
        boolean prepareResult = coordinator.prepareTransaction(txId);
        assertFalse(prepareResult);

        // Rollback the transaction. The coordinator should retry rollback until success.
        coordinator.rollbackTransaction(txId);

        List<String> log = shardRollbackRetry.getLog();
        long failCount = log.stream().filter(s -> s.startsWith("rollback:fail:")).count();
        long successCount = log.stream().filter(s -> s.startsWith("rollback:success:")).count();

        assertEquals(2, failCount);
        assertEquals(1, successCount);
    }

    @Test
    public void testConcurrentTransactions() throws InterruptedException {
        int numThreads = 10;
        ExecutorService executor = Executors.newFixedThreadPool(numThreads);
        CountDownLatch latch = new CountDownLatch(numThreads);
        List<Exception> exceptions = Collections.synchronizedList(new ArrayList<>());

        for (int i = 0; i < numThreads; i++) {
            final String txId = "ctx" + i;
            executor.submit(() -> {
                try {
                    FakeShard shard = new FakeShard();
                    coordinator.beginTransaction(txId);
                    coordinator.enlistShard(txId, shard);
                    boolean prepareResult = coordinator.prepareTransaction(txId);
                    if (prepareResult) {
                        coordinator.commitTransaction(txId);
                    } else {
                        coordinator.rollbackTransaction(txId);
                    }
                    List<String> log = shard.getLog();
                    assertTrue(log.contains("prepare:" + txId));
                    if (prepareResult) {
                        assertTrue(log.contains("commit:" + txId));
                    } else {
                        assertTrue(log.contains("rollback:" + txId));
                    }
                } catch (Exception e) {
                    exceptions.add(e);
                } finally {
                    latch.countDown();
                }
            });
        }
        latch.await();
        executor.shutdownNow();
        assertTrue(exceptions.isEmpty(), "Exceptions occurred during concurrent transactions: " + exceptions);
    }
}