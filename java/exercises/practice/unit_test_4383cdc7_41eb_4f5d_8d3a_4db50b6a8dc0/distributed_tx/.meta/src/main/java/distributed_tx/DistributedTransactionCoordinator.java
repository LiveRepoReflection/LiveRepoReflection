package distributed_tx;

import java.io.*;
import java.util.*;
import java.util.concurrent.locks.ReentrantLock;

public class DistributedTransactionCoordinator {
    // Log file to emulate persistent logging storage
    private final String logFilePath = "distributed_tx_log.txt";
    private final ReentrantLock logLock = new ReentrantLock();

    // Generates a unique transaction id based on UUID
    public String generateTransactionId() {
        return UUID.randomUUID().toString();
    }

    // Executes a distributed transaction using the Two-Phase Commit (2PC) protocol.
    // Returns true if commit succeeded, false if transaction was rolled back.
    public boolean executeTransaction(Transaction tx, List<Branch> branches) {
        List<Branch> preparedBranches = new ArrayList<>();
        logTransaction(tx.getTransactionId(), "START", branches);

        // Phase 1: Prepare
        for (Branch branch : branches) {
            // For simplicity, we assume one operation per branch.
            Operation op = tx.getOperations().get(0);
            boolean vote = branch.prepare(tx.getTransactionId(), op);
            logTransaction(tx.getTransactionId(), "PREPARE:" + (vote ? "YES" : "NO"), Collections.singletonList(branch));
            if (vote) {
                preparedBranches.add(branch);
            } else {
                // A failure forces rollback on all branches that voted yes.
                for (Branch b : preparedBranches) {
                    b.rollback(tx.getTransactionId());
                    logTransaction(tx.getTransactionId(), "ROLLBACK", Collections.singletonList(b));
                }
                logTransaction(tx.getTransactionId(), "ABORT", branches);
                return false;
            }
        }

        // Phase 2: Commit
        boolean allCommitted = true;
        for (Branch branch : branches) {
            boolean commitResult = branch.commit(tx.getTransactionId());
            logTransaction(tx.getTransactionId(), "COMMIT:" + (commitResult ? "SUCCESS" : "FAIL"), Collections.singletonList(branch));
            if (!commitResult) {
                allCommitted = false;
            }
        }

        logTransaction(tx.getTransactionId(), allCommitted ? "COMMIT_COMPLETE" : "COMMIT_INCONSISTENT", branches);
        return allCommitted;
    }

    // Recovery mechanism: Finalize an incomplete transaction.
    // decisionToCommit indicates whether to commit or rollback.
    public boolean recover(Transaction tx, List<Branch> branches, boolean decisionToCommit) {
        if (decisionToCommit) {
            for (Branch branch : branches) {
                branch.commit(tx.getTransactionId());
                logTransaction(tx.getTransactionId(), "RECOVERY_COMMIT", Collections.singletonList(branch));
            }
            logTransaction(tx.getTransactionId(), "RECOVERY_COMPLETE_COMMIT", branches);
            return true;
        } else {
            for (Branch branch : branches) {
                branch.rollback(tx.getTransactionId());
                logTransaction(tx.getTransactionId(), "RECOVERY_ROLLBACK", Collections.singletonList(branch));
            }
            logTransaction(tx.getTransactionId(), "RECOVERY_COMPLETE_ROLLBACK", branches);
            return false;
        }
    }

    // Synchronized logging to a persistent log (file)
    private void logTransaction(String transactionId, String event, List<?> branches) {
        logLock.lock();
        try (FileWriter fw = new FileWriter(logFilePath, true);
             BufferedWriter bw = new BufferedWriter(fw);
             PrintWriter out = new PrintWriter(bw)) {
            StringBuilder branchInfo = new StringBuilder();
            for (Object branch : branches) {
                branchInfo.append(branch.hashCode()).append(" ");
            }
            out.println(transactionId + " | " + event + " | " + branchInfo.toString().trim());
        } catch (IOException e) {
            System.err.println("Logging failed: " + e.getMessage());
        } finally {
            logLock.unlock();
        }
    }

    // For demonstration purposes: Reads the entire log file.
    public List<String> readLog() {
        List<String> logs = new ArrayList<>();
        logLock.lock();
        try (BufferedReader br = new BufferedReader(new FileReader(logFilePath))) {
            String line;
            while((line = br.readLine()) != null) {
                logs.add(line);
            }
        } catch (IOException e) {
            System.err.println("Reading log failed: " + e.getMessage());
        } finally {
            logLock.unlock();
        }
        return logs;
    }
}