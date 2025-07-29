import java.io.*;
import java.util.*;

public class TransactionLog {
    private static final String LOG_FILE = "tx-coordinator.log";
    
    public synchronized void logBegin(String transactionId, int participantCount) {
        writeLog(transactionId, "BEGIN", participantCount, false);
    }

    public synchronized void logPrepare(String transactionId, boolean prepared) {
        writeLog(transactionId, "PREPARE", -1, prepared);
    }

    public synchronized void logCommit(String transactionId) {
        writeLog(transactionId, "COMMIT", -1, true);
    }

    public synchronized void logRollback(String transactionId) {
        writeLog(transactionId, "ROLLBACK", -1, false);
    }

    public synchronized Map<String, LogEntry> getIncompleteTransactions() {
        Map<String, LogEntry> incomplete = new HashMap<>();
        try (BufferedReader reader = new BufferedReader(new FileReader(LOG_FILE))) {
            String line;
            while ((line = reader.readLine()) != null) {
                String[] parts = line.split(",");
                String txId = parts[0];
                String action = parts[1];
                
                if (action.equals("BEGIN")) {
                    incomplete.put(txId, new LogEntry(false));
                } else if (action.equals("PREPARE")) {
                    boolean prepared = Boolean.parseBoolean(parts[3]);
                    incomplete.put(txId, new LogEntry(prepared));
                }
            }
        } catch (IOException e) {
            // File doesn't exist yet
        }
        return incomplete;
    }

    private void writeLog(String transactionId, String action, int participantCount, boolean prepared) {
        try (PrintWriter writer = new PrintWriter(new FileWriter(LOG_FILE, true))) {
            String logLine = transactionId + "," + action + "," + participantCount + "," + prepared;
            writer.println(logLine);
        } catch (IOException e) {
            throw new RuntimeException("Failed to write transaction log", e);
        }
    }

    public static class LogEntry {
        final boolean prepared;
        
        LogEntry(boolean prepared) {
            this.prepared = prepared;
        }
    }
}