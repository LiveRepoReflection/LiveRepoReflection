import java.io.*;
import java.util.*;
import java.util.concurrent.*;

public class Coordinator {
    private final Map<String, TransactionState> transactions = new ConcurrentHashMap<>();
    private final TransactionLog transactionLog = new TransactionLog();
    
    public void beginTransaction(String transactionId, List<Participant> participants) {
        TransactionState state = new TransactionState(participants);
        transactions.put(transactionId, state);
        transactionLog.logBegin(transactionId, participants.size());
    }

    public boolean prepareTransaction(String transactionId) {
        TransactionState state = transactions.get(transactionId);
        if (state == null) return false;

        state.prepareVotes = new ArrayList<>();
        for (Participant participant : state.participants) {
            boolean vote = participant.prepare(transactionId);
            state.prepareVotes.add(vote);
            if (!vote) break;
        }

        boolean allPrepared = state.prepareVotes.stream().allMatch(v -> v);
        transactionLog.logPrepare(transactionId, allPrepared);
        return allPrepared;
    }

    public void commitTransaction(String transactionId) {
        TransactionState state = transactions.get(transactionId);
        if (state == null) return;

        for (Participant participant : state.participants) {
            participant.commit(transactionId);
        }
        transactionLog.logCommit(transactionId);
        transactions.remove(transactionId);
    }

    public void rollbackTransaction(String transactionId) {
        TransactionState state = transactions.get(transactionId);
        if (state == null) return;

        for (Participant participant : state.participants) {
            participant.rollback(transactionId);
        }
        transactionLog.logRollback(transactionId);
        transactions.remove(transactionId);
    }

    public void recover() {
        Map<String, TransactionLog.LogEntry> incompleteTx = transactionLog.getIncompleteTransactions();
        for (Map.Entry<String, TransactionLog.LogEntry> entry : incompleteTx.entrySet()) {
            String txId = entry.getKey();
            TransactionLog.LogEntry logEntry = entry.getValue();
            
            if (logEntry.prepared) {
                commitTransaction(txId);
            } else {
                rollbackTransaction(txId);
            }
        }
    }

    private static class TransactionState {
        final List<Participant> participants;
        List<Boolean> prepareVotes;

        TransactionState(List<Participant> participants) {
            this.participants = participants;
        }
    }
}