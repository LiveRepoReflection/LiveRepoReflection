import java.util.*;
import java.util.concurrent.Callable;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

public class TransactionCoordinator {

    private final ConcurrentHashMap<String, TransactionContext> transactions = new ConcurrentHashMap<>();
    private final AtomicInteger transactionCounter = new AtomicInteger(0);
    private static final int MAX_RETRIES = 3;
    private static final long INITIAL_BACKOFF_MS = 100;

    private class TransactionContext {
        TransactionStatus status;
        List<EnlistedService> enlistedServices;

        TransactionContext() {
            this.status = TransactionStatus.PENDING;
            this.enlistedServices = new ArrayList<>();
        }
    }

    private class EnlistedService {
        BankService service;
        List<Operation> operations;

        EnlistedService(BankService service, List<Operation> operations) {
            this.service = service;
            this.operations = operations;
        }
    }

    public String begin() {
        String txnId = "TXN-" + transactionCounter.getAndIncrement();
        TransactionContext context = new TransactionContext();
        transactions.put(txnId, context);
        System.out.println("Transaction " + txnId + " started.");
        return txnId;
    }

    public void enlist(String transactionId, BankService service, java.util.List<Operation> operations) {
        TransactionContext context = transactions.get(transactionId);
        if (context == null) {
            throw new IllegalArgumentException("Transaction ID not found: " + transactionId);
        }
        synchronized (context) {
            context.enlistedServices.add(new EnlistedService(service, operations));
            System.out.println("Enlisted service for transaction " + transactionId);
        }
    }

    public void commit(String transactionId) {
        TransactionContext context = transactions.get(transactionId);
        if (context == null) {
            throw new IllegalArgumentException("Transaction ID not found: " + transactionId);
        }
        synchronized (context) {
            if (context.enlistedServices.isEmpty()) {
                context.status = TransactionStatus.COMMITTED;
                System.out.println("Transaction " + transactionId + " committed (empty transaction).");
                return;
            }

            // Phase 1: Prepare
            boolean prepareSuccess = true;
            for (EnlistedService enlisted : context.enlistedServices) {
                boolean result = retryOperation(() -> enlisted.service.prepare(transactionId, enlisted.operations));
                if (!result) {
                    prepareSuccess = false;
                    System.out.println("Service failed to prepare for transaction " + transactionId);
                    break;
                } else {
                    System.out.println("Service prepared for transaction " + transactionId);
                }
            }

            // If any prepare fails, rollback the transaction.
            if (!prepareSuccess) {
                System.out.println("Transaction " + transactionId + " prepare phase failed. Initiating rollback.");
                rollbackInternal(transactionId, context);
                context.status = TransactionStatus.ABORTED;
                return;
            }

            // Phase 2: Commit
            boolean commitSuccess = true;
            for (EnlistedService enlisted : context.enlistedServices) {
                boolean result = retryOperation(() -> enlisted.service.commit(transactionId));
                if (!result) {
                    commitSuccess = false;
                    System.out.println("Service failed to commit for transaction " + transactionId);
                    break;
                } else {
                    System.out.println("Service committed for transaction " + transactionId);
                }
            }

            if (!commitSuccess) {
                System.out.println("Transaction " + transactionId + " commit phase failed. Initiating rollback.");
                rollbackInternal(transactionId, context);
                context.status = TransactionStatus.ABORTED;
            } else {
                context.status = TransactionStatus.COMMITTED;
                System.out.println("Transaction " + transactionId + " committed successfully.");
            }
        }
    }

    public void rollback(String transactionId) {
        TransactionContext context = transactions.get(transactionId);
        if (context == null) {
            throw new IllegalArgumentException("Transaction ID not found: " + transactionId);
        }
        synchronized (context) {
            rollbackInternal(transactionId, context);
            context.status = TransactionStatus.ABORTED;
            System.out.println("Transaction " + transactionId + " rolled back explicitly.");
        }
    }

    private void rollbackInternal(String transactionId, TransactionContext context) {
        for (EnlistedService enlisted : context.enlistedServices) {
            boolean result = retryOperation(() -> enlisted.service.rollback(transactionId));
            if (result) {
                System.out.println("Service rolled back for transaction " + transactionId);
            } else {
                System.out.println("Service failed to rollback for transaction " + transactionId);
            }
        }
    }

    public TransactionStatus getTransactionStatus(String transactionId) {
        TransactionContext context = transactions.get(transactionId);
        if (context == null) {
            throw new IllegalArgumentException("Transaction ID not found: " + transactionId);
        }
        return context.status;
    }

    private boolean retryOperation(Callable<Boolean> operation) {
        int attempt = 0;
        long backoff = INITIAL_BACKOFF_MS;
        while (attempt < MAX_RETRIES) {
            try {
                if (operation.call()) {
                    return true;
                }
            } catch (Exception e) {
                System.out.println("Operation threw exception: " + e.getMessage());
            }
            try {
                Thread.sleep(backoff);
            } catch (InterruptedException ie) {
                Thread.currentThread().interrupt();
                return false;
            }
            backoff *= 2;
            attempt++;
        }
        return false;
    }
}