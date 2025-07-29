package distributed_tx;

import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class TransactionCoordinator {
    private final List<Participant> participants;
    private final Map<String, Transaction> activeTransactions = new ConcurrentHashMap<>();
    private final Map<String, Boolean> preparedStatus = new ConcurrentHashMap<>();
    private final Map<String, Boolean> commitStatus = new ConcurrentHashMap<>();

    public TransactionCoordinator(List<Participant> participants) {
        this.participants = participants;
    }

    public void beginTransaction(Transaction tx) {
        activeTransactions.put(tx.getId(), tx);
    }

    public boolean prepareTransaction(Transaction tx) {
        boolean overallPrepared = true;
        for (Participant participant : participants) {
            boolean prepared = participant.prepare(tx);
            if (!prepared) {
                overallPrepared = false;
            }
        }
        preparedStatus.put(tx.getId(), overallPrepared);
        return overallPrepared;
    }

    public boolean commitTransaction(Transaction tx) {
        if (!Boolean.TRUE.equals(preparedStatus.get(tx.getId()))) {
            return false;
        }
        boolean overallCommit = true;
        for (Participant participant : participants) {
            boolean committed = participant.commit(tx);
            if (!committed) {
                overallCommit = false;
            }
        }
        commitStatus.put(tx.getId(), overallCommit);
        return overallCommit;
    }

    public boolean rollbackTransaction(Transaction tx) {
        boolean overallRollback = true;
        for (Participant participant : participants) {
            if (!participant.rollback(tx)) {
                overallRollback = false;
            }
        }
        return overallRollback;
    }
}