import java.util.*;
import java.util.concurrent.*;

public class DistributedTxCoordinator {

    private final Map<String, BankService> bankServices;
    private final ExecutorService executor;

    public DistributedTxCoordinator(Map<String, BankService> bankServices) {
        this.bankServices = bankServices;
        // Using a cached thread pool for parallel execution.
        this.executor = Executors.newCachedThreadPool();
    }

    public boolean executeTransaction(String transactionId, List<TransactionOperation> operations) {
        // Filter out read-only operations: they don't participate in the 2PC protocol.
        List<TransactionOperation> nonReadOnlyOps = new ArrayList<>();
        for (TransactionOperation op : operations) {
            if (!op.readOnly) {
                nonReadOnlyOps.add(op);
            } else {
                // Read-only optimization: simply log and skip.
                System.out.println("Transaction " + transactionId + " - readOnly operation on bank: " + op.bankId);
            }
        }

        // Phase 1: Prepare phase in parallel.
        Map<TransactionOperation, Future<Boolean>> prepareFutures = new HashMap<>();
        for (TransactionOperation op : nonReadOnlyOps) {
            BankService bank = bankServices.get(op.bankId);
            if (bank == null) {
                System.out.println("Transaction " + transactionId + " - bank service not found for bankId: " + op.bankId);
                rollbackOperations(transactionId, prepareFutures, nonReadOnlyOps);
                return false;
            }
            Future<Boolean> future = executor.submit(() -> {
                System.out.println("Transaction " + transactionId + " - preparing on bank: " + op.bankId + ", account: " + op.accountId);
                return bank.prepare(transactionId, op.accountId, op.amount);
            });
            prepareFutures.put(op, future);
        }

        // Collect prepare results.
        List<TransactionOperation> preparedOps = new ArrayList<>();
        for (Map.Entry<TransactionOperation, Future<Boolean>> entry : prepareFutures.entrySet()) {
            try {
                boolean prepareResult = entry.getValue().get();
                if (!prepareResult) {
                    System.out.println("Transaction " + transactionId + " - prepare failed on bank: " + entry.getKey().bankId);
                    rollbackOperations(transactionId, preparedOps);
                    return false;
                }
                preparedOps.add(entry.getKey());
            } catch (InterruptedException | ExecutionException e) {
                System.out.println("Transaction " + transactionId + " - exception during prepare on bank: " + entry.getKey().bankId);
                rollbackOperations(transactionId, preparedOps);
                return false;
            }
        }

        // Phase 2: Commit phase in parallel.
        Map<TransactionOperation, Future<Boolean>> commitFutures = new HashMap<>();
        for (TransactionOperation op : preparedOps) {
            BankService bank = bankServices.get(op.bankId);
            Future<Boolean> future = executor.submit(() -> {
                System.out.println("Transaction " + transactionId + " - committing on bank: " + op.bankId + ", account: " + op.accountId);
                return bank.commit(transactionId, op.accountId, op.amount);
            });
            commitFutures.put(op, future);
        }

        // Verify commit results.
        for (Map.Entry<TransactionOperation, Future<Boolean>> entry : commitFutures.entrySet()) {
            try {
                boolean commitResult = entry.getValue().get();
                if (!commitResult) {
                    System.out.println("Transaction " + transactionId + " - commit failed on bank: " + entry.getKey().bankId);
                    rollbackOperations(transactionId, preparedOps);
                    return false;
                }
            } catch (InterruptedException | ExecutionException e) {
                System.out.println("Transaction " + transactionId + " - exception during commit on bank: " + entry.getKey().bankId);
                rollbackOperations(transactionId, preparedOps);
                return false;
            }
        }

        System.out.println("Transaction " + transactionId + " - committed successfully");
        return true;
    }

    private void rollbackOperations(String transactionId, List<TransactionOperation> operations) {
        // Rollback in parallel.
        List<Future<Boolean>> rollbackFutures = new ArrayList<>();
        for (TransactionOperation op : operations) {
            BankService bank = bankServices.get(op.bankId);
            Future<Boolean> future = executor.submit(() -> {
                System.out.println("Transaction " + transactionId + " - rolling back on bank: " + op.bankId + ", account: " + op.accountId);
                return bank.rollback(transactionId, op.accountId, op.amount);
            });
            rollbackFutures.add(future);
        }
        for (Future<Boolean> future : rollbackFutures) {
            try {
                future.get();
            } catch (InterruptedException | ExecutionException e) {
                System.out.println("Transaction " + transactionId + " - exception during rollback");
            }
        }
        System.out.println("Transaction " + transactionId + " - rollback completed");
    }

    private void rollbackOperations(String transactionId, Map<TransactionOperation, Future<Boolean>> futures, List<TransactionOperation> allOps) {
        List<TransactionOperation> opsToRollback = new ArrayList<>();
        for (TransactionOperation op : allOps) {
            try {
                Future<Boolean> future = futures.get(op);
                if (future != null && future.isDone() && future.get()) {
                    opsToRollback.add(op);
                }
            } catch (Exception e) {
                // If the operation did not complete, skip rollback.
            }
        }
        rollbackOperations(transactionId, opsToRollback);
    }
}