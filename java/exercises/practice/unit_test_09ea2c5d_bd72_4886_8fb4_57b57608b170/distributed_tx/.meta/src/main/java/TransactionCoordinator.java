package distributed_tx;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.BufferedReader;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.List;

public class TransactionCoordinator {

    private final String logFileName = "transaction_log.txt";

    public TransactionCoordinator() {
        // Ensure that the log file exists.
        File file = new File(logFileName);
        if (!file.exists()) {
            try {
                file.createNewFile();
            } catch (IOException e) {
                System.err.println("Unable to create log file: " + e.getMessage());
            }
        }
    }

    public TransactionStatus coordinateTransaction(Transaction tx, List<Participant> participants) throws Exception {
        // Phase 1: Preparation Phase
        boolean allPrepared = true;
        for (Participant participant : participants) {
            try {
                boolean vote = participant.prepare(tx);
                if (!vote) {
                    allPrepared = false;
                    break;
                }
            } catch (Exception e) {
                allPrepared = false;
                break;
            }
        }

        if (!allPrepared) {
            // Abort transaction: send abort to all participants.
            for (Participant participant : participants) {
                try {
                    participant.abort(tx);
                } catch (Exception e) {
                    // Ignore exceptions during abort to allow cleanup.
                }
            }
            logTransaction(tx.getTransactionId(), TransactionStatus.ABORTED);
            return TransactionStatus.ABORTED;
        }

        // Phase 2: Commit Phase
        try {
            for (Participant participant : participants) {
                participant.commit(tx);
            }
        } catch (Exception commitException) {
            // Propagate the commit failure.
            throw new Exception("Commit phase failed: " + commitException.getMessage());
        }

        logTransaction(tx.getTransactionId(), TransactionStatus.COMMITTED);
        return TransactionStatus.COMMITTED;
    }

    public TransactionStatus recoverTransaction(String transactionId) throws Exception {
        List<String> entries = readLogEntries();
        TransactionStatus status = null;
        for (String line : entries) {
            String[] parts = line.split(",");
            if (parts.length == 2) {
                String txId = parts[0].trim();
                String stat = parts[1].trim();
                if (txId.equals(transactionId)) {
                    if (stat.equals("COMMITTED")) {
                        status = TransactionStatus.COMMITTED;
                    } else if (stat.equals("ABORTED")) {
                        status = TransactionStatus.ABORTED;
                    }
                }
            }
        }
        if (status == null) {
            throw new Exception("Transaction not found in log for id: " + transactionId);
        }
        return status;
    }

    private synchronized void logTransaction(String transactionId, TransactionStatus status) throws IOException {
        BufferedWriter writer = new BufferedWriter(new FileWriter(logFileName, true));
        writer.write(transactionId + ", " + status);
        writer.newLine();
        writer.close();
    }

    private List<String> readLogEntries() throws IOException {
        List<String> entries = new ArrayList<>();
        BufferedReader reader = new BufferedReader(new FileReader(logFileName));
        String line;
        while ((line = reader.readLine()) != null) {
            entries.add(line);
        }
        reader.close();
        return entries;
    }
}