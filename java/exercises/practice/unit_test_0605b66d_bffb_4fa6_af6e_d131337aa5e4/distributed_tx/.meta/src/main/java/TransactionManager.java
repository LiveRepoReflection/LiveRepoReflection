package distributed_tx;

import java.util.List;
import java.util.ArrayList;
import java.util.concurrent.Executors;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.concurrent.Callable;
import java.util.logging.Logger;

public class TransactionManager {
    private static final Logger LOGGER = Logger.getLogger(TransactionManager.class.getName());
    private static final long PREPARE_TIMEOUT_SEC = 5;

    public boolean executeTransaction(List<Service> services) {
        TransactionContext tx = new TransactionContext();
        ExecutorService executor = Executors.newFixedThreadPool(services.size());
        List<Future<Boolean>> prepareFutures = new ArrayList<>();
        boolean prepareSuccess = true;

        try {
            // Initiate prepare phase concurrently.
            for (Service service : services) {
                Callable<Boolean> task = () -> {
                    try {
                        return service.prepare(tx);
                    } catch (Exception e) {
                        LOGGER.severe("Exception during prepare in service " + service + ": " + e.getMessage());
                        throw e;
                    }
                };
                prepareFutures.add(executor.submit(task));
            }

            // Wait for all prepare tasks to complete and check their results.
            for (Future<Boolean> future : prepareFutures) {
                try {
                    boolean servicePrepared = future.get(PREPARE_TIMEOUT_SEC, TimeUnit.SECONDS);
                    if (!servicePrepared) {
                        prepareSuccess = false;
                    }
                } catch (TimeoutException e) {
                    LOGGER.severe("Prepare phase timed out: " + e.getMessage());
                    prepareSuccess = false;
                } catch (Exception e) {
                    LOGGER.severe("Exception during prepare phase: " + e.getMessage());
                    prepareSuccess = false;
                }
            }

            if (prepareSuccess) {
                // Initiate commit concurrently if prepare phase was successful.
                List<Future<?>> commitFutures = new ArrayList<>();
                for (Service service : services) {
                    Runnable commitTask = () -> {
                        try {
                            service.commit(tx);
                        } catch (Exception e) {
                            LOGGER.severe("Exception during commit: " + e.getMessage());
                        }
                    };
                    commitFutures.add(executor.submit(commitTask));
                }
                // Wait for all commit operations to finish.
                for (Future<?> future : commitFutures) {
                    try {
                        future.get();
                    } catch (Exception e) {
                        LOGGER.severe("Exception while waiting for commit to finish: " + e.getMessage());
                    }
                }
                return true;
            } else {
                // Initiate rollback concurrently if any prepare failed.
                List<Future<?>> rollbackFutures = new ArrayList<>();
                for (Service service : services) {
                    Runnable rollbackTask = () -> {
                        try {
                            service.rollback(tx);
                        } catch (Exception e) {
                            LOGGER.severe("Exception during rollback: " + e.getMessage());
                        }
                    };
                    rollbackFutures.add(executor.submit(rollbackTask));
                }
                // Wait for all rollback operations to finish.
                for (Future<?> future : rollbackFutures) {
                    try {
                        future.get();
                    } catch (Exception e) {
                        LOGGER.severe("Exception while waiting for rollback to finish: " + e.getMessage());
                    }
                }
                return false;
            }
        } finally {
            executor.shutdownNow();
        }
    }
}