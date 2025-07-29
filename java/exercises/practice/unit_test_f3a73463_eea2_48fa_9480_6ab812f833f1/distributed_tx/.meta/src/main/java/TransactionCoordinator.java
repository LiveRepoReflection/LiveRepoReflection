import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class TransactionCoordinator {
    // Map to store transactionId -> list of enlisted shards.
    private final Map<String, List<Shard>> transactions = new ConcurrentHashMap<>();
    // Maximum number of retries for commit and rollback.
    private static final int MAX_RETRY = 5;
    // Base delay in milliseconds for retry backoff.
    private static final long BASE_DELAY_MS = 50;

    /**
     * Begins a new distributed transaction.
     * @param transactionId Unique identifier for the transaction.
     */
    public void beginTransaction(String transactionId) {
        // Use synchronized list to hold shards.
        transactions.put(transactionId, Collections.synchronizedList(new ArrayList<>()));
        log("Transaction started: " + transactionId);
    }

    /**
     * Enlists a shard into an existing transaction.
     * @param transactionId Unique identifier for the transaction.
     * @param shard The shard to enlist.
     */
    public void enlistShard(String transactionId, Shard shard) {
        List<Shard> shards = transactions.get(transactionId);
        if (shards == null) {
            throw new IllegalArgumentException("Transaction " + transactionId + " does not exist.");
        }
        synchronized (shards) {
            if (!shards.contains(shard)) {
                shards.add(shard);
                log("Shard enlisted in transaction " + transactionId);
            }
        }
    }

    /**
     * Prepares the transaction by calling prepare on each enlisted shard.
     * @param transactionId Unique identifier for the transaction.
     * @return true if all shards prepared successfully, false otherwise.
     */
    public boolean prepareTransaction(String transactionId) {
        List<Shard> shards = transactions.get(transactionId);
        if (shards == null) {
            throw new IllegalArgumentException("Transaction " + transactionId + " does not exist.");
        }

        boolean allPrepared = true;
        synchronized (shards) {
            for (Shard shard : shards) {
                try {
                    boolean prepared = shard.prepare(transactionId);
                    log("Shard prepare result for transaction " + transactionId + ": " + prepared);
                    if (!prepared) {
                        allPrepared = false;
                    }
                } catch (Exception e) {
                    log("Exception during prepare on transaction " + transactionId + ": " + e.getMessage());
                    allPrepared = false;
                }
            }
        }
        if (allPrepared) {
            log("All shards prepared successfully for transaction " + transactionId);
        } else {
            log("Prepare phase failed for transaction " + transactionId);
        }
        return allPrepared;
    }

    /**
     * Commits the transaction if the prepare phase succeeded.
     * Retries commit on any shard that fails with a reasonable backoff.
     * @param transactionId Unique identifier for the transaction.
     */
    public void commitTransaction(String transactionId) {
        List<Shard> shards = transactions.get(transactionId);
        if (shards == null) {
            throw new IllegalArgumentException("Transaction " + transactionId + " does not exist.");
        }

        synchronized (shards) {
            for (Shard shard : shards) {
                boolean committed = false;
                int attempt = 0;
                while (!committed && attempt < MAX_RETRY) {
                    try {
                        shard.commit(transactionId);
                        log("Shard commit success on transaction " + transactionId + " at attempt " + (attempt + 1));
                        committed = true;
                    } catch (Exception e) {
                        attempt++;
                        log("Shard commit failure on transaction " + transactionId + " at attempt " + attempt + ": " + e.getMessage());
                        try {
                            Thread.sleep(BASE_DELAY_MS * attempt);
                        } catch (InterruptedException ie) {
                            Thread.currentThread().interrupt();
                        }
                    }
                }
                if (!committed) {
                    log("Failed to commit shard for transaction " + transactionId + " after " + MAX_RETRY + " attempts.");
                    // Depending on system design, you may choose to throw an exception or mark for manual intervention.
                    throw new RuntimeException("Commit failed for transaction " + transactionId);
                }
            }
        }
        log("Transaction " + transactionId + " committed successfully.");
        // Optionally, cleanup the transaction
        transactions.remove(transactionId);
    }

    /**
     * Rolls back the transaction.
     * Retries rollback on any shard that fails, logs error if rollback ultimately fails.
     * @param transactionId Unique identifier for the transaction.
     */
    public void rollbackTransaction(String transactionId) {
        List<Shard> shards = transactions.get(transactionId);
        if (shards == null) {
            throw new IllegalArgumentException("Transaction " + transactionId + " does not exist.");
        }

        synchronized (shards) {
            for (Shard shard : shards) {
                boolean rolledBack = false;
                int attempt = 0;
                while (!rolledBack && attempt < MAX_RETRY) {
                    try {
                        shard.rollback(transactionId);
                        log("Shard rollback success on transaction " + transactionId + " at attempt " + (attempt + 1));
                        rolledBack = true;
                    } catch (Exception e) {
                        attempt++;
                        log("Shard rollback failure on transaction " + transactionId + " at attempt " + attempt + ": " + e.getMessage());
                        try {
                            Thread.sleep(BASE_DELAY_MS * attempt);
                        } catch (InterruptedException ie) {
                            Thread.currentThread().interrupt();
                        }
                    }
                }
                if (!rolledBack) {
                    log("Failed to rollback shard for transaction " + transactionId + " after " + MAX_RETRY + " attempts. Manual intervention may be required.");
                }
            }
        }
        log("Transaction " + transactionId + " rolled back.");
        // Cleanup the transaction
        transactions.remove(transactionId);
    }

    private void log(String message) {
        System.out.println("[TransactionCoordinator] " + message);
    }
}