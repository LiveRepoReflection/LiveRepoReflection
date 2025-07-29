import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.ReentrantLock;

public class TransactionManager {
    private final Map<String, TransactionState> transactionStates;
    private final Map<String, ReentrantLock> transactionLocks;
    private final String logPath = "transaction_logs";

    public TransactionManager() {
        this.transactionStates = new ConcurrentHashMap<>();
        this.transactionLocks = new ConcurrentHashMap<>();
        createLogDirectory();
    }

    public boolean executeTransaction(String txId, TransactionParticipant... participants) {
        ReentrantLock lock = transactionLocks.computeIfAbsent(txId, k -> new ReentrantLock());
        
        if (!lock.tryLock()) {
            return getTransactionState(txId) == TransactionState.COMMITTED;
        }

        try {
            if (transactionStates.containsKey(txId)) {
                return getTransactionState(txId) == TransactionState.COMMITTED;
            }

            logTransactionStart(txId);
            transactionStates.put(txId, TransactionState.STARTED);

            // Phase 1: Prepare
            boolean allPrepared = true;
            for (TransactionParticipant participant : participants) {
                if (!participant.prepare(txId)) {
                    allPrepared = false;
                    break;
                }
            }

            // Phase 2: Commit or Rollback
            if (allPrepared) {
                for (TransactionParticipant participant : participants) {
                    participant.commit(txId);
                }
                transactionStates.put(txId, TransactionState.COMMITTED);
                logTransactionEnd(txId, true);
                return true;
            } else {
                for (TransactionParticipant participant : participants) {
                    participant.rollback(txId);
                }
                transactionStates.put(txId, TransactionState.ROLLED_BACK);
                logTransactionEnd(txId, false);
                return false;
            }
        } finally {
            lock.unlock();
        }
    }

    public void logTransactionStart(String txId) {
        try {
            Files.write(
                Paths.get(logPath, txId + ".log"),
                Arrays.asList("START", String.valueOf(System.currentTimeMillis())),
                StandardOpenOption.CREATE
            );
        } catch (IOException e) {
            throw new RuntimeException("Failed to log transaction start", e);
        }
    }

    private void logTransactionEnd(String txId, boolean committed) {
        try {
            Files.write(
                Paths.get(logPath, txId + ".log"),
                Arrays.asList(committed ? "COMMIT" : "ROLLBACK", String.valueOf(System.currentTimeMillis())),
                StandardOpenOption.APPEND
            );
        } catch (IOException e) {
            throw new RuntimeException("Failed to log transaction end", e);
        }
    }

    public boolean recoverTransaction(String txId) {
        try {
            List<String> logs = Files.readAllLines(Paths.get(logPath, txId + ".log"));
            if (logs.size() >= 2) {
                String lastAction = logs.get(logs.size() - 2);
                if ("COMMIT".equals(lastAction)) {
                    transactionStates.put(txId, TransactionState.COMMITTED);
                    return true;
                } else if ("ROLLBACK".equals(lastAction)) {
                    transactionStates.put(txId, TransactionState.ROLLED_BACK);
                    return true;
                }
            }
            transactionStates.put(txId, TransactionState.ROLLED_BACK);
            return true;
        } catch (IOException e) {
            return false;
        }
    }

    public TransactionState getTransactionState(String txId) {
        return transactionStates.getOrDefault(txId, TransactionState.UNKNOWN);
    }

    private void createLogDirectory() {
        try {
            Files.createDirectories(Paths.get(logPath));
        } catch (IOException e) {
            throw new RuntimeException("Failed to create log directory", e);
        }
    }
}