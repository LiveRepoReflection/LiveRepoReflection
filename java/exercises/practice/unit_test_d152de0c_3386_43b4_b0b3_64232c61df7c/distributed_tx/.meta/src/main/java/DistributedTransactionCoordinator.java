package distributed_tx;

import java.util.*;
import java.util.concurrent.*;

public class DistributedTransactionCoordinator {

    private final long TIMEOUT_MILLIS = 1000;
    private final ExecutorService executor = Executors.newCachedThreadPool();

    // Map to hold pending transactions which simulate a crash prior to commit.
    private final ConcurrentMap<String, List<BranchService>> pendingTransactions = new ConcurrentHashMap<>();

    public TransactionStatus executeTransaction(String transactionId, List<BranchService> branches) {
        List<Future<Boolean>> prepareFutures = new ArrayList<>();
        for (BranchService branch : branches) {
            prepareFutures.add(executor.submit(() -> branch.prepare(transactionId)));
        }
        boolean allPrepared = true;
        for (Future<Boolean> future : prepareFutures) {
            try {
                Boolean result = future.get(TIMEOUT_MILLIS, TimeUnit.MILLISECONDS);
                if (!result) {
                    allPrepared = false;
                    break;
                }
            } catch (InterruptedException | ExecutionException | TimeoutException e) {
                allPrepared = false;
                break;
            }
        }
        if (!allPrepared) {
            // Rollback all branches.
            for (BranchService branch : branches) {
                try {
                    branch.rollback(transactionId);
                } catch (Exception e) {
                    // Error logging can be added here if needed.
                }
            }
            return TransactionStatus.ABORTED;
        }

        // Commit phase: commit transaction on all branches.
        List<Future<?>> commitFutures = new ArrayList<>();
        for (BranchService branch : branches) {
            commitFutures.add(executor.submit(() -> branch.commit(transactionId)));
        }
        boolean commitSuccessful = true;
        for (Future<?> future : commitFutures) {
            try {
                future.get(TIMEOUT_MILLIS, TimeUnit.MILLISECONDS);
            } catch (InterruptedException | ExecutionException | TimeoutException e) {
                commitSuccessful = false;
                break;
            }
        }
        if (!commitSuccessful) {
            for (BranchService branch : branches) {
                try {
                    branch.rollback(transactionId);
                } catch (Exception e) {
                    // Error logging can be added here if needed.
                }
            }
            return TransactionStatus.ABORTED;
        }
        return TransactionStatus.COMMITTED;
    }

    public void simulateCrashDuringCommit(String transactionId, List<BranchService> branches) {
        List<Future<Boolean>> prepareFutures = new ArrayList<>();
        for (BranchService branch : branches) {
            prepareFutures.add(executor.submit(() -> branch.prepare(transactionId)));
        }
        boolean allPrepared = true;
        for (Future<Boolean> future : prepareFutures) {
            try {
                Boolean result = future.get(TIMEOUT_MILLIS, TimeUnit.MILLISECONDS);
                if (!result) {
                    allPrepared = false;
                    break;
                }
            } catch (InterruptedException | ExecutionException | TimeoutException e) {
                allPrepared = false;
                break;
            }
        }
        if (!allPrepared) {
            for (BranchService branch : branches) {
                try {
                    branch.rollback(transactionId);
                } catch (Exception e) {
                    // Error logging can be added here if needed.
                }
            }
        } else {
            // Simulate a crash by not performing the commit but storing the transaction state.
            pendingTransactions.put(transactionId, branches);
        }
    }

    public TransactionStatus recoverPendingTransactions(String transactionId) {
        List<BranchService> branches = pendingTransactions.get(transactionId);
        if (branches == null) {
            // No pending transaction found. Assume it was already committed.
            return TransactionStatus.COMMITTED;
        }
        List<Future<?>> commitFutures = new ArrayList<>();
        for (BranchService branch : branches) {
            commitFutures.add(executor.submit(() -> branch.commit(transactionId)));
        }
        boolean commitSuccessful = true;
        for (Future<?> future : commitFutures) {
            try {
                future.get(TIMEOUT_MILLIS, TimeUnit.MILLISECONDS);
            } catch (InterruptedException | ExecutionException | TimeoutException e) {
                commitSuccessful = false;
                break;
            }
        }
        pendingTransactions.remove(transactionId);
        if (!commitSuccessful) {
            for (BranchService branch : branches) {
                try {
                    branch.rollback(transactionId);
                } catch (Exception e) {
                    // Error logging can be added here if needed.
                }
            }
            return TransactionStatus.ABORTED;
        }
        return TransactionStatus.COMMITTED;
    }
}