import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;
import java.util.concurrent.Executors;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.List;
import java.util.ArrayList;
import static org.junit.jupiter.api.Assertions.*;

public class TransactionCoordinatorTest {

    // Mock implementation of DataNode for testing
    private static class MockDataNode implements DataNode {
        private final String name;
        private final boolean prepareSuccess;
        private final long prepareDelayMillis;
        private final boolean commitSuccess;
        private final long commitDelayMillis;
        private final boolean abortSuccess;
        private final long abortDelayMillis;
        private boolean committedOrAborted = false;
        private final boolean available;

        public MockDataNode(String name, boolean available, boolean prepareSuccess, long prepareDelayMillis,
                            boolean commitSuccess, long commitDelayMillis,
                            boolean abortSuccess, long abortDelayMillis) {
            this.name = name;
            this.available = available;
            this.prepareSuccess = prepareSuccess;
            this.prepareDelayMillis = prepareDelayMillis;
            this.commitSuccess = commitSuccess;
            this.commitDelayMillis = commitDelayMillis;
            this.abortSuccess = abortSuccess;
            this.abortDelayMillis = abortDelayMillis;
        }

        // This version always returns availability as provided.
        @Override
        public boolean isAvailable() {
            return available;
        }

        @Override
        public boolean prepare(int transactionId) throws RemoteException {
            if (!available) {
                throw new RemoteException(name + " is not available during prepare.");
            }
            try {
                Thread.sleep(prepareDelayMillis);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                throw new RemoteException(name + " interrupted during prepare.");
            }
            return prepareSuccess;
        }

        @Override
        public void commit(int transactionId) throws RemoteException {
            if (!available) {
                throw new RemoteException(name + " is not available during commit.");
            }
            try {
                Thread.sleep(commitDelayMillis);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                throw new RemoteException(name + " interrupted during commit.");
            }
            if (!commitSuccess) {
                throw new RemoteException(name + " failed during commit.");
            }
            // Ensure idempotency: only mark once.
            if (!committedOrAborted) {
                committedOrAborted = true;
            }
        }

        @Override
        public void abort(int transactionId) throws RemoteException {
            if (!available) {
                throw new RemoteException(name + " is not available during abort.");
            }
            try {
                Thread.sleep(abortDelayMillis);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                throw new RemoteException(name + " interrupted during abort.");
            }
            if (!abortSuccess) {
                throw new RemoteException(name + " failed during abort.");
            }
            // Ensure idempotency: only mark once.
            if (!committedOrAborted) {
                committedOrAborted = true;
            }
        }
    }

    // Test case 1: All DataNodes vote commit and commit successfully.
    @Test
    public void testTransactionCommitSuccess() {
        TransactionCoordinator coordinator = new TransactionCoordinator();
        int transactionId = 1;

        coordinator.begin_transaction(transactionId);
        // Create three nodes that prepare, commit, and abort successfully without delay.
        DataNode node1 = new MockDataNode("Node1", true, true, 0, true, 0, true, 0);
        DataNode node2 = new MockDataNode("Node2", true, true, 0, true, 0, true, 0);
        DataNode node3 = new MockDataNode("Node3", true, true, 0, true, 0, true, 0);

        coordinator.register_data_node(transactionId, node1);
        coordinator.register_data_node(transactionId, node2);
        coordinator.register_data_node(transactionId, node3);

        boolean committed = coordinator.execute_transaction(transactionId);
        assertTrue(committed, "Transaction should commit when all nodes vote commit and commit successfully.");
    }

    // Test case 2: One DataNode votes abort during prepare.
    @Test
    public void testTransactionAbortDueToPrepareAbort() {
        TransactionCoordinator coordinator = new TransactionCoordinator();
        int transactionId = 2;

        coordinator.begin_transaction(transactionId);
        DataNode node1 = new MockDataNode("Node1", true, true, 0, true, 0, true, 0);
        DataNode node2 = new MockDataNode("Node2", true, false, 0, true, 0, true, 0); // Votes abort in prepare
        DataNode node3 = new MockDataNode("Node3", true, true, 0, true, 0, true, 0);

        coordinator.register_data_node(transactionId, node1);
        coordinator.register_data_node(transactionId, node2);
        coordinator.register_data_node(transactionId, node3);

        boolean committed = coordinator.execute_transaction(transactionId);
        assertFalse(committed, "Transaction should abort if any node votes abort during prepare.");
    }

    // Test case 3: DataNode times out during prepare phase.
    // This test uses a timeout annotation to avoid long waits.
    @Test
    @Timeout(10)
    public void testTransactionAbortDueToTimeout() {
        TransactionCoordinator coordinator = new TransactionCoordinator();
        int transactionId = 3;

        coordinator.begin_transaction(transactionId);
        DataNode node1 = new MockDataNode("Node1", true, true, 0, true, 0, true, 0);
        // Provide a delay longer than the expected timeout (assumed 5 seconds) to force timeout.
        DataNode node2 = new MockDataNode("Node2", true, true, 6000, true, 0, true, 0);
        DataNode node3 = new MockDataNode("Node3", true, true, 0, true, 0, true, 0);

        coordinator.register_data_node(transactionId, node1);
        coordinator.register_data_node(transactionId, node2);
        coordinator.register_data_node(transactionId, node3);

        boolean committed = coordinator.execute_transaction(transactionId);
        assertFalse(committed, "Transaction should abort if any node does not respond in time during prepare.");
    }

    // Test case 4: DataNode failure during commit phase.
    @Test
    public void testTransactionAbortDueToCommitFailure() {
        TransactionCoordinator coordinator = new TransactionCoordinator();
        int transactionId = 4;

        coordinator.begin_transaction(transactionId);
        DataNode node1 = new MockDataNode("Node1", true, true, 0, true, 0, true, 0);
        // Node2 will throw exception during commit even though it votes commit in prepare.
        DataNode node2 = new MockDataNode("Node2", true, true, 0, false, 0, true, 0);
        DataNode node3 = new MockDataNode("Node3", true, true, 0, true, 0, true, 0);

        coordinator.register_data_node(transactionId, node1);
        coordinator.register_data_node(transactionId, node2);
        coordinator.register_data_node(transactionId, node3);

        boolean committed = coordinator.execute_transaction(transactionId);
        assertFalse(committed, "Transaction should abort if any node fails during commit.");
    }

    // Test case 5: Concurrency test - multiple transactions in parallel.
    @Test
    public void testConcurrentTransactions() throws InterruptedException {
        final int numTransactions = 10;
        ExecutorService executor = Executors.newFixedThreadPool(numTransactions);
        List<Boolean> results = new ArrayList<>();
        List<Integer> txIds = new ArrayList<>();

        // Initialize multiple transactions
        for (int i = 0; i < numTransactions; i++) {
            txIds.add(100 + i);
        }

        for (int txId : txIds) {
            executor.submit(() -> {
                TransactionCoordinator coordinator = new TransactionCoordinator();
                coordinator.begin_transaction(txId);
                // Each transaction gets 5 nodes that always succeed.
                for (int j = 0; j < 5; j++) {
                    DataNode node = new MockDataNode("Tx" + txId + "Node" + j, true, true, 0, true, 0, true, 0);
                    coordinator.register_data_node(txId, node);
                }
                boolean result = coordinator.execute_transaction(txId);
                synchronized(results) {
                    results.add(result);
                }
            });
        }
        executor.shutdown();
        executor.awaitTermination(30, TimeUnit.SECONDS);

        // All transactions should commit successfully.
        for (Boolean res : results) {
            assertTrue(res, "All concurrent transactions should commit successfully.");
        }
    }
}