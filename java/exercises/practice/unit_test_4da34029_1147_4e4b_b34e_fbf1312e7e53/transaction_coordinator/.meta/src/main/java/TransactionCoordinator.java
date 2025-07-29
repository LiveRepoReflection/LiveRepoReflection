package transaction_coordinator;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

public class TransactionCoordinator {

    private static final long PREPARE_TIMEOUT_MILLIS = 2000;
    private static final long COMMIT_TIMEOUT_MILLIS = 2000;
    private final ExecutorService executor = Executors.newCachedThreadPool();
    private final ConcurrentMap<String, Transaction> transactions = new ConcurrentHashMap<>();

    private enum TransactionState {
        INIT,
        PREPARED,
        COMMITTED,
        ROLLED_BACK
    }

    private static class Transaction {
        final String transactionId;
        final List<BankingService> services;
        volatile TransactionState state;
        final List<String> operations;

        Transaction(String transactionId, List<BankingService> services) {
            this.transactionId = transactionId;
            this.services = services;
            this.state = TransactionState.INIT;
            this.operations = new ArrayList<>();
        }
    }

    public String beginTransaction(List<BankingService> services) {
        String txnId = UUID.randomUUID().toString();
        Transaction txn = new Transaction(txnId, services);
        transactions.put(txnId, txn);
        // Here, implement persistence if needed.
        return txnId;
    }

    public void performOperation(String transactionId, String operationDetails) throws IllegalArgumentException {
        Transaction txn = transactions.get(transactionId);
        if (txn == null) {
            throw new IllegalArgumentException("Transaction not found: " + transactionId);
        }
        // Simulate performing an operation. In real scenarios, record the operation and update the system.
        txn.operations.add(operationDetails);
    }

    public void commitTransaction(String transactionId) throws TransactionFailureException, TransactionTimeoutException {
        Transaction txn = transactions.get(transactionId);
        if (txn == null) {
            throw new IllegalArgumentException("Transaction not found: " + transactionId);
        }
        if (txn.services.isEmpty()) {
            txn.state = TransactionState.COMMITTED;
            return;
        }

        // Phase 1: Prepare
        List<Future<Boolean>> prepareFutures = new ArrayList<>();
        for (BankingService service : txn.services) {
            Callable<Boolean> task = () -> service.prepare(transactionId);
            Future<Boolean> future = executor.submit(task);
            prepareFutures.add(future);
        }

        AtomicInteger successCount = new AtomicInteger(0);
        for (Future<Boolean> future : prepareFutures) {
            try {
                boolean prepared = future.get(PREPARE_TIMEOUT_MILLIS, TimeUnit.MILLISECONDS);
                if (prepared) {
                    successCount.incrementAndGet();
                } else {
                    rollbackTransaction(transactionId);
                    txn.state = TransactionState.ROLLED_BACK;
                    throw new TransactionFailureException("Prepare phase failed on one of the services.");
                }
            } catch (TimeoutException e) {
                rollbackTransaction(transactionId);
                txn.state = TransactionState.ROLLED_BACK;
                throw new TransactionTimeoutException("Prepare phase timed out.");
            } catch (InterruptedException | ExecutionException e) {
                rollbackTransaction(transactionId);
                txn.state = TransactionState.ROLLED_BACK;
                throw new TransactionFailureException("Prepare phase encountered an exception: " + e.getMessage());
            }
        }

        // If not all services prepared, then fail.
        if (successCount.get() != txn.services.size()) {
            rollbackTransaction(transactionId);
            txn.state = TransactionState.ROLLED_BACK;
            throw new TransactionFailureException("Not all services prepared successfully.");
        }
        txn.state = TransactionState.PREPARED;

        // Phase 2: Commit
        List<Future<?>> commitFutures = new ArrayList<>();
        for (BankingService service : txn.services) {
            Runnable task = () -> service.commit(transactionId);
            Future<?> future = executor.submit(task);
            commitFutures.add(future);
        }

        for (Future<?> future : commitFutures) {
            try {
                future.get(COMMIT_TIMEOUT_MILLIS, TimeUnit.MILLISECONDS);
            } catch (TimeoutException e) {
                // In case of timeout during commit, best effort rollback is not possible because commit should be idempotent.
                txn.state = TransactionState.COMMITTED;
                throw new TransactionTimeoutException("Commit phase timed out.");
            } catch (InterruptedException | ExecutionException e) {
                txn.state = TransactionState.COMMITTED;
                throw new TransactionFailureException("Commit phase encountered an exception: " + e.getMessage());
            }
        }
        txn.state = TransactionState.COMMITTED;
        // Persist final state if needed.
    }

    public void rollbackTransaction(String transactionId) {
        Transaction txn = transactions.get(transactionId);
        if (txn == null) {
            throw new IllegalArgumentException("Transaction not found: " + transactionId);
        }
        List<Future<?>> rollbackFutures = new ArrayList<>();
        for (BankingService service : txn.services) {
            Runnable task = () -> service.rollback(transactionId);
            Future<?> future = executor.submit(task);
            rollbackFutures.add(future);
        }

        for (Future<?> future : rollbackFutures) {
            try {
                future.get(COMMIT_TIMEOUT_MILLIS, TimeUnit.MILLISECONDS);
            } catch (TimeoutException | InterruptedException | ExecutionException e) {
                // Suppress exceptions during rollback because rollback should be idempotent.
            }
        }
        txn.state = TransactionState.ROLLED_BACK;
        // Persist rollback state if needed.
    }
}