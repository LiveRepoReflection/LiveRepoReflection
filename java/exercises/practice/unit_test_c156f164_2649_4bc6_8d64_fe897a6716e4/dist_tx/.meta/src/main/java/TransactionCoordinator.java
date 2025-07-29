import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

public class TransactionCoordinator {
    private final Map<String, List<ResourceManager>> transactions = new ConcurrentHashMap<>();
    private final Map<String, Boolean> transactionPrepared = new ConcurrentHashMap<>();
    private final Path logFile;

    public TransactionCoordinator() {
        logFile = Paths.get("dist_tx_transaction.log");
    }

    public void registerTransaction(String transactionId, List<ResourceManager> resourceManagers) {
        transactions.put(transactionId, resourceManagers);
    }

    public void executeTransaction(String transactionId) {
        List<ResourceManager> resourceManagers = transactions.get(transactionId);
        if (resourceManagers == null) {
            throw new IllegalArgumentException("Transaction not registered: " + transactionId);
        }
        boolean allPrepared = true;
        for (ResourceManager rm : resourceManagers) {
            if (!rm.prepare(transactionId)) {
                allPrepared = false;
                break;
            }
        }
        transactionPrepared.put(transactionId, allPrepared);
        writeLog(transactionId, allPrepared ? "PREPARED_COMMIT" : "PREPARED_ABORT");

        if (allPrepared) {
            for (ResourceManager rm : resourceManagers) {
                rm.commit(transactionId);
            }
            writeLog(transactionId, "COMMITTED");
        } else {
            for (ResourceManager rm : resourceManagers) {
                rm.rollback(transactionId);
            }
            writeLog(transactionId, "ROLLEDBACK");
        }
    }

    public void simulateCrashAfterPrepare(String transactionId) {
        List<ResourceManager> resourceManagers = transactions.get(transactionId);
        if (resourceManagers == null) {
            return;
        }
        boolean allPrepared = true;
        for (ResourceManager rm : resourceManagers) {
            if (!rm.prepare(transactionId)) {
                allPrepared = false;
                break;
            }
        }
        transactionPrepared.put(transactionId, allPrepared);
        writeLog(transactionId, allPrepared ? "PREPARED_COMMIT" : "PREPARED_ABORT");
        // Simulate crash: do not proceed to commit or rollback.
    }

    public void recover() {
        try {
            if (!Files.exists(logFile)) {
                return;
            }
            List<String> lines = Files.readAllLines(logFile);
            Map<String, String> lastState = new HashMap<>();
            for (String line : lines) {
                String[] parts = line.split(",");
                if (parts.length == 2) {
                    lastState.put(parts[0], parts[1]);
                }
            }
            for (Map.Entry<String, String> entry : lastState.entrySet()) {
                String txId = entry.getKey();
                String state = entry.getValue();
                List<ResourceManager> resourceManagers = transactions.get(txId);
                if (resourceManagers == null) {
                    continue;
                }
                if (state.equals("PREPARED_COMMIT")) {
                    for (ResourceManager rm : resourceManagers) {
                        rm.commit(txId);
                    }
                    writeLog(txId, "COMMITTED");
                } else if (state.equals("PREPARED_ABORT")) {
                    for (ResourceManager rm : resourceManagers) {
                        rm.rollback(txId);
                    }
                    writeLog(txId, "ROLLEDBACK");
                }
            }
            Files.delete(logFile);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private synchronized void writeLog(String transactionId, String status) {
        String logEntry = transactionId + "," + status;
        try (BufferedWriter writer = Files.newBufferedWriter(logFile, StandardOpenOption.CREATE, StandardOpenOption.APPEND)) {
            writer.write(logEntry);
            writer.newLine();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}