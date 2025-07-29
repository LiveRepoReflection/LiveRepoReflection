import java.util.*;

public class DistributedTransactionCoordinator {
    private final Map<String, String> resourceData;
    private final Set<String> failedNodes;

    public DistributedTransactionCoordinator() {
        resourceData = new HashMap<>();
        failedNodes = Collections.synchronizedSet(new HashSet<>());
    }

    public synchronized TransactionOutcome process(Transaction transaction) {
        List<String> conflictNotifications = new ArrayList<>();
        for (Operation op : transaction.getOperations()) {
            String resourceId = op.getResourceId();
            if (op.getType() == OperationType.READ) {
                continue;
            } else if (op.getType() == OperationType.WRITE) {
                if (failedNodes.contains(resourceId)) {
                    failedNodes.remove(resourceId);
                }
                String existingValue = resourceData.get(resourceId);
                if (existingValue != null && !existingValue.equals(op.getData())) {
                    conflictNotifications.add("Conflict on resource " + resourceId + ": previous value '" 
                        + existingValue + "' overwritten by transaction " + transaction.getTransactionId());
                }
                resourceData.put(resourceId, op.getData());
            }
        }
        Map<String, String> currentStates = new HashMap<>();
        for (Operation op : transaction.getOperations()) {
            currentStates.put(op.getResourceId(), resourceData.get(op.getResourceId()));
        }
        return new TransactionOutcome("COMMIT", currentStates, conflictNotifications);
    }

    public synchronized void simulateNodeFailure(String resourceId) {
        failedNodes.add(resourceId);
    }
}