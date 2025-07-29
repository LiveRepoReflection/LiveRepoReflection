package tx_coordinator;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Timeout;
import org.junit.jupiter.api.Assertions;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;

public class CoordinatorTest {

    private TransactionCoordinator coordinator;
    private Map<String, StorageNode> storageNodes;

    @BeforeEach
    public void setup() {
        // Create mock storage nodes with default successful prepare responses
        storageNodes = new HashMap<>();
        storageNodes.put("nodeA", new MockStorageNode("nodeA", true));
        storageNodes.put("nodeB", new MockStorageNode("nodeB", true));
        storageNodes.put("nodeC", new MockStorageNode("nodeC", true));
        coordinator = new TransactionCoordinator(storageNodes, 500); // timeout in milliseconds
    }

    @Test
    public void testSingleOperationCommit() {
        List<Operation> transaction = new ArrayList<>();
        transaction.add(new Operation("nodeA", "write", "key1", "value1"));
        boolean result = coordinator.submitTransaction(transaction);
        Assertions.assertTrue(result, "Transaction with a single operation should commit");
    }

    @Test
    public void testMultipleOperationsCommit() {
        List<Operation> transaction = new ArrayList<>();
        transaction.add(new Operation("nodeA", "write", "key1", "value1"));
        transaction.add(new Operation("nodeB", "write", "key2", "value2"));
        transaction.add(new Operation("nodeC", "read", "key3", null));
        boolean result = coordinator.submitTransaction(transaction);
        Assertions.assertTrue(result, "Transaction with multiple operations should commit");
    }

    @Test
    public void testTransactionAbortDueToNodeFailure() {
        // Simulate failure on nodeB prepare phase
        storageNodes.put("nodeB", new MockStorageNode("nodeB", false));
        coordinator = new TransactionCoordinator(storageNodes, 500);
        
        List<Operation> transaction = new ArrayList<>();
        transaction.add(new Operation("nodeA", "write", "key1", "value1"));
        transaction.add(new Operation("nodeB", "write", "key2", "value2"));
        transaction.add(new Operation("nodeC", "read", "key3", null));
        boolean result = coordinator.submitTransaction(transaction);
        Assertions.assertFalse(result, "Transaction should abort if any node fails to prepare");
    }

    @Test
    @Timeout(3)
    public void testCoordinatorFailureRecovery() {
        // Simulate coordinator failure after prepare phase.
        // All nodes are set to succeed in prepare.
        TransactionCoordinator faultyCoordinator = new TransactionCoordinator(storageNodes, 200);
        faultyCoordinator.setSimulateCoordinatorFailure(true);
        
        List<Operation> transaction = new ArrayList<>();
        transaction.add(new Operation("nodeA", "write", "key1", "value1"));
        transaction.add(new Operation("nodeB", "write", "key2", "value2"));
        
        boolean result = faultyCoordinator.submitTransaction(transaction);
        // After gossip recovery, the transaction should be committed if no abort occurred.
        Assertions.assertTrue(result, "Transaction should commit after recovery from coordinator failure");
    }

    @Test
    public void testConcurrentTransactions() throws InterruptedException, ExecutionException {
        int numTransactions = 50;
        ExecutorService executor = Executors.newFixedThreadPool(10);
        List<Future<Boolean>> futures = new ArrayList<>();
        for (int i = 0; i < numTransactions; i++) {
            List<Operation> transaction = new ArrayList<>();
            // Alternate among nodes for diversity
            String nodeId = (i % 3 == 0) ? "nodeA" : (i % 3 == 1 ? "nodeB" : "nodeC");
            transaction.add(new Operation(nodeId, "write", "key" + i, "value" + i));
            futures.add(executor.submit(() -> coordinator.submitTransaction(transaction)));
        }
        for (Future<Boolean> future : futures) {
            Assertions.assertTrue(future.get(), "All concurrent transactions should commit");
        }
        executor.shutdown();
    }

    // MockStorageNode simulates a storage node's behavior during the transaction phases.
    static class MockStorageNode implements StorageNode {
        private final String nodeId;
        private final boolean prepareSuccess;

        public MockStorageNode(String nodeId, boolean prepareSuccess) {
            this.nodeId = nodeId;
            this.prepareSuccess = prepareSuccess;
        }

        @Override
        public boolean prepare(Operation operation) {
            return prepareSuccess;
        }

        @Override
        public void commit(Operation operation) {
            // Simulate successful commit
        }

        @Override
        public void abort(Operation operation) {
            // Simulate abort action
        }

        @Override
        public String getNodeId() {
            return nodeId;
        }

        @Override
        public void sendGossip(String transactionId, Map<String, Boolean> statusMap) {
            // Simulate gossip by contributing this node's prepare status
            statusMap.put(nodeId, prepareSuccess);
        }
    }
}