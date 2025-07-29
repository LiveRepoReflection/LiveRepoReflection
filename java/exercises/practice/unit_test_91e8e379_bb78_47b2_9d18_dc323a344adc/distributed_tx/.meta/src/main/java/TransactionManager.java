package distributed_tx;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

public class TransactionManager {
    // List of registered resource managers.
    private final List<ResourceManager> resourceManagers = new ArrayList<>();
    
    // Map to hold transaction votes: txid -> (rmId -> vote)
    private final Map<String, Map<String, String>> transactionVotes = new ConcurrentHashMap<>();
    
    // Map to hold transaction start times: txid -> start time (milliseconds)
    private final Map<String, Long> transactionStartTime = new ConcurrentHashMap<>();

    // Timeout duration in milliseconds.
    private final long TIMEOUT = 1000;

    /**
     * Registers a Resource Manager to participate in transactions.
     * @param rm The Resource Manager to register.
     */
    public void registerResourceManager(ResourceManager rm) {
        resourceManagers.add(rm);
    }

    /**
     * Begins a new transaction by generating a unique transaction ID.
     * @return The generated transaction ID.
     */
    public String beginTransaction() {
        String txid = UUID.randomUUID().toString();
        transactionVotes.put(txid, new ConcurrentHashMap<>());
        transactionStartTime.put(txid, System.currentTimeMillis());
        return txid;
    }

    /**
     * Receives a vote from a Resource Manager for a given transaction.
     * @param txid The transaction ID.
     * @param rmId The unique identifier of the Resource Manager.
     * @param vote The vote, either "commit" or "abort".
     */
    public void receiveVote(String txid, String rmId, String vote) {
        Map<String, String> votes = transactionVotes.get(txid);
        if (votes != null) {
            votes.put(rmId, vote);
        }
    }

    /**
     * Runs the Two-Phase Commit protocol for a transaction.
     * Waits for votes until a predefined timeout has elapsed,
     * then either commits or aborts the transaction based on the collected votes.
     * @param txid The transaction ID.
     */
    public void runTransaction(String txid) {
        long start = System.currentTimeMillis();
        // Wait for all Resource Managers to vote or until timeout.
        while (true) {
            Map<String, String> votes = transactionVotes.get(txid);
            boolean allVoted = true;
            for (ResourceManager rm : resourceManagers) {
                String rmId = getResourceManagerId(rm);
                if (!votes.containsKey(rmId)) {
                    allVoted = false;
                    break;
                }
            }
            if (allVoted || (System.currentTimeMillis() - start > TIMEOUT)) {
                break;
            }
            try {
                Thread.sleep(10);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }

        Map<String, String> votes = transactionVotes.get(txid);
        boolean commitTransaction = true;
        // Evaluate votes: if any RM did not vote or voted "abort", abort the transaction.
        for (ResourceManager rm : resourceManagers) {
            String rmId = getResourceManagerId(rm);
            String vote = votes.get(rmId);
            if (vote == null || !"commit".equalsIgnoreCase(vote)) {
                commitTransaction = false;
                break;
            }
        }
        // Notify Resource Managers to commit or abort.
        for (ResourceManager rm : resourceManagers) {
            if (commitTransaction) {
                rm.commit(txid);
            } else {
                rm.abort(txid);
            }
        }
        // Clean up transaction state.
        transactionVotes.remove(txid);
        transactionStartTime.remove(txid);
    }

    /**
     * Helper method to get the unique identifier for a Resource Manager.
     * It first checks if the ResourceManager has a "getId" method; if not, returns its hashcode.
     * @param rm The Resource Manager object.
     * @return The unique identifier as a String.
     */
    private String getResourceManagerId(ResourceManager rm) {
        try {
            return (String) rm.getClass().getMethod("getId").invoke(rm);
        } catch (Exception e) {
            return String.valueOf(rm.hashCode());
        }
    }
}