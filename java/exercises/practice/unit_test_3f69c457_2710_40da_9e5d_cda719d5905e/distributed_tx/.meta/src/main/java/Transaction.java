package distributed_tx;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.*;

public class Transaction {
    private final List<Participant> participants = new ArrayList<>();
    private long timeout;
    private int maxRetries;
    private long retryInterval;

    public Transaction(long timeout, int maxRetries, long retryInterval) {
        this.timeout = timeout;
        this.maxRetries = maxRetries;
        this.retryInterval = retryInterval;
    }

    public void registerParticipant(Participant participant) {
        synchronized (participants) {
            participants.add(participant);
        }
    }

    public void setTimeout(long timeout) {
        this.timeout = timeout;
    }

    public void setMaxRetries(int maxRetries) {
        this.maxRetries = maxRetries;
    }

    public void setRetryInterval(long retryInterval) {
        this.retryInterval = retryInterval;
    }

    public boolean execute() {
        boolean prepareSuccess = true;
        // Phase 1: Prepare
        for (Participant participant : participants) {
            Boolean result = callWithTimeout(() -> participant.prepare(), timeout);
            if (result == null || !result) {
                prepareSuccess = false;
                break;
            }
        }
        boolean overallSuccess = false;
        if (prepareSuccess) {
            // Phase 2: Commit
            overallSuccess = true;
            for (Participant participant : participants) {
                boolean commitSuccess = executeWithRetries(() -> participant.commit());
                if (!commitSuccess) {
                    overallSuccess = false;
                    break;
                }
            }
            if (!overallSuccess) {
                // If commit fails for at least one participant, attempt rollback for all.
                for (Participant participant : participants) {
                    executeWithRetries(() -> participant.rollback());
                }
            }
        } else {
            // Rollback phase if prepare failed
            overallSuccess = false;
            for (Participant participant : participants) {
                executeWithRetries(() -> participant.rollback());
            }
        }
        return overallSuccess;
    }

    private boolean executeWithRetries(Callable<Boolean> task) {
        int attempts = 0;
        while (attempts <= maxRetries) {
            Boolean result = callWithTimeout(task, timeout);
            if (result != null && result) {
                return true;
            }
            attempts++;
            if (attempts <= maxRetries) {
                try {
                    Thread.sleep(retryInterval);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    return false;
                }
            }
        }
        return false;
    }

    private Boolean callWithTimeout(Callable<Boolean> task, long timeoutMillis) {
        ExecutorService executor = Executors.newSingleThreadExecutor();
        Future<Boolean> future = executor.submit(task);
        try {
            return future.get(timeoutMillis, TimeUnit.MILLISECONDS);
        } catch (TimeoutException e) {
            future.cancel(true);
            return false;
        } catch (Exception e) {
            return false;
        } finally {
            executor.shutdownNow();
        }
    }
}