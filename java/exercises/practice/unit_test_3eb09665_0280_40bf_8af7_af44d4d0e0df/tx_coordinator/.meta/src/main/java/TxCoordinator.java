package tx_coordinator;

import java.util.List;
import java.util.UUID;
import java.util.ArrayList;
import java.util.concurrent.Callable;
import java.util.concurrent.Future;
import java.util.concurrent.Executors;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.concurrent.ExecutionException;

public class TxCoordinator {

    private final List<ParticipantService> participants;
    private final long prepareTimeoutMillis;
    private TransactionStatus status;
    private String txId;

    public TxCoordinator(List<ParticipantService> participants, long prepareTimeoutMillis) {
        this.participants = participants;
        this.prepareTimeoutMillis = prepareTimeoutMillis;
        this.status = TransactionStatus.BEGIN;
    }

    public synchronized TransactionStatus executeTransaction() {
        // Generate a unique transaction id
        txId = UUID.randomUUID().toString();
        System.out.println("Transaction " + txId + " started.");

        // Move to PREPARING state
        status = TransactionStatus.PREPARING;
        boolean prepareSuccess = executePreparePhase();

        if (!prepareSuccess) {
            // Transition to rollback phase due to prepare failure or timeout
            status = TransactionStatus.ROLLBACK_PENDING;
            System.out.println("Transaction " + txId + " failed during prepare. Initiating rollback.");
            executeRollbackPhase();
            status = TransactionStatus.ROLLED_BACK;
            System.out.println("Transaction " + txId + " rolled back.");
            return status;
        }

        // Move to commit phase if prepare successful
        status = TransactionStatus.COMMIT_PENDING;
        System.out.println("Transaction " + txId + " prepared successfully. Initiating commit.");
        boolean commitSuccess = executeCommitPhase();

        if (!commitSuccess) {
            // If commit fails, try a rollback (idempotent operations)
            status = TransactionStatus.ROLLBACK_PENDING;
            System.out.println("Transaction " + txId + " failed during commit. Initiating rollback.");
            executeRollbackPhase();
            status = TransactionStatus.ROLLED_BACK;
            System.out.println("Transaction " + txId + " rolled back.");
            return status;
        }

        status = TransactionStatus.COMMITTED;
        System.out.println("Transaction " + txId + " committed successfully.");
        return status;
    }

    private boolean executePreparePhase() {
        ExecutorService executor = Executors.newFixedThreadPool(participants.size());
        List<Future<Boolean>> futures = new ArrayList<>();

        for (ParticipantService participant : participants) {
            Callable<Boolean> task = () -> {
                System.out.println("Participant " + participant.getClass().getSimpleName() + " received prepare for txId " + txId);
                // The prepare call should be idempotent.
                return participant.prepare(txId);
            };
            futures.add(executor.submit(task));
        }

        boolean allPrepared = true;
        for (Future<Boolean> future : futures) {
            try {
                boolean result = future.get(prepareTimeoutMillis, TimeUnit.MILLISECONDS);
                if (!result) {
                    allPrepared = false;
                }
            } catch (TimeoutException te) {
                System.out.println("Timeout during prepare phase for txId " + txId);
                allPrepared = false;
            } catch (InterruptedException ie) {
                Thread.currentThread().interrupt();
                allPrepared = false;
            } catch (ExecutionException ee) {
                allPrepared = false;
            }
        }
        executor.shutdownNow();
        return allPrepared;
    }

    private boolean executeCommitPhase() {
        boolean allCommitted = true;
        for (ParticipantService participant : participants) {
            System.out.println("Participant " + participant.getClass().getSimpleName() + " received commit for txId " + txId);
            try {
                boolean result = participant.commit(txId);
                if (!result) {
                    allCommitted = false;
                }
            } catch (Exception e) {
                allCommitted = false;
            }
        }
        return allCommitted;
    }

    private void executeRollbackPhase() {
        for (ParticipantService participant : participants) {
            System.out.println("Participant " + participant.getClass().getSimpleName() + " received rollback for txId " + txId);
            try {
                participant.rollback(txId);
            } catch (Exception e) {
                // Since rollback is idempotent, continue regardless of individual failures.
            }
        }
    }
}