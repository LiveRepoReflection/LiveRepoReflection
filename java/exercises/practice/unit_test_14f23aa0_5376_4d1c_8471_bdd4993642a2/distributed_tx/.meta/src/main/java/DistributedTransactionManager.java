import java.util.Map;
import java.util.HashMap;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Executors;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutionException;

public class DistributedTransactionManager {
    private final Map<String, ParticipantService> services = new ConcurrentHashMap<>();
    private final Map<String, TransactionState> transactionStates = new ConcurrentHashMap<>();
    private int prepareTimeout = 5000; // Default 5 seconds timeout
    private final ExecutorService executor = Executors.newCachedThreadPool();

    public void registerService(String serviceName, ParticipantService service) {
        services.put(serviceName, service);
    }

    public String beginTransaction() {
        String transactionId = UUID.randomUUID().toString();
        transactionStates.put(transactionId, new TransactionState());
        return transactionId;
    }

    public boolean commitTransaction(String transactionId, Map<String, Map<String, Object>> transactionData) {
        if (!transactionStates.containsKey(transactionId)) {
            return false;
        }

        TransactionState state = transactionStates.get(transactionId);
        if (state.getPhase() != TransactionPhase.INITIAL) {
            return state.getPhase() == TransactionPhase.COMMITTED;
        }

        // Prepare phase
        state.setPhase(TransactionPhase.PREPARING);
        boolean allPrepared = preparePhase(transactionId, transactionData);

        if (!allPrepared) {
            rollbackPhase(transactionId);
            return false;
        }

        // Commit phase
        state.setPhase(TransactionPhase.COMMITTING);
        boolean allCommitted = commitPhase(transactionId);

        if (allCommitted) {
            state.setPhase(TransactionPhase.COMMITTED);
            return true;
        } else {
            rollbackPhase(transactionId);
            return false;
        }
    }

    private boolean preparePhase(String transactionId, Map<String, Map<String, Object>> transactionData) {
        Map<String, CompletableFuture<Boolean>> futures = new HashMap<>();

        for (Map.Entry<String, Map<String, Object>> entry : transactionData.entrySet()) {
            String serviceName = entry.getKey();
            Map<String, Object> data = entry.getValue();
            ParticipantService service = services.get(serviceName);

            if (service != null) {
                CompletableFuture<Boolean> future = CompletableFuture.supplyAsync(() -> {
                    try {
                        return service.prepare(transactionId, data);
                    } catch (Exception e) {
                        return false;
                    }
                }, executor);

                futures.put(serviceName, future);
            }
        }

        try {
            CompletableFuture<Void> allFutures = CompletableFuture.allOf(
                futures.values().toArray(new CompletableFuture[0])
            );
            allFutures.get(prepareTimeout, TimeUnit.MILLISECONDS);

            for (Map.Entry<String, CompletableFuture<Boolean>> entry : futures.entrySet()) {
                if (!entry.getValue().get()) {
                    return false;
                }
            }
            return true;
        } catch (TimeoutException e) {
            return false;
        } catch (InterruptedException | ExecutionException e) {
            Thread.currentThread().interrupt();
            return false;
        }
    }

    private boolean commitPhase(String transactionId) {
        for (ParticipantService service : services.values()) {
            try {
                if (!service.commit(transactionId)) {
                    return false;
                }
            } catch (Exception e) {
                return false;
            }
        }
        return true;
    }

    private void rollbackPhase(String transactionId) {
        for (ParticipantService service : services.values()) {
            try {
                service.rollback(transactionId);
            } catch (Exception e) {
                // Continue with other services even if one fails
            }
        }
    }

    public void setPrepareTimeout(int timeoutMillis) {
        this.prepareTimeout = timeoutMillis;
    }

    private enum TransactionPhase {
        INITIAL, PREPARING, COMMITTING, COMMITTED, ROLLED_BACK
    }

    private static class TransactionState {
        private TransactionPhase phase = TransactionPhase.INITIAL;

        public TransactionPhase getPhase() {
            return phase;
        }

        public void setPhase(TransactionPhase phase) {
            this.phase = phase;
        }
    }
}