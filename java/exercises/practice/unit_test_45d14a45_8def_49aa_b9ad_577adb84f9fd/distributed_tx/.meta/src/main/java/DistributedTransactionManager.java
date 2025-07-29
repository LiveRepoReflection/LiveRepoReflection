package distributed_tx;

import java.util.List;
import java.util.ArrayList;
import java.util.concurrent.*;

public class DistributedTransactionManager {

    private final List<TransactionParticipant> participants;
    private final int timeoutMillis;

    public DistributedTransactionManager(List<TransactionParticipant> participants, int timeoutMillis) {
        this.participants = participants;
        this.timeoutMillis = timeoutMillis;
    }

    public TransactionResult executeTransaction() {
        ExecutorService executor = Executors.newFixedThreadPool(participants.size());
        try {
            // Prepare Phase
            List<Future<Boolean>> futures = new ArrayList<>();
            for (TransactionParticipant participant : participants) {
                Future<Boolean> future = executor.submit(() -> participant.prepare());
                futures.add(future);
            }

            for (Future<Boolean> future : futures) {
                try {
                    Boolean prepared = future.get(timeoutMillis, TimeUnit.MILLISECONDS);
                    if (!prepared) {
                        rollbackAll();
                        return TransactionResult.ABORT;
                    }
                } catch (TimeoutException | ExecutionException | InterruptedException e) {
                    rollbackAll();
                    return TransactionResult.ABORT;
                }
            }

            // Durable logging before commit phase
            durableLog("COMMIT");

            // Commit Phase
            for (TransactionParticipant participant : participants) {
                try {
                    participant.commit();
                } catch (Exception e) {
                    // In a real system, we would handle commit failures.
                }
            }
            return TransactionResult.COMMIT;
        } finally {
            executor.shutdownNow();
        }
    }

    private void rollbackAll() {
        for (TransactionParticipant participant : participants) {
            try {
                participant.rollback();
            } catch (Exception e) {
                // Ignore exceptions in rollback to ensure all participants get a chance to rollback.
            }
        }
        durableLog("ABORT");
    }

    // Simulate durable persistence by appending the decision to a local log file.
    private void durableLog(String decision) {
        try (java.io.FileWriter fw = new java.io.FileWriter("tx_log.txt", true)) {
            fw.write(decision + "\n");
            fw.flush();
        } catch (Exception e) {
            // In production, proper error handling/logging is required.
        }
    }
}