import java.util.*;
import java.util.concurrent.*;
import java.util.logging.Logger;

public class Coordinator {
    private static final Logger LOGGER = Logger.getLogger(Coordinator.class.getName());
    private static final int MAX_PARTICIPANTS = 10;
    
    private final ConcurrentMap<String, TransactionLog> transactionLogs;
    private final ExecutorService executorService;
    private long timeout = 1000; // Default timeout in milliseconds
    private boolean simulateCrashAfterPrepare = false;

    public Coordinator() {
        this.transactionLogs = new ConcurrentHashMap<>();
        this.executorService = Executors.newCachedThreadPool();
    }

    public void setTimeout(long timeout) {
        this.timeout = timeout;
    }

    public void simulateCrashAfterPrepare(boolean simulate) {
        this.simulateCrashAfterPrepare = simulate;
    }

    public TransactionResult executeTransaction(Transaction transaction, List<Participant> participants) {
        if (participants.size() > MAX_PARTICIPANTS) {
            throw new IllegalArgumentException("Maximum number of participants exceeded");
        }

        // Check if transaction was already processed
        TransactionLog existingLog = transactionLogs.get(transaction.getId());
        if (existingLog != null && 
            (existingLog.getState() == TransactionState.COMMITTED || 
             existingLog.getState() == TransactionState.ROLLED_BACK)) {
            return new TransactionResult(
                existingLog.getState() == TransactionState.COMMITTED,
                "Transaction already processed",
                existingLog.getState()
            );
        }

        // Phase 1: Prepare
        TransactionLog log = new TransactionLog(transaction.getId(), TransactionState.INITIATED);
        transactionLogs.put(transaction.getId(), log);

        List<CompletableFuture<Vote>> prepareFutures = new ArrayList<>();
        for (Participant participant : participants) {
            CompletableFuture<Vote> future = CompletableFuture.supplyAsync(() -> {
                try {
                    return participant.prepare(transaction);
                } catch (Exception e) {
                    LOGGER.severe("Prepare phase failed for participant: " + e.getMessage());
                    return Vote.ROLLBACK;
                }
            }, executorService).orTimeout(timeout, TimeUnit.MILLISECONDS)
              .exceptionally(ex -> Vote.ROLLBACK);
            
            prepareFutures.add(future);
        }

        boolean shouldCommit = true;
        try {
            List<Vote> votes = CompletableFuture.allOf(
                prepareFutures.toArray(new CompletableFuture[0]))
                .thenApply(v -> prepareFutures.stream()
                    .map(CompletableFuture::join)
                    .toList())
                .get(timeout, TimeUnit.MILLISECONDS);

            shouldCommit = votes.stream().allMatch(vote -> vote == Vote.COMMIT);
            log.updateState(TransactionState.PREPARED);

            if (simulateCrashAfterPrepare) {
                throw new RuntimeException("Simulated crash after prepare phase");
            }

        } catch (Exception e) {
            shouldCommit = false;
            LOGGER.severe("Prepare phase failed: " + e.getMessage());
        }

        // Phase 2: Commit or Rollback
        if (shouldCommit) {
            return executeCommit(transaction, participants, log);
        } else {
            return executeRollback(transaction, participants, log);
        }
    }

    private TransactionResult executeCommit(Transaction transaction, List<Participant> participants, TransactionLog log) {
        List<CompletableFuture<Void>> commitFutures = participants.stream()
            .map(participant -> CompletableFuture.runAsync(() -> {
                try {
                    participant.commit(transaction);
                } catch (Exception e) {
                    LOGGER.severe("Commit failed for participant: " + e.getMessage());
                    throw new CompletionException(e);
                }
            }, executorService))
            .toList();

        try {
            CompletableFuture.allOf(commitFutures.toArray(new CompletableFuture[0]))
                .get(timeout, TimeUnit.MILLISECONDS);
            log.updateState(TransactionState.COMMITTED);
            return new TransactionResult(true, "Transaction committed successfully", TransactionState.COMMITTED);
        } catch (Exception e) {
            log.updateState(TransactionState.FAILED);
            LOGGER.severe("Commit phase failed: " + e.getMessage());
            return new TransactionResult(false, "Commit phase failed: " + e.getMessage(), TransactionState.FAILED);
        }
    }

    private TransactionResult executeRollback(Transaction transaction, List<Participant> participants, TransactionLog log) {
        List<CompletableFuture<Void>> rollbackFutures = participants.stream()
            .map(participant -> CompletableFuture.runAsync(() -> {
                try {
                    participant.rollback(transaction);
                } catch (Exception e) {
                    LOGGER.severe("Rollback failed for participant: " + e.getMessage());
                    throw new CompletionException(e);
                }
            }, executorService))
            .toList();

        try {
            CompletableFuture.allOf(rollbackFutures.toArray(new CompletableFuture[0]))
                .get(timeout, TimeUnit.MILLISECONDS);
            log.updateState(TransactionState.ROLLED_BACK);
            return new TransactionResult(false, "Transaction rolled back", TransactionState.ROLLED_BACK);
        } catch (Exception e) {
            log.updateState(TransactionState.FAILED);
            LOGGER.severe("Rollback phase failed: " + e.getMessage());
            return new TransactionResult(false, "Rollback phase failed: " + e.getMessage(), TransactionState.FAILED);
        }
    }

    public void recover() {
        transactionLogs.values().stream()
            .filter(log -> log.getState() == TransactionState.PREPARED)
            .forEach(log -> {
                log.updateState(TransactionState.ROLLED_BACK);
                LOGGER.info("Recovered transaction " + log.getTransactionId() + " by rolling back");
            });
    }

    public List<TransactionLog> getTransactionLogs() {
        return new ArrayList<>(transactionLogs.values());
    }

    public void shutdown() {
        executorService.shutdown();
        try {
            if (!executorService.awaitTermination(60, TimeUnit.SECONDS)) {
                executorService.shutdownNow();
            }
        } catch (InterruptedException e) {
            executorService.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }
}