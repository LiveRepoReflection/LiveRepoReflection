package dtm;

import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;

public class DTM {
    private final Map<String, List<Service>> transactions = new ConcurrentHashMap<>();

    public String begin() {
        String transactionId = UUID.randomUUID().toString();
        transactions.put(transactionId, new CopyOnWriteArrayList<>());
        return transactionId;
    }

    public void enlist(String transactionId, Service service) {
        List<Service> services = transactions.get(transactionId);
        if (services == null) {
            throw new IllegalArgumentException("Transaction ID not found: " + transactionId);
        }
        services.add(service);
    }

    public void commit(String transactionId) throws TransactionException {
        List<Service> services = transactions.get(transactionId);
        if (services == null) {
            throw new TransactionException("Transaction not found: " + transactionId);
        }

        // Prepare phase: each service must vote commit (true)
        for (Service service : services) {
            try {
                boolean vote = service.prepare(transactionId);
                if (!vote) {
                    rollbackInternal(transactionId, services);
                    throw new TransactionException("Service " + service.getClass().getSimpleName() + " returned rollback vote during prepare.");
                }
            } catch (Exception e) {
                rollbackInternal(transactionId, services);
                throw new TransactionException("Exception during prepare from service " + service.getClass().getSimpleName(), e);
            }
        }

        // Commit phase: commit each service with retry mechanism.
        for (Service service : services) {
            try {
                retryOperation(() -> service.commit(transactionId));
            } catch (Exception e) {
                rollbackInternal(transactionId, services);
                throw new TransactionException("Commit failed for service " + service.getClass().getSimpleName(), e);
            }
        }

        transactions.remove(transactionId);
    }

    public void rollback(String transactionId) throws TransactionException {
        List<Service> services = transactions.get(transactionId);
        if (services == null) {
            throw new TransactionException("Transaction not found: " + transactionId);
        }
        rollbackInternal(transactionId, services);
        transactions.remove(transactionId);
    }

    private void rollbackInternal(String transactionId, List<Service> services) throws TransactionException {
        TransactionException exception = null;
        for (Service service : services) {
            try {
                retryOperation(() -> service.rollback(transactionId));
            } catch (Exception e) {
                if (exception == null) {
                    exception = new TransactionException("Rollback failed for service " + service.getClass().getSimpleName(), e);
                }
            }
        }
        if (exception != null) {
            throw exception;
        }
    }

    private void retryOperation(RetryableOperation operation) throws Exception {
        int maxRetries = 3;
        long delay = 100; // milliseconds
        for (int i = 0; i < maxRetries; i++) {
            try {
                operation.execute();
                return;
            } catch (Exception e) {
                if (i == maxRetries - 1) {
                    throw e;
                }
                try {
                    Thread.sleep(delay);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    throw new Exception("Thread interrupted during retry", ie);
                }
                delay *= 2;
            }
        }
    }

    @FunctionalInterface
    interface RetryableOperation {
        void execute() throws Exception;
    }
}