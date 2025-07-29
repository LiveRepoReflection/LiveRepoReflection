package distributed_tx;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Assertions;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.List;
import java.util.ArrayList;

public class DistributedTxTest {

    @Test
    public void testSuccessfulCommit() throws Exception {
        // Set up coordinator with dummy nodes that always succeed
        TransactionCoordinator coordinator = new TransactionCoordinator();
        coordinator.registerDataNode(new AlwaysCommitNode("Node1"));
        coordinator.registerDataNode(new AlwaysCommitNode("Node2"));
        coordinator.registerDataNode(new AlwaysCommitNode("Node3"));

        Transaction tx = coordinator.startTransaction();
        // Simulate operations for the transaction
        tx.addOperation("update record 1");
        tx.addOperation("update record 2");

        coordinator.commitTransaction(tx.getId());
        TransactionStatus status = coordinator.getTransactionStatus(tx.getId());

        Assertions.assertEquals(TransactionStatus.COMMITTED, status, "Transaction should be committed successfully.");
    }

    @Test
    public void testTimeoutAbort() throws Exception {
        // Set up coordinator with one node that delays beyond the timeout threshold.
        TransactionCoordinator coordinator = new TransactionCoordinator();
        coordinator.registerDataNode(new AlwaysCommitNode("Node1"));
        coordinator.registerDataNode(new DelayedCommitNode("DelayedNode", 5000)); // 5000ms delay

        Transaction tx = coordinator.startTransaction();
        tx.addOperation("update record A");

        // Set a short timeout (e.g., 1000ms) for the transaction
        coordinator.setTransactionTimeout(1000);

        coordinator.commitTransaction(tx.getId());
        TransactionStatus status = coordinator.getTransactionStatus(tx.getId());

        Assertions.assertEquals(TransactionStatus.ABORTED, status, "Transaction should be aborted due to timeout.");
    }

    @Test
    public void testConcurrentTransactions() throws Exception {
        TransactionCoordinator coordinator = new TransactionCoordinator();
        coordinator.registerDataNode(new AlwaysCommitNode("Node1"));
        coordinator.registerDataNode(new AlwaysCommitNode("Node2"));

        int totalTransactions = 100;
        CountDownLatch latch = new CountDownLatch(totalTransactions);
        AtomicInteger committedCount = new AtomicInteger(0);
        List<Thread> threads = new ArrayList<>();

        for (int i = 0; i < totalTransactions; i++) {
            Thread t = new Thread(() -> {
                try {
                    Transaction tx = coordinator.startTransaction();
                    tx.addOperation("update record X");
                    coordinator.commitTransaction(tx.getId());
                    if (coordinator.getTransactionStatus(tx.getId()) == TransactionStatus.COMMITTED) {
                        committedCount.incrementAndGet();
                    }
                } catch (Exception e) {
                    // Exception handling for individual transaction failures
                } finally {
                    latch.countDown();
                }
            });
            threads.add(t);
            t.start();
        }

        latch.await(10, TimeUnit.SECONDS);
        Assertions.assertEquals(totalTransactions, committedCount.get(), "All concurrent transactions should commit successfully.");
    }

    @Test
    public void testRecoveryAfterFailure() throws Exception {
        // Set up coordinator and perform transactions
        TransactionCoordinator coordinator = new TransactionCoordinator();
        coordinator.registerDataNode(new AlwaysCommitNode("Node1"));
        coordinator.registerDataNode(new AlwaysCommitNode("Node2"));

        Transaction tx1 = coordinator.startTransaction();
        tx1.addOperation("insert record");
        coordinator.commitTransaction(tx1.getId());

        Transaction tx2 = coordinator.startTransaction();
        tx2.addOperation("delete record");
        // Do not commit tx2 to simulate an in-flight transaction during coordinator failure
        coordinator.simulateFailure();

        // Simulate recovery process by creating a new coordinator instance that recovers state from logs.
        TransactionCoordinator recoveredCoordinator = TransactionCoordinator.recover();
        TransactionStatus status1 = recoveredCoordinator.getTransactionStatus(tx1.getId());
        TransactionStatus status2 = recoveredCoordinator.getTransactionStatus(tx2.getId());

        Assertions.assertEquals(TransactionStatus.COMMITTED, status1, "Recovered transaction tx1 should be committed.");
        Assertions.assertEquals(TransactionStatus.ABORTED, status2, "Recovered transaction tx2 should be aborted after failure.");
    }

    // Dummy implementations for DataNode to simulate behavior during testing.
    static class AlwaysCommitNode implements DataNode {
        private final String nodeName;

        AlwaysCommitNode(String nodeName) {
            this.nodeName = nodeName;
        }

        @Override
        public boolean prepareTransaction(String txId) {
            return true;
        }

        @Override
        public void commitTransaction(String txId) {
            // Commit operation always succeeds.
        }

        @Override
        public void abortTransaction(String txId) {
            // Abort operation (no action needed).
        }

        @Override
        public String getNodeName() {
            return nodeName;
        }
    }

    static class DelayedCommitNode implements DataNode {
        private final String nodeName;
        private final long delayMillis;

        DelayedCommitNode(String nodeName, long delayMillis) {
            this.nodeName = nodeName;
            this.delayMillis = delayMillis;
        }

        @Override
        public boolean prepareTransaction(String txId) throws InterruptedException {
            Thread.sleep(delayMillis);
            return true;
        }

        @Override
        public void commitTransaction(String txId) throws InterruptedException {
            Thread.sleep(delayMillis);
        }

        @Override
        public void abortTransaction(String txId) {
            // Abort operation (no action needed).
        }

        @Override
        public String getNodeName() {
            return nodeName;
        }
    }
}