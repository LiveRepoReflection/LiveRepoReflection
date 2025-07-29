import java.util.List;
import java.util.ArrayList;
import java.util.concurrent.Executors;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

public class TransactionManager {
    private final long timeoutMillis = 2000; // Timeout threshold for prepare phase in milliseconds

    public void executeTransaction(List<Participant> participants) throws Exception {
        logTransaction("START TRANSACTION");
        List<Vote> votes = new ArrayList<>();

        ExecutorService executor = Executors.newFixedThreadPool(participants.size());
        List<Future<Vote>> futures = new ArrayList<>();

        // Phase 1: Prepare
        logTransaction("PREPARING");
        for (Participant participant : participants) {
            Future<Vote> future = executor.submit(() -> participant.prepare());
            futures.add(future);
        }

        for (Future<Vote> future : futures) {
            try {
                Vote vote = future.get(timeoutMillis, TimeUnit.MILLISECONDS);
                votes.add(vote);
            } catch (TimeoutException e) {
                executor.shutdownNow();
                logTransaction("TIMEOUT DETECTED, ROLLING BACK");
                for (Participant participant : participants) {
                    participant.rollback();
                }
                logTransaction("TRANSACTION ROLLED BACK");
                throw new TransactionTimeoutException("Timeout during prepare phase");
            } catch (Exception ex) {
                executor.shutdownNow();
                logTransaction("EXCEPTION DETECTED, ROLLING BACK");
                for (Participant participant : participants) {
                    participant.rollback();
                }
                logTransaction("TRANSACTION ROLLED BACK");
                throw new TransactionFailedException("Exception during prepare: " + ex.getMessage());
            }
        }

        executor.shutdownNow();

        // Phase 2: Commit or Rollback based on votes
        boolean allCommit = votes.stream().allMatch(vote -> vote == Vote.COMMIT);

        if (allCommit) {
            logTransaction("COMMITTING");
            for (Participant participant : participants) {
                participant.commit();
            }
            logTransaction("TRANSACTION COMMITTED");
        } else {
            logTransaction("NEGATIVE VOTE DETECTED, ROLLING BACK");
            for (Participant participant : participants) {
                participant.rollback();
            }
            logTransaction("TRANSACTION ROLLED BACK");
            throw new TransactionFailedException("Prepare phase failed, rolling back");
        }

        logTransaction("END TRANSACTION");
    }

    private void logTransaction(String message) {
        System.out.println("[TransactionManager] " + message);
    }
}