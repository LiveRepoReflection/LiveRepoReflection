package distributed_tx;

import java.util.*;
import java.util.concurrent.*;

public class DistributedTransactionCoordinator {

    private final List<TransactionalService> services;
    private final long prepareTimeoutMillis;
    private final ConcurrentMap<String, List<TransactionalService>> pendingTransactions = new ConcurrentHashMap<>();

    public DistributedTransactionCoordinator(List<TransactionalService> services, long prepareTimeoutMillis) {
        this.services = services;
        this.prepareTimeoutMillis = prepareTimeoutMillis;
    }

    public TransactionResult executeTransaction() {
        String transactionId = UUID.randomUUID().toString();
        ExecutorService executor = Executors.newFixedThreadPool(services.size());
        List<Future<Boolean>> futures = new ArrayList<>();

        // Phase 1: Prepare
        for (TransactionalService service : services) {
            Future<Boolean> future = executor.submit(() -> {
                try {
                    return service.prepare(transactionId);
                } catch (Exception e) {
                    return false;
                }
            });
            futures.add(future);
        }

        boolean allPrepared = true;
        for (Future<Boolean> future : futures) {
            try {
                boolean result = future.get(prepareTimeoutMillis, TimeUnit.MILLISECONDS);
                if (!result) {
                    allPrepared = false;
                }
            } catch (Exception e) {
                allPrepared = false;
            }
        }

        // If not all services prepared successfully, rollback
        if (!allPrepared) {
            for (TransactionalService service : services) {
                try {
                    service.rollback(transactionId);
                } catch (Exception e) {
                    // Ignore rollback exception
                }
            }
            executor.shutdownNow();
            return new TransactionResult(transactionId, TransactionState.ABORTED);
        }

        // Phase 2: Commit
        List<Future<?>> commitFutures = new ArrayList<>();
        for (TransactionalService service : services) {
            Future<?> commitFuture = executor.submit(() -> {
                try {
                    service.commit(transactionId);
                } catch (Exception e) {
                    // Commit failures are not propagated
                }
            });
            commitFutures.add(commitFuture);
        }

        for (Future<?> commitFuture : commitFutures) {
            try {
                commitFuture.get();
            } catch (Exception e) {
                // Ignore exceptions during commit phase
            }
        }

        executor.shutdown();

        // Record the transaction for potential crash recovery simulation.
        pendingTransactions.put(transactionId, new ArrayList<>(services));
        return new TransactionResult(transactionId, TransactionState.COMMITTED);
    }

    public void recoverPendingTransaction(String transactionId) {
        List<TransactionalService> transactionServices = pendingTransactions.get(transactionId);
        if (transactionServices != null) {
            for (TransactionalService service : transactionServices) {
                try {
                    service.commit(transactionId);
                } catch (Exception e) {
                    // Ignore exceptions during recovery commit
                }
            }
            pendingTransactions.remove(transactionId);
        }
    }
}