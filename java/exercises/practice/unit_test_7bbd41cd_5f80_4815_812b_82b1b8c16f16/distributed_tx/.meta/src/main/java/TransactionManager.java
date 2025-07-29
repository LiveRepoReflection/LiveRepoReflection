package distributed_tx;

import java.util.List;
import java.util.concurrent.*;
import java.io.*;
import java.util.concurrent.locks.ReentrantLock;

public class TransactionManager {
    private final String logFilePath;
    private final ReentrantLock logLock = new ReentrantLock();
    private static final long PREPARE_TIMEOUT_MS = 2000;

    public TransactionManager(String logFilePath) {
        this.logFilePath = logFilePath;
    }

    public boolean executeTransaction(String transactionId, List<Participant> participants) {
        boolean decision = true; // true means commit, false means abort
        log("START " + transactionId);
        ExecutorService executor = Executors.newFixedThreadPool(participants.size());
        try {
            for (Participant p : participants) {
                Future<Boolean> future = executor.submit(() -> p.prepare(transactionId));
                boolean vote = false;
                try {
                    vote = future.get(PREPARE_TIMEOUT_MS, TimeUnit.MILLISECONDS);
                } catch (TimeoutException e) {
                    vote = false;
                } catch (Exception e) {
                    vote = false;
                }
                log("PREPARE " + transactionId + " Participant: " + p.toString() + " Vote: " + vote);
                if (!vote) {
                    decision = false;
                    break;
                }
            }
        } finally {
            executor.shutdownNow();
        }
        if (decision) {
            for (Participant p : participants) {
                p.commit(transactionId);
            }
            log("FINAL " + transactionId + " Decision: COMMIT");
        } else {
            for (Participant p : participants) {
                p.rollback(transactionId);
            }
            log("FINAL " + transactionId + " Decision: ABORT");
        }
        return decision;
    }

    public static TransactionManager recoverFromLog(String logFilePath) {
        // For this simplified implementation, recovery is simulated by returning a new TransactionManager instance.
        return new TransactionManager(logFilePath);
    }

    public void recoverPendingTransactions() {
        // In a fully implemented system, this method would parse the log file and resolve any pending transactions.
        // For simplicity, we assume that transactions in the log are already finalized.
    }

    private void log(String message) {
        logLock.lock();
        try (FileWriter fw = new FileWriter(logFilePath, true);
             BufferedWriter bw = new BufferedWriter(fw)) {
            bw.write(message);
            bw.newLine();
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            logLock.unlock();
        }
    }
}