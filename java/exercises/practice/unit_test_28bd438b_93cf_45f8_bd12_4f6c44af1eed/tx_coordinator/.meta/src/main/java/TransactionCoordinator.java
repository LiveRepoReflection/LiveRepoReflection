package tx_coordinator;

import java.util.List;
import java.util.Map;
import java.util.concurrent.Callable;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

public class TransactionCoordinator {
    private final Map<String, Service> serviceRegistry = new ConcurrentHashMap<>();
    private final Map<String, TransactionStatus> completedTransactions = new ConcurrentHashMap<>();
    private final ExecutorService executor;
    // Default timeout in milliseconds
    private long timeoutMs = 1000;

    public TransactionCoordinator() {
        this.executor = Executors.newCachedThreadPool();
    }

    public void setTimeout(long timeoutMs) {
        this.timeoutMs = timeoutMs;
    }

    public void registerService(String serviceId, Service service) {
        serviceRegistry.put(serviceId, service);
    }

    public TransactionStatus initiateTransaction(String transactionId, List<String> participants) {
        // Check idempotency: if transaction already processed, return the recorded result.
        if (completedTransactions.containsKey(transactionId)) {
            return completedTransactions.get(transactionId);
        }

        boolean prepareAllSuccess = true;

        // Prepare phase: For each participant, run prepare with timeout.
        for (String serviceId : participants) {
            Service service = serviceRegistry.get(serviceId);
            if (service == null) {
                prepareAllSuccess = false;
                break;
            }
            Callable<Boolean> prepareTask = () -> service.prepare(transactionId);
            Future<Boolean> future = executor.submit(prepareTask);
            try {
                boolean result = future.get(timeoutMs, TimeUnit.MILLISECONDS);
                if (!result) {
                    prepareAllSuccess = false;
                }
            } catch (Exception e) {
                // Timeout or interruption; consider as failure.
                prepareAllSuccess = false;
            }
        }

        TransactionStatus finalStatus;
        // Commit or Rollback phase based on prepare results.
        if (prepareAllSuccess) {
            for (String serviceId : participants) {
                Service service = serviceRegistry.get(serviceId);
                if (service != null) {
                    service.commit(transactionId);
                }
            }
            finalStatus = TransactionStatus.COMMITTED;
        } else {
            for (String serviceId : participants) {
                Service service = serviceRegistry.get(serviceId);
                if (service != null) {
                    service.rollback(transactionId);
                }
            }
            finalStatus = TransactionStatus.ROLLED_BACK;
        }

        // Cache the result for idempotency.
        completedTransactions.put(transactionId, finalStatus);
        return finalStatus;
    }

    public void shutdown() {
        executor.shutdownNow();
    }
}