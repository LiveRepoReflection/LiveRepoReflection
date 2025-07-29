import java.util.concurrent.*;
import java.util.*;
 
public class TransactionCoordinator {
    private final ConcurrentMap<Integer, List<DataNode>> transactionMap;
 
    public TransactionCoordinator() {
        transactionMap = new ConcurrentHashMap<>();
    }
 
    public void begin_transaction(int transactionId) {
        transactionMap.putIfAbsent(transactionId, Collections.synchronizedList(new ArrayList<>()));
    }
 
    public void register_data_node(int transactionId, DataNode dataNode) {
        List<DataNode> nodes = transactionMap.get(transactionId);
        if (nodes != null) {
            nodes.add(dataNode);
        }
    }
 
    public boolean execute_transaction(int transactionId) {
        List<DataNode> nodes = transactionMap.get(transactionId);
        if (nodes == null) {
            return false;
        }
 
        boolean allVoteCommit = true;
        ExecutorService prepareExecutor = Executors.newFixedThreadPool(nodes.size());
        List<Future<Boolean>> prepareFutures = new ArrayList<>();
 
        for (DataNode node : nodes) {
            Future<Boolean> future = prepareExecutor.submit(() -> {
                try {
                    if (!node.isAvailable()) {
                        return false;
                    }
                    return node.prepare(transactionId);
                } catch (RemoteException e) {
                    return false;
                }
            });
            prepareFutures.add(future);
        }
 
        for (Future<Boolean> future : prepareFutures) {
            try {
                Boolean vote = future.get(5, TimeUnit.SECONDS);
                if (!vote) {
                    allVoteCommit = false;
                }
            } catch (Exception e) {
                allVoteCommit = false;
            }
        }
 
        prepareExecutor.shutdownNow();
 
        if (!allVoteCommit) {
            ExecutorService abortExecutor = Executors.newFixedThreadPool(nodes.size());
            List<Future<?>> abortFutures = new ArrayList<>();
 
            for (DataNode node : nodes) {
                Future<?> abortFuture = abortExecutor.submit(() -> {
                    try {
                        if (node.isAvailable()) {
                            node.abort(transactionId);
                        }
                    } catch (RemoteException e) {
                        // Exception during abort is ignored
                    }
                });
                abortFutures.add(abortFuture);
            }
 
            for (Future<?> future : abortFutures) {
                try {
                    future.get();
                } catch (Exception e) {
                    // Ignored
                }
            }
 
            abortExecutor.shutdownNow();
            return false;
        }
 
        ExecutorService commitExecutor = Executors.newFixedThreadPool(nodes.size());
        List<Future<Boolean>> commitFutures = new ArrayList<>();
 
        for (DataNode node : nodes) {
            Future<Boolean> future = commitExecutor.submit(() -> {
                try {
                    if (node.isAvailable()) {
                        node.commit(transactionId);
                        return true;
                    }
                } catch (RemoteException e) {
                    // Commit failure
                }
                return false;
            });
            commitFutures.add(future);
        }
 
        boolean allCommit = true;
        for (Future<Boolean> future : commitFutures) {
            try {
                Boolean result = future.get();
                if (!result) {
                    allCommit = false;
                }
            } catch (Exception e) {
                allCommit = false;
            }
        }
 
        commitExecutor.shutdownNow();
 
        if (!allCommit) {
            ExecutorService abortExecutor2 = Executors.newFixedThreadPool(nodes.size());
            List<Future<?>> abortFutures2 = new ArrayList<>();
 
            for (DataNode node : nodes) {
                Future<?> abortFuture = abortExecutor2.submit(() -> {
                    try {
                        if (node.isAvailable()) {
                            node.abort(transactionId);
                        }
                    } catch (RemoteException e) {
                        // Exception during abort is ignored
                    }
                });
                abortFutures2.add(abortFuture);
            }
 
            for (Future<?> future : abortFutures2) {
                try {
                    future.get();
                } catch (Exception e) {
                    // Ignored
                }
            }
 
            abortExecutor2.shutdownNow();
            return false;
        }
 
        return true;
    }
}