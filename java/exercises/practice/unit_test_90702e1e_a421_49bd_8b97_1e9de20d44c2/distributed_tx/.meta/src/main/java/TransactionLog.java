package distributed_tx;

import java.util.concurrent.CopyOnWriteArrayList;

public class TransactionLog {
    private static final CopyOnWriteArrayList<String> logs = new CopyOnWriteArrayList<>();

    public static void log(String txId, String message) {
        String logEntry = "TXID: " + txId + " - " + message;
        logs.add(logEntry);
        System.out.println(logEntry);
    }

    public static CopyOnWriteArrayList<String> getLogs() {
        return logs;
    }
}