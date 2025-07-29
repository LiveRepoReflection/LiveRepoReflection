import java.util.Map;
import java.util.HashMap;
import java.util.concurrent.ConcurrentHashMap;

public class MockOrderService implements ParticipantService {
    private final Map<String, Boolean> preparedTransactions = new ConcurrentHashMap<>();
    private final Map<String, Boolean> committedTransactions = new ConcurrentHashMap<>();
    private final Map<String, Boolean> rolledBackTransactions = new ConcurrentHashMap<>();
    private boolean shouldFailPrepare = false;

    @Override
    public synchronized boolean prepare(String transactionId, Map<String, Object> data) {
        if (shouldFailPrepare) {
            return false;
        }
        preparedTransactions.put(transactionId, true);
        return true;
    }

    @Override
    public synchronized boolean commit(String transactionId) {
        if (!preparedTransactions.containsKey(transactionId)) {
            return false;
        }
        committedTransactions.put(transactionId, true);
        preparedTransactions.remove(transactionId);
        return true;
    }

    @Override
    public synchronized boolean rollback(String transactionId) {
        rolledBackTransactions.put(transactionId, true);
        preparedTransactions.remove(transactionId);
        return true;
    }

    public void setShouldFailPrepare(boolean shouldFail) {
        this.shouldFailPrepare = shouldFail;
    }

    public boolean isPrepared(String transactionId) {
        return preparedTransactions.getOrDefault(transactionId, false);
    }

    public boolean isCommitted(String transactionId) {
        return committedTransactions.getOrDefault(transactionId, false);
    }

    public boolean isRolledBack(String transactionId) {
        return rolledBackTransactions.getOrDefault(transactionId, false);
    }
}