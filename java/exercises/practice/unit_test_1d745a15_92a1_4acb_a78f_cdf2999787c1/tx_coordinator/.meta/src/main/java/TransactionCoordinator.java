import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class TransactionCoordinator {
    private Map<String, BankServer> servers;
    private List<String> log;

    public TransactionCoordinator(Map<String, BankServer> servers) {
        this.servers = servers;
        this.log = new ArrayList<>();
    }

    public List<String> getLog() {
        return log;
    }

    public boolean processTransaction(Transaction transaction) {
        // Group operations by serverID
        Map<String, List<Operation>> opsByServer = new HashMap<>();
        for (Operation op : transaction.operations) {
            opsByServer.computeIfAbsent(op.serverID, k -> new ArrayList<>()).add(op);
        }

        Map<String, Boolean> prepareResults = new HashMap<>();

        // Phase 1: Prepare using Two-Phase Commit protocol.
        for (Map.Entry<String, List<Operation>> entry : opsByServer.entrySet()) {
            String serverID = entry.getKey();
            BankServer server = servers.get(serverID);
            boolean result = server.prepare(transaction.transactionID, entry.getValue());
            prepareResults.put(serverID, result);
            log.add("Prepared " + serverID + " " + result);
            if (!result) {
                break;
            }
        }

        // Check if all servers are ready to commit.
        boolean allPrepared = prepareResults.values().stream().allMatch(b -> b);

        if (allPrepared) {
            // Phase 2: Commit the transaction on all servers.
            for (String serverID : opsByServer.keySet()) {
                BankServer server = servers.get(serverID);
                server.commit(transaction.transactionID);
                log.add("Committed " + serverID);
            }
            return true;
        } else {
            // Rollback on servers that successfully prepared.
            for (Map.Entry<String, Boolean> entry : prepareResults.entrySet()) {
                if (entry.getValue()) {
                    BankServer server = servers.get(entry.getKey());
                    server.rollback(transaction.transactionID);
                    log.add("Rolled back " + entry.getKey());
                }
            }
            return false;
        }
    }
}