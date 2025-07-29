import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;

public class TransactionCoordinator {
    private String transactionId;
    private TransactionStatus status;
    private final long timeoutMillis;
    private final List<Enlistment> enlistments;
    private final ExecutorService executor;

    private static class Enlistment {
        final Object service;
        final Callable<Boolean> prepareOperation;

        Enlistment(Object service, Callable<Boolean> prepareOperation) {
            this.service = service;
            this.prepareOperation = prepareOperation;
        }
    }

    public TransactionCoordinator(long timeoutMillis) {
        this.timeoutMillis = timeoutMillis;
        this.status = TransactionStatus.ACTIVE;
        this.enlistments = new ArrayList<>();
        this.executor = Executors.newCachedThreadPool();
    }

    public synchronized String begin() {
        this.transactionId = UUID.randomUUID().toString();
        this.status = TransactionStatus.ACTIVE;
        enlistments.clear();
        return this.transactionId;
    }

    public synchronized void enlist(Object service, Callable<Boolean> prepareOperation) {
        if (this.status != TransactionStatus.ACTIVE) {
            throw new IllegalStateException("Cannot enlist new service when transaction is not active.");
        }
        enlistments.add(new Enlistment(service, prepareOperation));
    }

    public synchronized boolean commit() {
        if (this.status != TransactionStatus.ACTIVE) {
            throw new IllegalStateException("Transaction is not active.");
        }
        this.status = TransactionStatus.PREPARING;
        List<Future<Boolean>> futures = new ArrayList<>();
        try {
            // Submit all prepare operations in parallel
            for (Enlistment enlistment : enlistments) {
                Future<Boolean> future = executor.submit(enlistment.prepareOperation);
                futures.add(future);
            }
            // Wait for all prepare operations with timeout
            for (Future<Boolean> future : futures) {
                Boolean result = future.get(timeoutMillis, TimeUnit.MILLISECONDS);
                if (result == null || !result) {
                    rollbackAll();
                    return false;
                }
            }
        } catch (Exception e) {
            rollbackAll();
            return false;
        }
        // If all prepare operations succeeded, commit all services.
        for (Enlistment enlistment : enlistments) {
            try {
                Method commitMethod = enlistment.service.getClass().getMethod("commit", String.class);
                commitMethod.invoke(enlistment.service, transactionId);
            } catch (Exception e) {
                // In case commit fails, try to rollback all services.
                rollbackAll();
                return false;
            }
        }
        this.status = TransactionStatus.COMMITTED;
        shutdownExecutor();
        return true;
    }

    public synchronized void rollback() {
        if (this.status == TransactionStatus.ABORTED || this.status == TransactionStatus.COMMITTED) {
            return;
        }
        rollbackAll();
    }

    public synchronized TransactionStatus getStatus() {
        return this.status;
    }

    private void rollbackAll() {
        for (Enlistment enlistment : enlistments) {
            try {
                Method rollbackMethod = enlistment.service.getClass().getMethod("rollback", String.class);
                rollbackMethod.invoke(enlistment.service, transactionId);
            } catch (Exception e) {
                // Ignore exceptions during rollback
            }
        }
        this.status = TransactionStatus.ABORTED;
        shutdownExecutor();
    }

    private void shutdownExecutor() {
        executor.shutdownNow();
    }
}