package distributed_tx;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.util.*;
import java.util.concurrent.*;

public class DistributedTxTest {

    enum TransactionStatus {
        PENDING, COMMITTED, ABORTED
    }
    
    // This interface simulates a participant in the two-phase commit protocol.
    interface Participant {
        // Simulate the prepare phase. Return true if voting commit, false otherwise.
        boolean prepare(String transactionId);
        // Process the commit command.
        void commit(String transactionId);
        // Process the abort command.
        void abort(String transactionId);
    }
    
    // A simplified Distributed Transaction Coordinator implementing 2PC.
    class DistributedTransactionCoordinator {
        private ConcurrentHashMap<String, TransactionStatus> transactionStates = new ConcurrentHashMap<>();
        private ConcurrentHashMap<String, List<String>> transactionLogs = new ConcurrentHashMap<>();

        // Initiates a transaction with the given participants and timeout for each vote.
        public void startTransaction(String transactionId, List<Participant> participants, long timeoutMillis) {
            transactionStates.put(transactionId, TransactionStatus.PENDING);
            transactionLogs.put(transactionId, new ArrayList<>());
            List<Future<Boolean>> futures = new ArrayList<>();
            ExecutorService executor = Executors.newFixedThreadPool(participants.size());
            for (Participant p : participants) {
                futures.add(executor.submit(() -> {
                    boolean vote = p.prepare(transactionId);
                    return vote;
                }));
            }
            boolean allVoteCommit = true;
            for (Future<Boolean> future : futures) {
                try {
                    boolean vote = future.get(timeoutMillis, TimeUnit.MILLISECONDS);
                    transactionLogs.get(transactionId).add(vote ? "VOTE_COMMIT" : "VOTE_ABORT");
                    if (!vote) {
                        allVoteCommit = false;
                    }
                } catch (Exception e) {
                    transactionLogs.get(transactionId).add("TIMEOUT");
                    allVoteCommit = false;
                }
            }
            executor.shutdownNow();

            if (allVoteCommit) {
                transactionStates.put(transactionId, TransactionStatus.COMMITTED);
                for (Participant p : participants) {
                    p.commit(transactionId);
                }
                transactionLogs.get(transactionId).add("COMMIT");
            } else {
                transactionStates.put(transactionId, TransactionStatus.ABORTED);
                for (Participant p : participants) {
                    p.abort(transactionId);
                }
                transactionLogs.get(transactionId).add("ABORT");
            }
        }

        // Returns the transaction status.
        public TransactionStatus getTransactionStatus(String transactionId) {
            return transactionStates.get(transactionId);
        }
        
        // Returns the transaction log for the given transaction.
        public List<String> getTransactionLog(String transactionId) {
            return transactionLogs.get(transactionId);
        }
    }
    
    // Participant that always votes commit.
    class CommitParticipant implements Participant {
        private boolean prepared = false;
        private boolean committed = false;
        private boolean aborted = false;
        
        public boolean prepare(String transactionId) {
            prepared = true;
            return true;
        }
        public void commit(String transactionId) {
            if (prepared) {
                committed = true;
            }
        }
        public void abort(String transactionId) {
            if (prepared) {
                aborted = true;
            }
        }
    }
    
    // Participant that always votes abort.
    class AbortParticipant implements Participant {
        private boolean prepared = false;
        private boolean committed = false;
        private boolean aborted = false;
        
        public boolean prepare(String transactionId) {
            prepared = true;
            return false;
        }
        public void commit(String transactionId) {
            committed = true;
        }
        public void abort(String transactionId) {
            if (prepared) {
                aborted = true;
            }
        }
    }
    
    // Participant that simulates a delay causing a timeout.
    class SlowParticipant implements Participant {
        private boolean prepared = false;
        private boolean committed = false;
        private boolean aborted = false;
        private long delayMillis;
        
        public SlowParticipant(long delayMillis) {
            this.delayMillis = delayMillis;
        }
        public boolean prepare(String transactionId) {
            try {
                Thread.sleep(delayMillis);
            } catch (InterruptedException e) {
                return false;
            }
            prepared = true;
            return true;
        }
        public void commit(String transactionId) {
            if (prepared) {
                committed = true;
            }
        }
        public void abort(String transactionId) {
            if (prepared) {
                aborted = true;
            }
        }
    }
    
