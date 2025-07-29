package transaction_coordinator;

import java.util.Map;
import java.util.UUID;
import java.util.concurrent.*;
import java.util.concurrent.ConcurrentHashMap;

public class DistributedTransactionCoordinator {

    private final Map<String, TransactionParticipant> participants = new ConcurrentHashMap<>();
    private final ExecutorService executor = Executors.newCachedThreadPool();
    private final long TIMEOUT_MILLIS = 2000; // Timeout for prepare phase (in milliseconds)

    /**
     * Registers a TransactionParticipant with the coordinator.
     * @param id Unique identifier for the participant.
     * @param participant The participant instance to register.
     */
    public void registerParticipant(String id, TransactionParticipant participant) {
        participants.put(id, participant);
    }

    /**
     * Executes the transaction following the Two-Phase Commit protocol.
     * @param request TransactionRequest containing the operations for each participant.
     * @return true if the transaction was committed successfully; false if the transaction was aborted.
     */
    public boolean executeTransaction(TransactionRequest request) {
        String txId = UUID.randomUUID().toString();
        Map<String, String> operations = request.getOperations();
        ConcurrentHashMap<String, Boolean> prepareResults = new ConcurrentHashMap<>();

        // Phase 1: Prepare Phase
        CountDownLatch latch = new CountDownLatch(operations.size());
        for (Map.Entry<String, String> entry : operations.entrySet()) {
            String participantId = entry.getKey();
            String operation = entry.getValue();
            TransactionParticipant participant = participants.get(participantId);
            if (participant == null) {
                // Participant not registered; automatically vote abort.
                prepareResults.put(participantId, false);
                latch.countDown();
                continue;
            }
            executor.submit(() -> {
                try {
                    Future<Boolean> future = executor.submit(() -> participant.prepare(txId, operation));
                    Boolean vote = future.get(TIMEOUT_MILLIS, TimeUnit.MILLISECONDS);
                    prepareResults.put(participantId, vote);
                } catch (InterruptedException | ExecutionException | TimeoutException e) {
                    prepareResults.put(participantId, false);
                } finally {
                    latch.countDown();
                }
            });
        }

        try {
            latch.await();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return false;
        }

        boolean allVoteCommit = true;
        for (Boolean vote : prepareResults.values()) {
            if (!vote) {
                allVoteCommit = false;
                break;
            }
        }

        // Phase 2: Commit or Abort phase
        if (allVoteCommit) {
            for (String participantId : operations.keySet()) {
                TransactionParticipant participant = participants.get(participantId);
                if (participant != null) {
                    executor.submit(() -> {
                        try {
                            participant.commit(txId);
                            System.out.println("Committed for participant " + participantId + " on transaction " + txId);
                        } catch (Exception e) {
                            System.out.println("Error during commit for participant " + participantId + " on transaction " + txId);
                        }
                    });
                }
            }
            return true;
        } else {
            for (String participantId : operations.keySet()) {
                TransactionParticipant participant = participants.get(participantId);
                if (participant != null) {
                    executor.submit(() -> {
                        try {
                            participant.rollback(txId);
                            System.out.println("Rolled back for participant " + participantId + " on transaction " + txId);
                        } catch (Exception e) {
                            System.out.println("Error during rollback for participant " + participantId + " on transaction " + txId);
                        }
                    });
                }
            }
            return false;
        }
    }
}