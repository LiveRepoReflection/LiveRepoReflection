import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

import java.util.*;
import java.util.concurrent.*;
import static org.junit.jupiter.api.Assertions.*;

/**
 * Comprehensive unit tests for the TxnCoordinator implementation.
 * These tests simulate a distributed transaction coordinator using dummy node implementations.
 */
public class TxnCoordinatorTest {

    private TxnCoordinator coordinator;

    @BeforeEach
    public void setUp() {
        coordinator = new TxnCoordinator();
    }

    /**
     * DummyNode simulates a distributed key-value store node.
     * Each node can be configured to always ACK, always NACK, or simulate a timeout on prepare.
     */
    private static class DummyNode implements TxnNode {
        enum Behavior {
            ALWAYS_ACK,
            ALWAYS_NACK,
            TIMEOUT
        }

        private final String nodeId;
        private final Behavior behavior;
        private final Map<String, String> store = new ConcurrentHashMap<>();
        // To track if commit/abort have been applied, for idempotency testing.
        private boolean committed = false;
        private boolean aborted = false;

        public DummyNode(String nodeId, Behavior behavior) {
            this.nodeId = nodeId;
            this.behavior = behavior;
        }

        @Override
        public CompletableFuture<NodeResponse> prepare(String transactionId, List<Operation> operations) {
            return CompletableFuture.supplyAsync(() -> {
                if (behavior == Behavior.TIMEOUT) {
                    // Simulate a delay beyond coordinator timeout threshold.
                    try {
                        Thread.sleep(3000);
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                    }
                }
                if (behavior == Behavior.ALWAYS_NACK) {
                    return new NodeResponse(false, "SimulatedFailure");
                }
                // For ALWAYS_ACK and if not timing out
                return new NodeResponse(true, null);
            });
        }

        @Override
        public CompletableFuture<Void> commit(String transactionId) {
            return CompletableFuture.runAsync(() -> {
                // Simulate idempotency.
                if (!committed) {
                    // Apply all pending operations in a real node;
                    committed = true;
                }
            });
        }

        @Override
        public CompletableFuture<Void> abort(String transactionId) {
            return CompletableFuture.runAsync(() -> {
                if (!aborted) {
                    // Discard pending operations.
                    aborted = true;
                }
            });
        }

        public boolean isCommitted() {
            return committed;
        }

        public boolean isAborted() {
            return aborted;
        }

        public String getNodeId() {
            return nodeId;
        }

        public Map<String, String> getStore() {
            return store;
        }
    }

    /**
     * Test a successful transaction where all nodes respond with ACK.
     */
    @Test
    @Timeout(5)
    public void testSuccessfulCommit() throws Exception {
        String txnId = UUID.randomUUID().toString();
        // Create two dummy nodes that always ACK.
        DummyNode node1 = new DummyNode("node1", DummyNode.Behavior.ALWAYS_ACK);
        DummyNode node2 = new DummyNode("node2", DummyNode.Behavior.ALWAYS_ACK);
        coordinator.registerNode("node1", node1);
        coordinator.registerNode("node2", node2);

        coordinator.begin(txnId);
        coordinator.put(txnId, "node1", "key1", "value1");
        coordinator.put(txnId, "node2", "key2", "value2");

        boolean commitResult = coordinator.commit(txnId);
        assertTrue(commitResult, "Transaction should commit successfully.");

        // Validate that the commit was applied on each node.
        assertTrue(node1.isCommitted(), "Node1 should have committed the transaction.");
        assertTrue(node2.isCommitted(), "Node2 should have committed the transaction.");
    }

    /**
     * Test a transaction that aborts because one node returns NACK.
     */
    @Test
    @Timeout(5)
    public void testTransactionAbortDueToNack() throws Exception {
        String txnId = UUID.randomUUID().toString();
        // Create one node that ACKs and one that always NACKs.
        DummyNode node1 = new DummyNode("node1", DummyNode.Behavior.ALWAYS_ACK);
        DummyNode node2 = new DummyNode("node2", DummyNode.Behavior.ALWAYS_NACK);
        coordinator.registerNode("node1", node1);
        coordinator.registerNode("node2", node2);

        coordinator.begin(txnId);
        coordinator.put(txnId, "node1", "key1", "value1");
        coordinator.put(txnId, "node2", "key2", "value2");

        boolean commitResult = coordinator.commit(txnId);
        assertFalse(commitResult, "Transaction should be aborted due to a NACK response.");

        // Validate that abort was invoked on each node.
        assertTrue(node1.isAborted(), "Node1 should have aborted the transaction.");
        assertTrue(node2.isAborted(), "Node2 should have aborted the transaction.");
    }

    /**
     * Test that a transaction is aborted if one node times out.
     */
    @Test
    @Timeout(5)
    public void testTimeoutHandling() throws Exception {
        String txnId = UUID.randomUUID().toString();
        // Create one node that ACKs and one node that times out.
        DummyNode node1 = new DummyNode("node1", DummyNode.Behavior.ALWAYS_ACK);
        DummyNode node2 = new DummyNode("node2", DummyNode.Behavior.TIMEOUT);
        coordinator.registerNode("node1", node1);
        coordinator.registerNode("node2", node2);

        coordinator.begin(txnId);
        coordinator.put(txnId, "node1", "key1", "value1");
        coordinator.put(txnId, "node2", "key2", "value2");

        boolean commitResult = coordinator.commit(txnId);
        assertFalse(commitResult, "Transaction should be aborted due to a timeout from one node.");

        // Both nodes should have executed abort.
        assertTrue(node1.isAborted(), "Node1 should have aborted the transaction.");
        assertTrue(node2.isAborted(), "Node2 should have aborted the transaction.");
    }

    /**
     * Test idempotency of commit and abort operations by issuing repeated commit and abort calls.
     */
    @Test
    @Timeout(5)
    public void testIdempotency() throws Exception {
        String txnId = UUID.randomUUID().toString();
        DummyNode node1 = new DummyNode("node1", DummyNode.Behavior.ALWAYS_ACK);
        coordinator.registerNode("node1", node1);

        coordinator.begin(txnId);
        coordinator.put(txnId, "node1", "key1", "value1");

        // First commit attempt.
        boolean firstCommit = coordinator.commit(txnId);
        assertTrue(firstCommit, "First commit should succeed.");
        // Second commit attempt should also return true (idempotent) but not reapply the operations.
        boolean secondCommit = coordinator.commit(txnId);
        assertTrue(secondCommit, "Second commit should be idempotent and succeed.");
        // Simulate a scenario where abort is called after a successful commit.
        coordinator.abort(txnId);
        // Node should remain in committed state.
        assertTrue(node1.isCommitted(), "Node1 should remain committed despite abort call after commit.");
    }
}