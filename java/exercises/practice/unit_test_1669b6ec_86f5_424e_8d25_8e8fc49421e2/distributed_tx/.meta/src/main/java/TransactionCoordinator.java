package distributed_tx;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.logging.Level;
import java.util.logging.Logger;

public class TransactionCoordinator {
    private static final Logger logger = Logger.getLogger(TransactionCoordinator.class.getName());
    private final ConcurrentMap<Integer, List<Microservice>> transactions;
    private final AtomicInteger txIdGenerator;
    private final ExecutorService executor;
    private final long timeoutMillis;

    public TransactionCoordinator() {
        // Default timeout of 5000 milliseconds.
        this(5000);
    }

    public TransactionCoordinator(long timeoutMillis) {
        this.transactions = new ConcurrentHashMap<>();
        this.txIdGenerator = new AtomicInteger(1);
        this.executor = Executors.newCachedThreadPool();
        this.timeoutMillis = timeoutMillis;
    }

    public int begin() {
        int txId = txIdGenerator.getAndIncrement();
        transactions.put(txId, Collections.synchronizedList(new ArrayList<>()));
        logger.info("Transaction started: " + txId);
        return txId;
    }

    public void enlist(int transactionId, Microservice microservice) {
        List<Microservice> services = transactions.get(transactionId);
        if (services == null) {
            throw new IllegalArgumentException("Transaction ID not found: " + transactionId);
        }
        services.add(microservice);
        logger.info("Microservice enlisted in transaction: " + transactionId);
    }

    public boolean commit(int transactionId) {
        List<Microservice> services = transactions.get(transactionId);
        if (services == null) {
            logger.warning("Transaction ID not found during commit: " + transactionId);
            throw new IllegalArgumentException("Transaction ID not found: " + transactionId);
        }
        logger.info("Commit initiated for transaction: " + transactionId);

        List<Future<Boolean>> prepareFutures = new ArrayList<>();
        // Execute prepare calls concurrently.
        for (Microservice service : services) {
            Future<Boolean> future = executor.submit(() -> {
                try {
                    boolean result = service.prepare(transactionId);
                    logger.info("Microservice prepare result for tx " + transactionId + ": " + result);
                    return result;
                } catch (Exception e) {
                    logger.log(Level.SEVERE, "Exception during prepare in tx " + transactionId, e);
                    return false;
                }
            });
            prepareFutures.add(future);
        }

        boolean prepareSuccess = true;
        for (Future<Boolean> future : prepareFutures) {
            try {
                boolean result = future.get(timeoutMillis, TimeUnit.MILLISECONDS);
                if (!result) {
                    prepareSuccess = false;
                }
            } catch (TimeoutException e) {
                prepareSuccess = false;
                logger.log(Level.SEVERE, "Timeout during prepare for tx " + transactionId, e);
            } catch (Exception e) {
                prepareSuccess = false;
                logger.log(Level.SEVERE, "Exception during prepare for tx " + transactionId, e);
            }
        }

        if (prepareSuccess) {
            logger.info("All prepares successful for tx " + transactionId + ". Committing transaction.");
            for (Microservice service : services) {
                try {
                    service.commit(transactionId);
                    logger.info("Microservice commit successful for tx " + transactionId);
                } catch (Exception e) {
                    logger.log(Level.SEVERE, "Exception during commit for tx " + transactionId, e);
                    prepareSuccess = false;
                }
            }
            if (!prepareSuccess) {
                rollback(transactionId);
                logger.info("Commit failed; transaction rolled back for tx " + transactionId);
            }
        } else {
            logger.info("Prepare phase failed for tx " + transactionId + ". Rolling back transaction.");
            rollback(transactionId);
        }

        transactions.remove(transactionId);
        logger.info("Transaction completed and removed: " + transactionId);
        return prepareSuccess;
    }

    public boolean rollback(int transactionId) {
        List<Microservice> services = transactions.get(transactionId);
        if (services == null) {
            logger.warning("Transaction ID not found during rollback: " + transactionId);
            throw new IllegalArgumentException("Transaction ID not found: " + transactionId);
        }
        logger.info("Rollback initiated for transaction: " + transactionId);
        boolean allRollbackSuccess = true;
        for (Microservice service : services) {
            try {
                service.rollback(transactionId);
                logger.info("Microservice rollback successful for tx " + transactionId);
            } catch (Exception e) {
                allRollbackSuccess = false;
                logger.log(Level.SEVERE, "Exception during rollback for tx " + transactionId, e);
            }
        }
        transactions.remove(transactionId);
        logger.info("Transaction rolled back and removed: " + transactionId);
        return allRollbackSuccess;
    }
}