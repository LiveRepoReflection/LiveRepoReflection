import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;

public class TransactionCoordinator {
    private final List<Service> services = new ArrayList<>();
    private final Map<java.util.UUID, Transaction> transactions = new ConcurrentHashMap<>();
    private final int timeoutMillis = 1000;
    private final int retryLimit = 3;

    public void registerService(Service service) {
        services.add(service);
    }

    public Transaction beginTransaction() {
        Transaction txn = new Transaction();
        transactions.put(txn.getId(), txn);
        return txn;
    }

    public void addOperation(Transaction txn, String op) {
        txn.addOperation(op);
    }

    public boolean commitTransaction(Transaction txn) {
        txn.setStatus(TransactionStatus.PREPARED);
        List<Future<Boolean>> futures = new ArrayList<>();
        ExecutorService executor = Executors.newFixedThreadPool(services.size());

        for (Service service : services) {
            futures.add(executor.submit(() -> {
                int attempt = 0;
                // In this simple implementation, we just try once up to retryLimit.
                while (attempt < retryLimit) {
                    boolean result = service.prepare(txn);
                    return result;
                }
                return false;
            }));
        }
        executor.shutdown();
        try {
            if (!executor.awaitTermination(timeoutMillis, TimeUnit.MILLISECONDS)) {
                executor.shutdownNow();
                txn.setStatus(TransactionStatus.ABORTED);
                return false;
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            txn.setStatus(TransactionStatus.ABORTED);
            return false;
        }

        boolean allPrepared = true;
        for (Future<Boolean> future : futures) {
            try {
                if (!future.get(timeoutMillis, TimeUnit.MILLISECONDS)) {
                    allPrepared = false;
                    break;
                }
            } catch (Exception e) {
                allPrepared = false;
                break;
            }
        }

        if (!allPrepared) {
            txn.setStatus(TransactionStatus.ABORTED);
            for (Service service : services) {
                service.rollback(txn);
            }
            return false;
        }

        for (Service service : services) {
            service.commit(txn);
        }
        txn.setStatus(TransactionStatus.COMMITTED);
        return true;
    }

    public void rollbackTransaction(Transaction txn) {
        txn.setStatus(TransactionStatus.ABORTED);
        for (Service service : services) {
            service.rollback(txn);
        }
    }
}