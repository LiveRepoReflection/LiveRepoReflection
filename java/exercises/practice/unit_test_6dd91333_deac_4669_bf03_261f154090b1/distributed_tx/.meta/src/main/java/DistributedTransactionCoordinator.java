package distributed_tx;

import java.util.*;
import java.util.concurrent.*;

public class DistributedTransactionCoordinator {
    public enum TransactionStatus {
        PENDING, COMMITTED, ABORTED
    }
    
    private ConcurrentHashMap<String, TransactionStatus> transactionStates = new ConcurrentHashMap<>();
    private ConcurrentHashMap<String, List<String>> transactionLogs = new ConcurrentHashMap<>();

    // Initiates a transaction using the two-phase commit protocol.
    public void startTransaction(String transactionId, List<Participant> participants, long timeoutMillis) {
        transactionStates.put(transactionId, TransactionStatus.PENDING);
        transactionLogs.put(transactionId, new ArrayList<>());
        List<Future<Boolean>> futures = new ArrayList<>();
        ExecutorService executor = Executors.newFixedThreadPool(participants.size());

        for (Participant p : participants) {
            futures.add(executor.submit(() -> p.prepare(transactionId)));
        }
        
        boolean allVoteCommit = true;
        for (Future<Boolean> future : futures) {
            try {
                boolean vote = future.get(timeoutMillis, TimeUnit.MILLISECONDS);
                transactionLogs.get(transactionId).add(vote ? "VOTE_COMMIT" : "VOTE_ABORT");
                if (!vote) {
                    allVoteCommit = false;
                }
            } catch (Exception e) {
                transactionLogs.get(transactionId).add("TIMEOUT");
                allVoteCommit = false;
            }
        }
        
        executor.shutdownNow();

        if (allVoteCommit) {
            transactionStates.put(transactionId, TransactionStatus.COMMITTED);
            for (Participant p : participants) {
                p.commit(transactionId);
            }
            transactionLogs.get(transactionId).add("COMMIT");
        } else {
            transactionStates.put(transactionId, TransactionStatus.ABORTED);
            for (Participant p : participants) {
                p.abort(transactionId);
            }
            transactionLogs.get(transactionId).add("ABORT");
        }
    }

    // Returns the current status of the transaction.
    public TransactionStatus getTransactionStatus(String transactionId) {
        return transactionStates.get(transactionId);
    }
    
    // Returns the transaction log detailing actions taken for the given transaction.
    public List<String> getTransactionLog(String transactionId) {
        return transactionLogs.get(transactionId);
    }
}