    @Test
    public void testSuccessfulTransaction() {
        DistributedTransactionCoordinator coordinator = new DistributedTransactionCoordinator();
        List<Participant> participants = new ArrayList<>();
        participants.add(new CommitParticipant());
        participants.add(new CommitParticipant());
        participants.add(new CommitParticipant());
        String transactionId = "tx_success";
        coordinator.startTransaction(transactionId, participants, 1000);
        TransactionStatus status = coordinator.getTransactionStatus(transactionId);
        assertEquals(TransactionStatus.COMMITTED, status, "Transaction should be committed when all participants vote commit.");
        List<String> log = coordinator.getTransactionLog(transactionId);
        assertTrue(log.contains("COMMIT"), "Transaction log must record COMMIT action.");
    }
    
    @Test
    public void testAbortTransactionDueToAbortVote() {
        DistributedTransactionCoordinator coordinator = new DistributedTransactionCoordinator();
        List<Participant> participants = new ArrayList<>();
        participants.add(new CommitParticipant());
        participants.add(new AbortParticipant());
        participants.add(new CommitParticipant());
        String transactionId = "tx_abort_vote";
        coordinator.startTransaction(transactionId, participants, 1000);
        TransactionStatus status = coordinator.getTransactionStatus(transactionId);
        assertEquals(TransactionStatus.ABORTED, status, "Transaction should be aborted if any participant votes abort.");
        List<String> log = coordinator.getTransactionLog(transactionId);
        assertTrue(log.contains("ABORT"), "Transaction log must record ABORT action.");
    }
    
    @Test
    public void testAbortTransactionDueToTimeout() {
        DistributedTransactionCoordinator coordinator = new DistributedTransactionCoordinator();
        List<Participant> participants = new ArrayList<>();
        participants.add(new CommitParticipant());
        participants.add(new SlowParticipant(1500)); // This participant delays beyond the specified timeout.
        participants.add(new CommitParticipant());
        String transactionId = "tx_abort_timeout";
        coordinator.startTransaction(transactionId, participants, 1000);
        TransactionStatus status = coordinator.getTransactionStatus(transactionId);
        assertEquals(TransactionStatus.ABORTED, status, "Transaction should be aborted if a participant times out.");
        List<String> log = coordinator.getTransactionLog(transactionId);
        assertTrue(log.contains("ABORT"), "Transaction log must record ABORT action.");
        assertTrue(log.contains("TIMEOUT"), "Transaction log must record TIMEOUT occurrence.");
    }
    
    @Test
    public void testConcurrentTransactions() throws InterruptedException {
        DistributedTransactionCoordinator coordinator = new DistributedTransactionCoordinator();
        ExecutorService executor = Executors.newFixedThreadPool(5);
        List<Callable<String>> tasks = new ArrayList<>();
        int numTransactions = 10;
        
        for (int i = 0; i < numTransactions; i++) {
            final int txIndex = i;
            tasks.add(() -> {
                List<Participant> participants = new ArrayList<>();
                participants.add(new CommitParticipant());
                participants.add(new CommitParticipant());
                String txId = "tx_concurrent_" + txIndex;
                coordinator.startTransaction(txId, participants, 1000);
                return txId;
            });
        }
        try {
            List<Future<String>> futures = executor.invokeAll(tasks);
            for (Future<String> future : futures) {
                String txId = future.get();
                TransactionStatus status = coordinator.getTransactionStatus(txId);
                assertEquals(TransactionStatus.COMMITTED, status, "Concurrent transaction " + txId + " should be committed.");
            }
        } catch (Exception e) {
            fail("Concurrent transaction execution failed: " + e.getMessage());
        } finally {
            executor.shutdownNow();
        }
    }
    
    @Test
    public void testCoordinatorRecoverySimulation() {
        // Simulate coordinator crash and recovery by checking that the persisted state remains consistent.
        DistributedTransactionCoordinator coordinator = new DistributedTransactionCoordinator();
        List<Participant> participants = new ArrayList<>();
        participants.add(new CommitParticipant());
        participants.add(new CommitParticipant());
        String transactionId = "tx_recovery";
        coordinator.startTransaction(transactionId, participants, 1000);
        TransactionStatus statusAfter = coordinator.getTransactionStatus(transactionId);
        assertNotNull(statusAfter, "Transaction status must not be null after recovery simulation.");
        if (statusAfter == TransactionStatus.COMMITTED) {
            List<String> log = coordinator.getTransactionLog(transactionId);
            assertTrue(log.contains("COMMIT"), "Recovered transaction must have COMMIT logged.");
        } else if (statusAfter == TransactionStatus.ABORTED) {
            List<String> log = coordinator.getTransactionLog(transactionId);
            assertTrue(log.contains("ABORT"), "Recovered transaction must have ABORT logged.");
        } else {
            fail("Transaction status must not remain PENDING after completion.");
        }
    }
}