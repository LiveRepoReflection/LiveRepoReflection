package tx_coordinator;

import java.util.*;

public class TransactionCoordinator {
    private final Map<String, StorageNode> storageNodes;
    private final int timeoutMs;
    private boolean simulateCoordinatorFailure = false;

    public TransactionCoordinator(Map<String, StorageNode> storageNodes, int timeoutMs) {
        this.storageNodes = storageNodes;
        this.timeoutMs = timeoutMs;
    }

    public void setSimulateCoordinatorFailure(boolean simulateCoordinatorFailure) {
        this.simulateCoordinatorFailure = simulateCoordinatorFailure;
    }

    public boolean submitTransaction(List<Operation> operations) {
        String transactionId = UUID.randomUUID().toString();
        // Group operations by storage node id
        Map<String, List<Operation>> nodeOperations = new HashMap<>();
        for (Operation op : operations) {
            nodeOperations.computeIfAbsent(op.getStorageNodeId(), k -> new ArrayList<>()).add(op);
        }

        // Validate all referenced storage nodes exist
        for (String nodeId : nodeOperations.keySet()) {
            if (!storageNodes.containsKey(nodeId)) {
                abortNodes(nodeOperations);
                return false;
            }
        }

        // Prepare phase: send prepare message to all nodes involved
        Map<String, Boolean> prepareResults = new HashMap<>();
        for (Map.Entry<String, List<Operation>> entry : nodeOperations.entrySet()) {
            String nodeId = entry.getKey();
            StorageNode node = storageNodes.get(nodeId);
            boolean allPrepared = true;
            for (Operation op : entry.getValue()) {
                boolean result = node.prepare(op);
                if (!result) {
                    allPrepared = false;
                    break;
                }
            }
            prepareResults.put(nodeId, allPrepared);
        }

        boolean globalPrepared = true;
        for (boolean result : prepareResults.values()) {
            if (!result) {
                globalPrepared = false;
                break;
            }
        }

        // Check if we need to simulate coordinator failure
        if (simulateCoordinatorFailure) {
            // Simulate delay beyond timeout if coordinator fails
            try {
                Thread.sleep(timeoutMs + 50);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            boolean recoveredDecision = gossipRecovery(nodeOperations.keySet(), transactionId);
            if (recoveredDecision) {
                commitNodes(nodeOperations);
                return true;
            } else {
                abortNodes(nodeOperations);
                return false;
            }
        } else {
            // Normal operation: if all nodes prepared, commit; otherwise, abort.
            if (globalPrepared) {
                commitNodes(nodeOperations);
                return true;
            } else {
                abortNodes(nodeOperations);
                return false;
            }
        }
    }

    private void commitNodes(Map<String, List<Operation>> nodeOperations) {
        for (Map.Entry<String, List<Operation>> entry : nodeOperations.entrySet()) {
            StorageNode node = storageNodes.get(entry.getKey());
            for (Operation op : entry.getValue()) {
                node.commit(op);
            }
        }
    }

    private void abortNodes(Map<String, List<Operation>> nodeOperations) {
        for (Map.Entry<String, List<Operation>> entry : nodeOperations.entrySet()) {
            StorageNode node = storageNodes.get(entry.getKey());
            for (Operation op : entry.getValue()) {
                node.abort(op);
            }
        }
    }

    // Gossip protocol: each node sends its prepare status.
    private boolean gossipRecovery(Set<String> nodeIds, String transactionId) {
        Map<String, Boolean> gossipStatus = new HashMap<>();
        for (String nodeId : nodeIds) {
            StorageNode node = storageNodes.get(nodeId);
            node.sendGossip(transactionId, gossipStatus);
        }
        // Simulate a short delay for gossip to complete.
        try {
            Thread.sleep(50);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        for (Boolean status : gossipStatus.values()) {
            if (!status) {
                return false;
            }
        }
        return true;
    }
}