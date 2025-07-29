import java.util.concurrent.*;
import java.util.*;
import java.util.concurrent.atomic.AtomicReference;

public class TransactionManager {
    private final long timeoutMillis;
    private final int maxCommitRetries;
    private final ExecutorService executor;
    private final Map<String, Service> registeredServices = new ConcurrentHashMap<>();
    private final Map<String, TransactionRecord> transactions = new ConcurrentHashMap<>();
    private final List<String> logs = Collections.synchronizedList(new ArrayList<>());

    public TransactionManager(long timeoutMillis, int maxCommitRetries) {
        this.timeoutMillis = timeoutMillis;
        this.maxCommitRetries = maxCommitRetries;
        this.executor = Executors.newCachedThreadPool();
    }

    public void registerService(String serviceName, Service service) {
        registeredServices.put(serviceName, service);
        log("Registered service: " + serviceName);
    }

    public String begin() {
        String txId = UUID.randomUUID().toString();
        TransactionRecord record = new TransactionRecord(txId, registeredServices.keySet());
        transactions.put(txId, record);
        log("Transaction " + txId + " begun with services: " + registeredServices.keySet());
        return txId;
    }

    public boolean commitTransaction(String txId) {
        TransactionRecord record = transactions.get(txId);
        if (record == null) {
            log("Transaction " + txId + " not found.");
            return false;
        }
        if (record.status.get() == TransactionStatus.COMMITTED) {
            log("Transaction " + txId + " already committed.");
            return true;
        }
        if (record.status.get() == TransactionStatus.ROLLEDBACK) {
            log("Transaction " + txId + " already rolled back.");
            return false;
        }
        // Phase 1: Prepare
        boolean prepared = preparePhase(txId, record);
        if (!prepared) {
            rollbackTransaction(txId);
            record.status.set(TransactionStatus.FAILED);
            log("Transaction " + txId + " prepare phase failed, rolled back.");
            return false;
        }
        // Phase 2: Commit
        boolean committed = commitPhase(txId, record);
        if (!committed) {
            rollbackTransaction(txId);
            record.status.set(TransactionStatus.FAILED);
            log("Transaction " + txId + " commit phase failed after retries, rolled back.");
            return false;
        }
        record.status.set(TransactionStatus.COMMITTED);
        log("Transaction " + txId + " successfully committed.");
        return true;
    }

    public void rollbackTransaction(String txId) {
        TransactionRecord record = transactions.get(txId);
        if (record == null) {
            log("Transaction " + txId + " not found for rollback.");
            return;
        }
        if (record.status.get() == TransactionStatus.ROLLEDBACK) {
            log("Transaction " + txId + " already rolled back.");
            return;
        }
        for (String serviceName : record.servicesParticipated) {
            Service service = registeredServices.get(serviceName);
            final String sName = serviceName;
            try {
                Future<Void> future = executor.submit(() -> {
                    service.rollback(txId);
                    log("Service " + sName + " rolled back for transaction " + txId);
                    return null;
                });
                future.get(timeoutMillis, TimeUnit.MILLISECONDS);
            } catch (Exception e) {
                log("Service " + sName + " rollback error for transaction " + txId + ": " + e.getMessage());
            }
        }
        record.status.set(TransactionStatus.ROLLEDBACK);
        log("Transaction " + txId + " marked as rolled back.");
    }

    private boolean preparePhase(String txId, TransactionRecord record) {
        CountDownLatch latch = new CountDownLatch(record.servicesParticipated.size());
        ConcurrentMap<String, Boolean> prepareResults = new ConcurrentHashMap<>();

        for (String serviceName : record.servicesParticipated) {
            Service service = registeredServices.get(serviceName);
            final String sName = serviceName;
            executor.submit(() -> {
                try {
                    Future<Boolean> future = executor.submit(() -> service.prepare(txId));
                    Boolean result = future.get(timeoutMillis, TimeUnit.MILLISECONDS);
                    prepareResults.put(sName, result);
                    log("Service " + sName + " prepare result for transaction " + txId + ": " + result);
                } catch (Exception e) {
                    prepareResults.put(sName, false);
                    log("Service " + sName + " prepare exception for transaction " + txId + ": " + e.getMessage());
                } finally {
                    latch.countDown();
                }
            });
        }
        try {
            boolean finished = latch.await(timeoutMillis, TimeUnit.MILLISECONDS);
            if (!finished) {
                log("Timeout waiting for prepare phase in transaction " + txId);
                return false;
            }
        } catch (InterruptedException e) {
            log("Prepare phase interrupted for transaction " + txId);
            return false;
        }
        for (String serviceName : record.servicesParticipated) {
            if (!Boolean.TRUE.equals(prepareResults.get(serviceName))) {
                return false;
            }
        }
        record.preparedServices.addAll(record.servicesParticipated);
        record.status.set(TransactionStatus.PREPARED);
        return true;
    }

    private boolean commitPhase(String txId, TransactionRecord record) {
        for (String serviceName : record.servicesParticipated) {
            Service service = registeredServices.get(serviceName);
            final String sName = serviceName;
            int attempt = 0;
            boolean committed = false;
            while (attempt <= maxCommitRetries && !committed) {
                try {
                    Future<Void> future = executor.submit(() -> {
                        service.commit(txId);
                        return null;
                    });
                    future.get(timeoutMillis, TimeUnit.MILLISECONDS);
                    committed = true;
                    log("Service " + sName + " committed on attempt " + (attempt + 1) + " for transaction " + txId);
                    record.committedServices.add(sName);
                } catch (Exception e) {
                    attempt++;
                    log("Service " + sName + " commit failed on attempt " + attempt + " for transaction " + txId + ": " + e.getMessage());
                    try {
                        Thread.sleep(100 * (1 << attempt));
                    } catch (InterruptedException ie) {
                        Thread.currentThread().interrupt();
                        return false;
                    }
                }
            }
            if (!committed) {
                return false;
            }
        }
        return true;
    }

    private void log(String message) {
        String logEntry = "[" + System.currentTimeMillis() + "] " + message;
        logs.add(logEntry);
        System.out.println(logEntry);
    }

    public List<String> getLogs() {
        return logs;
    }

    private enum TransactionStatus {
        STARTED,
        PREPARED,
        COMMITTED,
        ROLLEDBACK,
        FAILED
    }

    private static class TransactionRecord {
        final String transactionId;
        final Set<String> servicesParticipated;
        final Set<String> preparedServices = ConcurrentHashMap.newKeySet();
        final Set<String> committedServices = ConcurrentHashMap.newKeySet();
        final AtomicReference<TransactionStatus> status = new AtomicReference<>(TransactionStatus.STARTED);

        TransactionRecord(String transactionId, Set<String> servicesParticipated) {
            this.transactionId = transactionId;
            this.servicesParticipated = new HashSet<>(servicesParticipated);
        }
    }
}