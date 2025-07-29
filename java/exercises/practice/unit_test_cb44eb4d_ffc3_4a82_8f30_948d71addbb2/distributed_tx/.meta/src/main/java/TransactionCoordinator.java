package distributed_tx;

import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.concurrent.*;

public class TransactionCoordinator {
    private final ExecutorService executor;

    public TransactionCoordinator() {
        // Cached thread pool to allow dynamic thread reuse
        this.executor = Executors.newCachedThreadPool();
    }

    public boolean executeTransaction(Transaction transaction, int timeoutMillis) {
        Set<BankServer> servers = transaction.participatingServers();
        long deadline = System.currentTimeMillis() + timeoutMillis;

        // Phase 1: Prepare phase - send prepare concurrently to all servers.
        List<Future<Boolean>> prepareFutures = new ArrayList<>();
        for (BankServer server : servers) {
            Future<Boolean> future = executor.submit(() -> {
                try {
                    return server.prepare(transaction);
                } catch (Exception e) {
                    System.err.println("Prepare error on server: " + e.getMessage());
                    return false;
                }
            });
            prepareFutures.add(future);
        }

        boolean allPrepared = true;
        for (Future<Boolean> future : prepareFutures) {
            long timeLeft = deadline - System.currentTimeMillis();
            if (timeLeft <= 0) {
                allPrepared = false;
                break;
            }
            try {
                Boolean result = future.get(timeLeft, TimeUnit.MILLISECONDS);
                if (!result) {
                    allPrepared = false;
                    break;
                }
            } catch (Exception e) {
                allPrepared = false;
                break;
            }
        }

        if (allPrepared) {
            // Phase 2: Commit phase - all prepare succeeded, so attempt commit concurrently.
            List<Future<Boolean>> commitFutures = new ArrayList<>();
            for (BankServer server : servers) {
                Future<Boolean> future = executor.submit(() -> {
                    try {
                        server.commit(transaction);
                        return true;
                    } catch (Exception e) {
                        System.err.println("Commit error on server: " + e.getMessage());
                        return false;
                    }
                });
                commitFutures.add(future);
            }
            boolean allCommitted = true;
            for (Future<Boolean> future : commitFutures) {
                long timeLeft = deadline - System.currentTimeMillis();
                if (timeLeft <= 0) {
                    allCommitted = false;
                    break;
                }
                try {
                    Boolean result = future.get(timeLeft, TimeUnit.MILLISECONDS);
                    if (!result) {
                        allCommitted = false;
                        break;
                    }
                } catch (Exception e) {
                    allCommitted = false;
                    break;
                }
            }
            if (allCommitted) {
                return true;
            }
        }

        // If not all prepared or commit failed, then perform rollback concurrently on all servers.
        List<Future<Boolean>> rollbackFutures = new ArrayList<>();
        for (BankServer server : servers) {
            Future<Boolean> future = executor.submit(() -> {
                try {
                    server.rollback(transaction);
                    return true;
                } catch (Exception e) {
                    System.err.println("Rollback error on server: " + e.getMessage());
                    return false;
                }
            });
            rollbackFutures.add(future);
        }
        boolean allRolledBack = true;
        for (Future<Boolean> future : rollbackFutures) {
            long timeLeft = deadline - System.currentTimeMillis();
            if (timeLeft <= 0) {
                allRolledBack = false;
                break;
            }
            try {
                Boolean result = future.get(timeLeft, TimeUnit.MILLISECONDS);
                if (!result) {
                    allRolledBack = false;
                    break;
                }
            } catch (Exception e) {
                allRolledBack = false;
                break;
            }
        }
        return false;
    }

    public void shutdown() {
        executor.shutdown();
    }
}