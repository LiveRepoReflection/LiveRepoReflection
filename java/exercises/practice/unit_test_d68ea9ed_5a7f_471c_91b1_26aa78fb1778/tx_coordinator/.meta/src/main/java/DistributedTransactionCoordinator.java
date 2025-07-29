package tx_coordinator;

import java.util.UUID;
import java.util.List;
import java.util.ArrayList;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Executors;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Callable;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

public class DistributedTransactionCoordinator {

    private enum TransactionStatus {
        ACTIVE,
        COMMITTED,
        ROLLED_BACK
    }

    private static class Enlistment {
        final Service service;
        final String data;

        Enlistment(Service service, String data) {
            this.service = service;
            this.data = data;
        }
    }

    private static class Transaction {
        final String txId;
        final List<Enlistment> enlistments = new ArrayList<>();
        TransactionStatus status = TransactionStatus.ACTIVE;

        Transaction(String txId) {
            this.txId = txId;
        }
    }

    // Map of transaction id to Transaction object
    private final Map<String, Transaction> transactions = new ConcurrentHashMap<>();

    // Executor for parallel execution
    private final ExecutorService executor = Executors.newCachedThreadPool();

    // Timeout duration in milliseconds for prepare, commit and rollback operations
    private static final long TIMEOUT_MS = 1000;

    /**
     * Begins a new transaction and returns the unique transaction ID.
     */
    public String begin() {
        String txId = UUID.randomUUID().toString();
        Transaction tx = new Transaction(txId);
        transactions.put(txId, tx);
        return txId;
    }

    /**
     * Enlists a new service into the transaction.
     */
    public void enlist(String transactionId, Service service, String data) {
        Transaction tx = transactions.get(transactionId);
        if (tx == null) {
            throw new IllegalArgumentException("Transaction " + transactionId + " does not exist.");
        }
        synchronized (tx) {
            if (tx.status != TransactionStatus.ACTIVE) {
                throw new IllegalStateException("Cannot enlist service to non-active transaction " + transactionId);
            }
            tx.enlistments.add(new Enlistment(service, data));
        }
    }

    /**
     * Attempts to commit the transaction.
     * Performs prepare phase for all enlisted services, then commit or rollback accordingly.
     */
    public void commit(String transactionId) {
        Transaction tx = transactions.get(transactionId);
        if (tx == null) {
            throw new IllegalArgumentException("Transaction " + transactionId + " does not exist.");
        }
        synchronized (tx) {
            if (tx.status != TransactionStatus.ACTIVE) {
                // Idempotency: if already committed or rolled back, do nothing.
                return;
            }
            boolean prepareSuccess = true;
            List<Future<Boolean>> prepareFutures = new ArrayList<>();
            // Prepare Phase
            for (Enlistment en : tx.enlistments) {
                Callable<Boolean> task = () -> {
                    try {
                        return en.service.prepare(transactionId, en.data);
                    } catch (Exception e) {
                        return false;
                    }
                };
                Future<Boolean> future = executor.submit(task);
                prepareFutures.add(future);
            }

            for (Future<Boolean> future : prepareFutures) {
                try {
                    Boolean result = future.get(TIMEOUT_MS, TimeUnit.MILLISECONDS);
                    if (!result) {
                        prepareSuccess = false;
                        break;
                    }
                } catch (TimeoutException te) {
                    prepareSuccess = false;
                    break;
                } catch (Exception e) {
                    prepareSuccess = false;
                    break;
                }
            }

            if (!prepareSuccess) {
                // Log rollback initiation in the coordinator.
                System.out.println("Coordinator: Prepare phase failed. Initiating rollback for transaction " + transactionId);
                performRollback(tx);
                tx.status = TransactionStatus.ROLLED_BACK;
                return;
            }

            // Commit Phase
            List<Future<?>> commitFutures = new ArrayList<>();
            for (Enlistment en : tx.enlistments) {
                Callable<Void> task = () -> {
                    try {
                        en.service.commit(transactionId);
                        // Log each commit
                        System.out.println("Coordinator: Committed " + en.service.getName() + " for transaction " + transactionId);
                    } catch (Exception e) {
                        // Even if commit fails we log and continue since commit() is idempotent.
                        System.out.println("Coordinator: Exception during commit for " + en.service.getName() + " transaction " + transactionId);
                    }
                    return null;
                };
                Future<?> future = executor.submit(task);
                commitFutures.add(future);
            }
            // Await commit tasks to complete
            for (Future<?> future : commitFutures) {
                try {
                    future.get(TIMEOUT_MS, TimeUnit.MILLISECONDS);
                } catch (Exception e) {
                    // If commit fails due to timeout or exception, we still mark it as committed because of idempotency.
                    System.out.println("Coordinator: Commit timeout/exception in transaction " + transactionId);
                }
            }
            tx.status = TransactionStatus.COMMITTED;
        }
    }

    /**
     * Rolls back the transaction by calling rollback on each enlisted service.
     */
    public void rollback(String transactionId) {
        Transaction tx = transactions.get(transactionId);
        if (tx == null) {
            throw new IllegalArgumentException("Transaction " + transactionId + " does not exist.");
        }
        synchronized (tx) {
            if (tx.status == TransactionStatus.ROLLED_BACK || tx.status == TransactionStatus.COMMITTED) {
                // Idempotency: if already rolled back or committed, do nothing.
                return;
            }
            performRollback(tx);
            tx.status = TransactionStatus.ROLLED_BACK;
        }
    }

    /**
     * Helper method to perform rollback on all enlisted services concurrently.
     */
    private void performRollback(Transaction tx) {
        List<Future<?>> rollbackFutures = new ArrayList<>();
        for (Enlistment en : tx.enlistments) {
            Callable<Void> task = () -> {
                try {
                    en.service.rollback(tx.txId);
                    // Log each rollback
                    System.out.println("Coordinator: Rolled back " + en.service.getName() + " for transaction " + tx.txId);
                } catch (Exception e) {
                    System.out.println("Coordinator: Exception during rollback for " + en.service.getName() + " transaction " + tx.txId);
                }
                return null;
            };
            Future<?> future = executor.submit(task);
            rollbackFutures.add(future);
        }
        for (Future<?> future : rollbackFutures) {
            try {
                future.get(TIMEOUT_MS, TimeUnit.MILLISECONDS);
            } catch (Exception e) {
                System.out.println("Coordinator: Rollback timeout/exception in transaction " + tx.txId);
            }
        }
    }

    /**
     * Returns the current status of the transaction as a String:
     * "ACTIVE", "COMMITTED", or "ROLLED_BACK"
     */
    public String getTransactionStatus(String transactionId) {
        Transaction tx = transactions.get(transactionId);
        if (tx == null) {
            throw new IllegalArgumentException("Transaction " + transactionId + " does not exist.");
        }
        synchronized (tx) {
            return tx.status.name();
        }
    }
}