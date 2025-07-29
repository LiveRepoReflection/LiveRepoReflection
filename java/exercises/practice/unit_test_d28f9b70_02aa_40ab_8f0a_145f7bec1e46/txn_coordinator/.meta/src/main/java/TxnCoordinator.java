import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.locks.ReentrantReadWriteLock;

/**
 * A simple implementation of a distributed transaction coordinator using 2PC.
 * This implementation is for testing purposes and uses asynchronous communication.
 */
public class TxnCoordinator {
    private final Map<String, TxnNode> nodes = new ConcurrentHashMap<>();
    private final Map<String, List<OpWithNode>> transactions = new ConcurrentHashMap<>();
    private final ReentrantReadWriteLock lock = new ReentrantReadWriteLock();
    private final ExecutorService executor = Executors.newCachedThreadPool();
    private final int TIMEOUT_MILLIS = 2000;

    public void registerNode(String nodeId, TxnNode node) {
        nodes.put(nodeId, node);
    }

    public void begin(String transactionId) {
        lock.writeLock().lock();
        try {
            transactions.put(transactionId, new ArrayList<>());
        } finally {
            lock.writeLock().unlock();
        }
    }

    public void put(String transactionId, String nodeId, String key, String value) {
        addOperation(transactionId, nodeId, new Operation(Operation.Type.PUT, key, value));
    }

    public void delete(String transactionId, String nodeId, String key) {
        addOperation(transactionId, nodeId, new Operation(Operation.Type.DELETE, key, null));
    }

    private void addOperation(String transactionId, String nodeId, Operation op) {
        lock.writeLock().lock();
        try {
            if (!transactions.containsKey(transactionId))
                throw new IllegalArgumentException("Transaction not found: " + transactionId);
            transactions.get(transactionId).add(new OpWithNode(nodeId, op));
        } finally {
            lock.writeLock().unlock();
        }
    }

    public boolean commit(String transactionId) throws Exception {
        // Execute Phase 1: Prepare
        List<OpWithNode> ops;
        lock.readLock().lock();
        try {
            ops = transactions.get(transactionId);
            if (ops == null)
                throw new IllegalArgumentException("Transaction not found: " + transactionId);
        } finally {
            lock.readLock().unlock();
        }

        // Group operations by node.
        Map<String, List<Operation>> opsByNode = new HashMap<>();
        for (OpWithNode opWithNode : ops) {
            opsByNode.computeIfAbsent(opWithNode.nodeId, k -> new ArrayList<>()).add(opWithNode.op);
        }

        List<CompletableFuture<NodeResponse>> prepareFutures = new ArrayList<>();
        for (Map.Entry<String, List<Operation>> entry : opsByNode.entrySet()) {
            TxnNode node = nodes.get(entry.getKey());
            if (node == null)
                throw new IllegalArgumentException("Node not registered: " + entry.getKey());
            CompletableFuture<NodeResponse> future = node.prepare(transactionId, entry.getValue());
            prepareFutures.add(future.orTimeout(TIMEOUT_MILLIS, TimeUnit.MILLISECONDS));
        }

        boolean allAck = true;
        try {
            for (CompletableFuture<NodeResponse> future : prepareFutures) {
                NodeResponse response = future.get();
                if (!response.isAck()) {
                    allAck = false;
                    break;
                }
            }
        } catch (Exception e) {
            allAck = false;
        }

        // Execute Phase 2: Commit or Abort
        List<CompletableFuture<Void>> phase2Futures = new ArrayList<>();
        for (String nodeId : opsByNode.keySet()) {
            TxnNode node = nodes.get(nodeId);
            if (allAck) {
                phase2Futures.add(node.commit(transactionId));
            } else {
                phase2Futures.add(node.abort(transactionId));
            }
        }
        CompletableFuture.allOf(phase2Futures.toArray(new CompletableFuture[0]))
                .get(TIMEOUT_MILLIS, TimeUnit.MILLISECONDS);

        return allAck;
    }

    public void abort(String transactionId) throws Exception {
        List<OpWithNode> ops;
        lock.readLock().lock();
        try {
            ops = transactions.get(transactionId);
            if (ops == null)
                throw new IllegalArgumentException("Transaction not found: " + transactionId);
        } finally {
            lock.readLock().unlock();
        }
        Set<String> nodeIds = new HashSet<>();
        for (OpWithNode opWithNode : ops) {
            nodeIds.add(opWithNode.nodeId);
        }
        List<CompletableFuture<Void>> abortFutures = new ArrayList<>();
        for (String nodeId : nodeIds) {
            TxnNode node = nodes.get(nodeId);
            if (node != null) {
                abortFutures.add(node.abort(transactionId));
            }
        }
        CompletableFuture.allOf(abortFutures.toArray(new CompletableFuture[0]))
                .get(TIMEOUT_MILLIS, TimeUnit.MILLISECONDS);
    }

    private static class OpWithNode {
        final String nodeId;
        final Operation op;
        OpWithNode(String nodeId, Operation op) {
            this.nodeId = nodeId;
            this.op = op;
        }
    }
}