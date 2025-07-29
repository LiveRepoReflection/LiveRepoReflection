import java.util.List;
import java.util.UUID;
import java.util.ArrayList;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;

public class DistributedTransactionManager {
    private final List<TransactionalService> services = new CopyOnWriteArrayList<>();
    private final ConcurrentHashMap<UUID, Boolean> transactionResults = new ConcurrentHashMap<>();
    private final ExecutorService executor = Executors.newCachedThreadPool();
    private final long PREPARE_TIMEOUT = 2000; // timeout in milliseconds for prepare phase

    public void registerService(TransactionalService service) {
        services.add(service);
    }

    public UUID beginTransaction() {
        return UUID.randomUUID();
    }

    public boolean commitTransaction(UUID transactionId, Object data) {
        // Check idempotency: if the transaction has been processed, return its result.
        if (transactionResults.containsKey(transactionId)) {
            return transactionResults.get(transactionId);
        }
        synchronized (getLock(transactionId)) {
            if (transactionResults.containsKey(transactionId)) {
                return transactionResults.get(transactionId);
            }
            boolean result = executeTransaction(transactionId, data);
            transactionResults.put(transactionId, result);
            return result;
        }
    }

    // Using the transactionId itself as a lock object for per-transaction synchronization.
    private Object getLock(UUID transactionId) {
        return transactionId;
    }

    private boolean executeTransaction(UUID transactionId, Object data) {
        // Phase 1: Prepare - execute prepare calls concurrently.
        List<Future<Boolean>> prepareFutures = new ArrayList<>();
        for (TransactionalService service : services) {
            Future<Boolean> future = executor.submit(() -> service.prepare(transactionId, data));
            prepareFutures.add(future);
        }
        try {
            for (Future<Boolean> future : prepareFutures) {
                Boolean prepared = future.get(PREPARE_TIMEOUT, TimeUnit.MILLISECONDS);
                if (prepared == null || !prepared) {
                    rollbackAll(transactionId);
                    return false;
                }
            }
        } catch (Exception e) {
            rollbackAll(transactionId);
            return false;
        }

        // Phase 2: Commit - execute commit calls concurrently.
        List<Future<Boolean>> commitFutures = new ArrayList<>();
        for (TransactionalService service : services) {
            Future<Boolean> future = executor.submit(() -> service.commit(transactionId));
            commitFutures.add(future);
        }
        try {
            for (Future<Boolean> future : commitFutures) {
                Boolean committed = future.get();
                if (committed == null || !committed) {
                    rollbackAll(transactionId);
                    return false;
                }
            }
        } catch (Exception e) {
            rollbackAll(transactionId);
            return false;
        }
        return true;
    }

    private void rollbackAll(UUID transactionId) {
        List<Future<Boolean>> rollbackFutures = new ArrayList<>();
        for (TransactionalService service : services) {
            Future<Boolean> future = executor.submit(() -> service.rollback(transactionId));
            rollbackFutures.add(future);
        }
        for (Future<Boolean> future : rollbackFutures) {
            try {
                future.get();
            } catch (Exception e) {
                // Suppress exceptions during rollback.
            }
        }
    }
}