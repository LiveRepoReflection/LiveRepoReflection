import java.util.List;
import java.util.concurrent.*;
import java.util.logging.Logger;

public class DistributedTx {
    private static final Logger logger = Logger.getLogger(DistributedTx.class.getName());
    private static final int MAX_COMMIT_RETRIES = 3;
    private final ExecutorService executor;

    public DistributedTx() {
        this.executor = Executors.newCachedThreadPool();
    }

    public boolean transact(List<Service> services) {
        if (services == null || services.isEmpty()) {
            return true;
        }

        // Phase 1: Prepare
        boolean prepareSuccess = preparePhase(services);
        if (!prepareSuccess) {
            logger.warning("Transaction aborted during prepare phase");
            return false;
        }

        // Phase 2: Commit
        boolean commitSuccess = commitPhase(services);
        if (!commitSuccess) {
            logger.warning("Transaction partially committed - some services failed to commit");
            return false;
        }

        return true;
    }

    private boolean preparePhase(List<Service> services) {
        try {
            List<Future<Boolean>> futures = executor.invokeAll(services.stream()
                    .map(service -> (Callable<Boolean>) () -> {
                        try {
                            return service.prepare();
                        } catch (Exception e) {
                            logger.warning("Prepare failed for service: " + e.getMessage());
                            return false;
                        }
                    })
                    .toList());

            for (Future<Boolean> future : futures) {
                if (!future.get()) {
                    return false;
                }
            }
            return true;
        } catch (InterruptedException | ExecutionException e) {
            logger.severe("Error during prepare phase: " + e.getMessage());
            return false;
        }
    }

    private boolean commitPhase(List<Service> services) {
        boolean allCommitted = true;
        
        for (Service service : services) {
            boolean committed = false;
            int retryCount = 0;
            
            while (!committed && retryCount < MAX_COMMIT_RETRIES) {
                try {
                    committed = service.commit();
                    if (!committed) {
                        retryCount++;
                        logger.warning("Commit failed for service, retry " + retryCount);
                    }
                } catch (Exception e) {
                    retryCount++;
                    logger.warning("Commit exception for service: " + e.getMessage() + ", retry " + retryCount);
                }
            }
            
            if (!committed) {
                logger.severe("Failed to commit service after " + MAX_COMMIT_RETRIES + " retries");
                allCommitted = false;
            }
        }
        
        return allCommitted;
    }

    public void shutdown() {
        executor.shutdown();
        try {
            if (!executor.awaitTermination(5, TimeUnit.SECONDS)) {
                executor.shutdownNow();
            }
        } catch (InterruptedException e) {
            executor.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }
}