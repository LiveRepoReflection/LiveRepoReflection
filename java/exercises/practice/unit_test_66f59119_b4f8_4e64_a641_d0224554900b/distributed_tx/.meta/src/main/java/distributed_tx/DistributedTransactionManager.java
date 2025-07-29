package distributed_tx;

import java.util.List;
import java.util.ArrayList;
import java.util.Map;
import java.util.concurrent.*;
import java.util.concurrent.ConcurrentHashMap;

public class DistributedTransactionManager {

    private List<Participant> participants;
    private Map<String, TransactionResult> transactions;
    private ExecutorService executor;

    // Timeout value in milliseconds for participant prepare call.
    private static final long PREPARE_TIMEOUT = 2000;

    public DistributedTransactionManager() {
        this.participants = new ArrayList<>();
        this.transactions = new ConcurrentHashMap<>();
        // Using a cached thread pool for concurrent participant calls.
        this.executor = Executors.newCachedThreadPool();
    }

    public void registerParticipant(Participant participant) {
        participants.add(participant);
    }

    public TransactionResult executeTransaction(Transaction tx) {
        TransactionResult result = prepareTransaction(tx);
        if (result.getStatus() == TransactionStatus.PREPARED) {
            // All participants are ready, proceed to commit phase.
            commitTransaction(tx);
            result.setStatus(TransactionStatus.COMMITTED);
            LogUtil.writeLog("Transaction " + tx.getId() + " committed successfully.");
        } else {
            // One or more participants fail to prepare. Abort transaction.
            abortTransaction(tx);
            result.setStatus(TransactionStatus.ABORTED);
            LogUtil.writeLog("Transaction " + tx.getId() + " aborted during prepare phase.");
        }
        transactions.put(tx.getId(), result);
        return result;
    }

    public void startTransaction(Transaction tx) {
        TransactionResult result = prepareTransaction(tx);
        transactions.put(tx.getId(), result);
    }

    private TransactionResult prepareTransaction(Transaction tx) {
        TransactionResult result = new TransactionResult(tx, TransactionStatus.PREPARED);
        List<Future<ParticipantResponse>> futures = new ArrayList<>();
        for (Participant participant : participants) {
            Callable<ParticipantResponse> task = () -> participant.prepare(tx);
            Future<ParticipantResponse> future = executor.submit(task);
            futures.add(future);
        }

        for (Future<ParticipantResponse> future : futures) {
            try {
                ParticipantResponse response = future.get(PREPARE_TIMEOUT, TimeUnit.MILLISECONDS);
                if (response != ParticipantResponse.COMMIT) {
                    result.setStatus(TransactionStatus.ABORTED);
                    LogUtil.writeLog("Transaction " + tx.getId() + " received ABORT response.");
                    // Early exit if any participant refuses.
                    return result;
                }
            } catch (TimeoutException e) {
                result.setStatus(TransactionStatus.ABORTED);
                LogUtil.writeLog("Transaction " + tx.getId() + " prepare phase timed out.");
                return result;
            } catch (Exception e) {
                result.setStatus(TransactionStatus.ABORTED);
                LogUtil.writeLog("Transaction " + tx.getId() + " encountered exception: " + e.getMessage());
                return result;
            }
        }
        return result;
    }

    private void commitTransaction(Transaction tx) {
        for (Participant participant : participants) {
            try {
                participant.commit(tx);
            } catch (Exception e) {
                LogUtil.writeLog("Commit failed for participant in transaction " + tx.getId() + ": " + e.getMessage());
            }
        }
    }

    private void abortTransaction(Transaction tx) {
        for (Participant participant : participants) {
            try {
                participant.abort(tx);
            } catch (Exception e) {
                LogUtil.writeLog("Abort failed for participant in transaction " + tx.getId() + ": " + e.getMessage());
            }
        }
    }

    public void recover() {
        // Iterate through transactions and for those in PREPARED state, complete the commit phase.
        for (Map.Entry<String, TransactionResult> entry : transactions.entrySet()) {
            TransactionResult result = entry.getValue();
            if (result.getStatus() == TransactionStatus.PREPARED) {
                Transaction tx = result.getTransaction();
                // Attempt to commit.
                commitTransaction(tx);
                result.setStatus(TransactionStatus.COMMITTED);
                LogUtil.writeLog("Recovered and committed transaction " + tx.getId());
            }
        }
    }

    public TransactionResult getTransactionResult(String txId) {
        return transactions.get(txId);
    }
}