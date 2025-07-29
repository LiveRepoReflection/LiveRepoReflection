package tx_manager;

import java.util.UUID;
import java.util.List;
import java.util.ArrayList;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.ConcurrentMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

public class TransactionManager {

    private final ConcurrentMap<String, Transaction> transactions = new ConcurrentHashMap<>();
    private final ExecutorService executor = Executors.newCachedThreadPool();
    private final long prepareTimeoutMillis = 2000; // Timeout for participant prepare

    // In-memory transaction log: mapping transaction id to list of log entries.
    private final ConcurrentMap<String, List<LogEntry>> transactionLogs = new ConcurrentHashMap<>();

    public String beginTransaction() {
        String txId = UUID.randomUUID().toString();
        Transaction tx = new Transaction(txId);
        transactions.put(txId, tx);
        transactionLogs.put(txId, new CopyOnWriteArrayList<LogEntry>());
        log(txId, "BEGIN_TRANSACTION");
        return txId;
    }

    public void registerParticipant(String transactionId, Participant participant) {
        Transaction tx = transactions.get(transactionId);
        if (tx != null) {
            tx.registerParticipant(participant);
            log(transactionId, "REGISTER_PARTICIPANT: " + participant.toString());
        }
    }

    public void commitTransaction(String transactionId) {
        Transaction tx = transactions.get(transactionId);
        if (tx == null) {
            return;
        }

        List<Participant> participants = tx.getParticipants();
        boolean allCommit = true;
        List<Future<ParticipantVote>> futures = new ArrayList<>();

        // PREPARE phase: call prepare on all participants concurrently
        for (Participant participant : participants) {
            Future<ParticipantVote> future = executor.submit(() -> {
                Participant.Vote vote = participant.prepare(transactionId);
                return new ParticipantVote(participant, vote);
            });
            futures.add(future);
        }

        for (Future<ParticipantVote> future : futures) {
            try {
                ParticipantVote pv = future.get(prepareTimeoutMillis, TimeUnit.MILLISECONDS);
                log(transactionId, "PREPARE_RESPONSE from " + pv.participant.toString() + ": " + pv.vote);
                if (pv.vote != Participant.Vote.COMMIT) {
                    allCommit = false;
                }
            } catch (TimeoutException te) {
                allCommit = false;
                log(transactionId, "PREPARE_TIMEOUT");
            } catch (Exception e) {
                allCommit = false;
                log(transactionId, "PREPARE_EXCEPTION: " + e.getMessage());
            }
        }

        if (allCommit) {
            log(transactionId, "ALL_VOTE_COMMIT");
            for (Participant participant : participants) {
                try {
                    participant.commit(transactionId);
                    log(transactionId, "COMMIT_SENT to " + participant.toString());
                } catch (Exception e) {
                    log(transactionId, "COMMIT_EXCEPTION to " + participant.toString() + ": " + e.getMessage());
                }
            }
            tx.setState(TransactionState.COMMITTED);
            log(transactionId, "TRANSACTION_COMMITTED");
        } else {
            log(transactionId, "VOTE_ABORT_DETECTED");
            for (Participant participant : participants) {
                try {
                    participant.rollback(transactionId);
                    log(transactionId, "ROLLBACK_SENT to " + participant.toString());
                } catch (Exception e) {
                    log(transactionId, "ROLLBACK_EXCEPTION to " + participant.toString() + ": " + e.getMessage());
                }
            }
            tx.setState(TransactionState.ROLLEDBACK);
            log(transactionId, "TRANSACTION_ROLLEDBACK");
        }

        // Remove the transaction from active transactions.
        transactions.remove(transactionId);
    }

    private void log(String txId, String message) {
        List<LogEntry> logEntries = transactionLogs.get(txId);
        if (logEntries != null) {
            logEntries.add(new LogEntry(System.currentTimeMillis(), message));
        }
    }

    // Internal class to hold a participant's vote result.
    private static class ParticipantVote {
        Participant participant;
        Participant.Vote vote;

        ParticipantVote(Participant participant, Participant.Vote vote) {
            this.participant = participant;
            this.vote = vote;
        }
    }

    // Transaction states
    private enum TransactionState {
        PENDING,
        COMMITTED,
        ROLLEDBACK
    }

    // Internal Transaction class.
    private static class Transaction {
        private final String transactionId;
        private final List<Participant> participants = new CopyOnWriteArrayList<>();
        private TransactionState state = TransactionState.PENDING;

        Transaction(String transactionId) {
            this.transactionId = transactionId;
        }

        void registerParticipant(Participant participant) {
            if (!participants.contains(participant)) {
                participants.add(participant);
            }
        }

        List<Participant> getParticipants() {
            return participants;
        }

        void setState(TransactionState state) {
            this.state = state;
        }
    }

    // LogEntry class for transaction logging.
    private static class LogEntry {
        private final long timestamp;
        private final String message;

        LogEntry(long timestamp, String message) {
            this.timestamp = timestamp;
            this.message = message;
        }

        public long getTimestamp() {
            return timestamp;
        }

        public String getMessage() {
            return message;
        }
    }
}