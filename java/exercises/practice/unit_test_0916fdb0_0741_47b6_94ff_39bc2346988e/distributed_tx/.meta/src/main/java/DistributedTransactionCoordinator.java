package distributed_tx;

import java.util.*;
import java.util.concurrent.*;

public class DistributedTransactionCoordinator {

    private final long timeoutMillis;
    private final ConcurrentMap<UUID, LogEntry> log = new ConcurrentHashMap<>();
    private final ExecutorService executor;

    public DistributedTransactionCoordinator(long timeoutMillis) {
        this.timeoutMillis = timeoutMillis;
        this.executor = Executors.newCachedThreadPool();
    }

    public boolean executeTransaction(UUID transactionId, List<Service> services) {
        List<Future<Boolean>> futures = new ArrayList<>();
        List<String> serviceIds = new ArrayList<>();
        for (Service service : services) {
            serviceIds.add(service.toString());
            Callable<Boolean> task = () -> service.prepare(transactionId);
            Future<Boolean> future = executor.submit(task);
            futures.add(future);
        }

        boolean allPrepared = true;
        for (Future<Boolean> future : futures) {
            try {
                boolean prepared = future.get(timeoutMillis, TimeUnit.MILLISECONDS);
                if (!prepared) {
                    allPrepared = false;
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                allPrepared = false;
            } catch (ExecutionException e) {
                allPrepared = false;
            } catch (TimeoutException e) {
                allPrepared = false;
            }
        }

        if (allPrepared) {
            for (Service service : services) {
                try {
                    service.commit(transactionId);
                } catch (Exception e) {
                    // Commit failures in idempotent operations are ignored.
                }
            }
            log.put(transactionId, new LogEntry(transactionId, "COMMIT", serviceIds));
            return true;
        } else {
            for (Service service : services) {
                try {
                    service.rollback(transactionId);
                } catch (Exception e) {
                    // Rollback failures in idempotent operations are ignored.
                }
            }
            log.put(transactionId, new LogEntry(transactionId, "ROLLBACK", serviceIds));
            return false;
        }
    }

    public LogEntry getLogEntry(UUID transactionId) {
        return log.get(transactionId);
    }

    public void shutdown() {
        executor.shutdown();
    }
}