package distributed_tx;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.*;

public class Coordinator {
    private final List<Participant> participants = new ArrayList<>();
    private volatile boolean failureSimulated = false;
    private volatile boolean recoveryTriggered = false;
    private final Object recoveryLock = new Object();
    // Timeout in milliseconds for participant prepare phase
    private final long timeoutMillis = 100;

    /**
     * Register a participant to be involved in the transaction.
     * @param participant the transaction participant
     */
    public void addParticipant(Participant participant) {
        participants.add(participant);
    }

    /**
     * Executes the distributed transaction using Two-Phase Commit (2PC) protocol.
     * @return true if transaction commits successfully; false if aborted.
     */
    public boolean executeTransaction() {
        ExecutorService executor = Executors.newFixedThreadPool(participants.size());
        try {
            // Phase 1: Prepare Phase
            for (Participant participant : participants) {
                Future<Boolean> future = executor.submit(() -> participant.prepare());
                try {
                    Boolean vote = future.get(timeoutMillis, TimeUnit.MILLISECONDS);
                    if (!vote) {
                        rollbackAll();
                        return false;
                    }
                } catch (TimeoutException | InterruptedException | ExecutionException e) {
                    rollbackAll();
                    return false;
                }
            }
            
            // If a failure has been simulated, wait until recovery is triggered.
            if (failureSimulated) {
                waitForRecovery();
            }
            
            // Phase 2: Commit Phase
            for (Participant participant : participants) {
                participant.commit();
            }
            return true;
        } finally {
            executor.shutdown();
        }
    }

    /**
     * Rolls back all participants.
     */
    private void rollbackAll() {
        for (Participant participant : participants) {
            participant.rollback();
        }
    }

    /**
     * Simulate a coordinator failure after the prepare phase.
     */
    public void simulateFailure() {
        failureSimulated = true;
    }

    /**
     * Simulate the recovery of the coordinator. This method triggers completion
     * of the commit phase that was waiting due to a simulated failure.
     */
    public void recover() {
        synchronized (recoveryLock) {
            recoveryTriggered = true;
            recoveryLock.notifyAll();
        }
        failureSimulated = false;
    }

    /**
     * If a failure is simulated, wait until the recovery method is called.
     */
    private void waitForRecovery() {
        synchronized (recoveryLock) {
            try {
                while (!recoveryTriggered) {
                    recoveryLock.wait(50);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }
}