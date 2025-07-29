import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class DistributedTransactionManager {
    // Registry of service participants by their unique identifier.
    private final Map<String, ServiceParticipant> serviceRegistry = new HashMap<>();
    // Tracks the finalized transactions to ensure idempotent commit/rollback.
    private final Set<String> finalizedTransactions = new HashSet<>();

    /**
     * Registers a service participant with the DTM.
     *
     * @param serviceId   unique identifier for the service.
     * @param participant the instance implementing ServiceParticipant.
     */
    public synchronized void registerService(String serviceId, ServiceParticipant participant) {
        serviceRegistry.put(serviceId, participant);
    }

    /**
     * Executes a distributed transaction by coordinating the prepare, commit, and rollback phases.
     *
     * @param transactionId unique identifier for the transaction.
     * @param serviceIds    list of service identifiers participating in the transaction.
     * @return true if the transaction commits successfully; false if the transaction was rolled back.
     */
    public boolean executeTransaction(String transactionId, List<String> serviceIds) {
        // Prepare phase: ask each service to prepare.
        boolean allPrepared = true;
        for (String serviceId : serviceIds) {
            ServiceParticipant participant = serviceRegistry.get(serviceId);
            if (participant == null) {
                allPrepared = false;
                break;
            }
            boolean prepared = participant.prepare(transactionId);
            if (!prepared) {
                allPrepared = false;
                break;
            }
        }
        // Commit if all services are prepared successfully; otherwise rollback.
        if (allPrepared) {
            commitTransaction(transactionId, serviceIds);
            return true;
        } else {
            rollbackTransaction(transactionId, serviceIds);
            return false;
        }
    }

    /**
     * Commits the transaction by invoking commit on each service participant.
     * This method is idempotent: duplicate invocations will have no additional effect.
     *
     * @param transactionId unique identifier for the transaction.
     * @param serviceIds    list of service identifiers participating in the transaction.
     */
    public synchronized void commitTransaction(String transactionId, List<String> serviceIds) {
        if (finalizedTransactions.contains(transactionId)) {
            return;
        }
        for (String serviceId : serviceIds) {
            ServiceParticipant participant = serviceRegistry.get(serviceId);
            if (participant != null) {
                participant.commit(transactionId);
            }
        }
        finalizedTransactions.add(transactionId);
    }

    /**
     * Rolls back the transaction by invoking rollback on each service participant.
     * This method is idempotent: duplicate invocations will have no additional effect.
     *
     * @param transactionId unique identifier for the transaction.
     * @param serviceIds    list of service identifiers participating in the transaction.
     */
    public synchronized void rollbackTransaction(String transactionId, List<String> serviceIds) {
        if (finalizedTransactions.contains(transactionId)) {
            return;
        }
        for (String serviceId : serviceIds) {
            ServiceParticipant participant = serviceRegistry.get(serviceId);
            if (participant != null) {
                participant.rollback(transactionId);
            }
        }
        finalizedTransactions.add(transactionId);
    }
}