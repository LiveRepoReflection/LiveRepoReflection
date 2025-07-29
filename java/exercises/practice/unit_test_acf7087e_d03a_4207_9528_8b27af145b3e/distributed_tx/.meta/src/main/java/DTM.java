import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeoutException;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * Distributed Transaction Manager (DTM) that implements a Two-Phase Commit (2PC) protocol.
 * This class coordinates transactions across multiple participants to ensure atomicity.
 */
public class DTM {
    private static final Logger LOGGER = Logger.getLogger(DTM.class.getName());
    
    // Timeout for prepare/commit/rollback operations (in milliseconds)
    private static final long OPERATION_TIMEOUT_MS = 5000;
    
    // Thread pool for parallel execution of transaction phases
    private final ExecutorService executorService;
    
    // Maps transaction IDs to sets of participants
    private final Map<String, Set<Participant>> transactionParticipants;
    
    // Maps transaction IDs to their current state
    private final Map<String, TransactionState> transactionStates;

    /**
     * Enum representing the possible states of a distributed transaction.
     */
    private enum TransactionState {
        ACTIVE,
        PREPARING,
        PREPARED,
        COMMITTING,
        COMMITTED,
        ROLLING_BACK,
        ROLLED_BACK
    }

    /**
     * Creates a new Distributed Transaction Manager.
     */
    public DTM() {
        this.executorService = Executors.newCachedThreadPool();
        this.transactionParticipants = new ConcurrentHashMap<>();
        this.transactionStates = new ConcurrentHashMap<>();
    }

    /**
     * Begins a new distributed transaction.
     *
     * @return A unique transaction ID.
     */
    public String begin() {
        String transactionId = generateTransactionId();
        transactionParticipants.put(transactionId, ConcurrentHashMap.newKeySet());
        transactionStates.put(transactionId, TransactionState.ACTIVE);
        LOGGER.info("Transaction " + transactionId + " started");
        return transactionId;
    }

    /**
     * Enlists a participant in the specified transaction.
     *
     * @param transactionId The ID of the transaction.
     * @param participant The participant to enlist.
     */
    public void enlist(String transactionId, Participant participant) {
        validateTransactionActive(transactionId);
        transactionParticipants.get(transactionId).add(participant);
        LOGGER.info("Participant " + participant + " enlisted in transaction " + transactionId);
    }

    /**
     * Commits the specified transaction using the Two-Phase Commit protocol.
     *
     * @param transactionId The ID of the transaction to commit.
     * @return true if the transaction was committed successfully, false otherwise.
     */
    public boolean commit(String transactionId) {
        // Check if transaction exists
        if (!transactionParticipants.containsKey(transactionId)) {
            LOGGER.warning("Cannot commit non-existent transaction: " + transactionId);
            return false;
        }
        
        // Check current transaction state for idempotency
        TransactionState currentState = transactionStates.get(transactionId);
        if (currentState == TransactionState.COMMITTED) {
            LOGGER.info("Transaction " + transactionId + " already committed (idempotent operation)");
            return true;
        }
        
        if (currentState == TransactionState.ROLLED_BACK) {
            LOGGER.warning("Cannot commit transaction " + transactionId + " because it was already rolled back");
            return false;
        }
        
        // Get participants for this transaction
        Set<Participant> participants = transactionParticipants.get(transactionId);
        if (participants.isEmpty()) {
            // No participants, consider it a successful commit
            transactionStates.put(transactionId, TransactionState.COMMITTED);
            LOGGER.info("Transaction " + transactionId + " committed (no participants)");
            return true;
        }
        
        // === PHASE 1: PREPARE ===
        transactionStates.put(transactionId, TransactionState.PREPARING);
        LOGGER.info("Transaction " + transactionId + " prepare phase started with " + participants.size() + " participants");
        
        boolean prepareSuccess = prepareAllParticipants(transactionId, participants);
        
        if (!prepareSuccess) {
            // If prepare failed, roll back all participants
            rollback(transactionId);
            return false;
        }
        
        // Update state to PREPARED
        transactionStates.put(transactionId, TransactionState.PREPARED);
        
        // === PHASE 2: COMMIT ===
        transactionStates.put(transactionId, TransactionState.COMMITTING);
        LOGGER.info("Transaction " + transactionId + " commit phase started");
        
        boolean commitSuccess = commitAllParticipants(transactionId, participants);
        
        if (!commitSuccess) {
            // This is a critical failure - prepare was successful but commit failed
            // In a production system, we would need a recovery mechanism here
            LOGGER.severe("CRITICAL: Transaction " + transactionId + " had successful prepare but failed commit!");
            transactionStates.put(transactionId, TransactionState.ROLLED_BACK);
            return false;
        }
        
        // Update state to COMMITTED
        transactionStates.put(transactionId, TransactionState.COMMITTED);
        LOGGER.info("Transaction " + transactionId + " successfully committed");
        return true;
    }

    /**
     * Rolls back the specified transaction.
     *
     * @param transactionId The ID of the transaction to roll back.
     */
    public void rollback(String transactionId) {
        // Check if transaction exists
        if (!transactionParticipants.containsKey(transactionId)) {
            LOGGER.warning("Cannot rollback non-existent transaction: " + transactionId);
            return;
        }
        
        // Check current transaction state for idempotency
        TransactionState currentState = transactionStates.get(transactionId);
        if (currentState == TransactionState.ROLLED_BACK) {
            LOGGER.info("Transaction " + transactionId + " already rolled back (idempotent operation)");
            return;
        }
        
        if (currentState == TransactionState.COMMITTED) {
            LOGGER.severe("Cannot rollback transaction " + transactionId + " because it was already committed");
            return;
        }
        
        // Get participants for this transaction
        Set<Participant> participants = transactionParticipants.get(transactionId);
        if (participants.isEmpty()) {
            // No participants, mark as rolled back
            transactionStates.put(transactionId, TransactionState.ROLLED_BACK);
            LOGGER.info("Transaction " + transactionId + " rolled back (no participants)");
            return;
        }
        
        // Update state to ROLLING_BACK
        transactionStates.put(transactionId, TransactionState.ROLLING_BACK);
        LOGGER.info("Rolling back transaction " + transactionId + " with " + participants.size() + " participants");
        
        rollbackAllParticipants(transactionId, participants);
        
        // Update state to ROLLED_BACK
        transactionStates.put(transactionId, TransactionState.ROLLED_BACK);
        LOGGER.info("Transaction " + transactionId + " successfully rolled back");
    }

    /**
     * Prepares all participants for the specified transaction.
     *
     * @param transactionId The ID of the transaction.
     * @param participants The set of participants to prepare.
     * @return true if all participants were prepared successfully, false otherwise.
     */
    private boolean prepareAllParticipants(String transactionId, Set<Participant> participants) {
        List<Participant> participantList = new ArrayList<>(participants);
        CountDownLatch latch = new CountDownLatch(participantList.size());
        AtomicBoolean allPrepared = new AtomicBoolean(true);
        
        // Launch parallel prepare tasks
        List<Future<?>> futures = new ArrayList<>();
        for (Participant participant : participantList) {
            Future<?> future = executorService.submit(() -> {
                try {
                    boolean prepared = false;
                    try {
                        prepared = participant.prepare(transactionId);
                    } catch (Exception e) {
                        LOGGER.log(Level.WARNING, "Exception during prepare for participant " + participant, e);
                        prepared = false;
                    }
                    
                    if (!prepared) {
                        LOGGER.warning("Participant " + participant + " failed to prepare for transaction " + transactionId);
                        allPrepared.set(false);
                    }
                } finally {
                    latch.countDown();
                }
            });
            futures.add(future);
        }
        
        // Wait for all prepare operations to complete or time out
        try {
            boolean completed = latch.await(OPERATION_TIMEOUT_MS, TimeUnit.MILLISECONDS);
            if (!completed) {
                LOGGER.warning("Prepare phase timed out for transaction " + transactionId);
                allPrepared.set(false);
                
                // Cancel any pending futures
                for (Future<?> future : futures) {
                    if (!future.isDone()) {
                        future.cancel(true);
                    }
                }
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            LOGGER.warning("Prepare phase interrupted for transaction " + transactionId);
            allPrepared.set(false);
        }
        
        return allPrepared.get();
    }

    /**
     * Commits all participants for the specified transaction.
     *
     * @param transactionId The ID of the transaction.
     * @param participants The set of participants to commit.
     * @return true if all participants were committed successfully, false otherwise.
     */
    private boolean commitAllParticipants(String transactionId, Set<Participant> participants) {
        List<Participant> participantList = new ArrayList<>(participants);
        CountDownLatch latch = new CountDownLatch(participantList.size());
        AtomicBoolean allCommitted = new AtomicBoolean(true);
        
        // Launch parallel commit tasks
        for (Participant participant : participantList) {
            executorService.submit(() -> {
                try {
                    boolean committed = false;
                    try {
                        committed = participant.commit(transactionId);
                    } catch (Exception e) {
                        LOGGER.log(Level.SEVERE, "Exception during commit for participant " + participant, e);
                        committed = false;
                    }
                    
                    if (!committed) {
                        LOGGER.severe("CRITICAL: Participant " + participant + " failed to commit transaction " 
                                + transactionId + " after successful prepare!");
                        allCommitted.set(false);
                    }
                } finally {
                    latch.countDown();
                }
            });
        }
        
        // Wait for all commit operations to complete or time out
        try {
            boolean completed = latch.await(OPERATION_TIMEOUT_MS, TimeUnit.MILLISECONDS);
            if (!completed) {
                LOGGER.severe("Commit phase timed out for transaction " + transactionId);
                allCommitted.set(false);
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            LOGGER.severe("Commit phase interrupted for transaction " + transactionId);
            allCommitted.set(false);
        }
        
        return allCommitted.get();
    }

    /**
     * Rolls back all participants for the specified transaction.
     *
     * @param transactionId The ID of the transaction.
     * @param participants The set of participants to roll back.
     */
    private void rollbackAllParticipants(String transactionId, Set<Participant> participants) {
        List<Participant> participantList = new ArrayList<>(participants);
        CountDownLatch latch = new CountDownLatch(participantList.size());
        
        // Launch parallel rollback tasks
        for (Participant participant : participantList) {
            executorService.submit(() -> {
                try {
                    try {
                        boolean rolledBack = participant.rollback(transactionId);
                        if (!rolledBack) {
                            LOGGER.warning("Participant " + participant + " reported failure during rollback of transaction " 
                                    + transactionId);
                        }
                    } catch (Exception e) {
                        LOGGER.log(Level.WARNING, "Exception during rollback for participant " + participant, e);
                    }
                } finally {
                    latch.countDown();
                }
            });
        }
        
        // Wait for all rollback operations to complete or time out
        try {
            boolean completed = latch.await(OPERATION_TIMEOUT_MS, TimeUnit.MILLISECONDS);
            if (!completed) {
                LOGGER.warning("Rollback phase timed out for transaction " + transactionId);
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            LOGGER.warning("Rollback phase interrupted for transaction " + transactionId);
        }
    }

    /**
     * Validates that the specified transaction is active.
     *
     * @param transactionId The ID of the transaction to validate.
     * @throws IllegalStateException If the transaction does not exist or is not active.
     */
    private void validateTransactionActive(String transactionId) {
        if (!transactionParticipants.containsKey(transactionId)) {
            throw new IllegalStateException("Transaction does not exist: " + transactionId);
        }
        
        TransactionState state = transactionStates.get(transactionId);
        if (state != TransactionState.ACTIVE) {
            throw new IllegalStateException("Transaction is not in active state: " + transactionId + " (current state: " + state + ")");
        }
    }

    /**
     * Generates a unique transaction ID.
     *
     * @return A unique transaction ID.
     */
    private String generateTransactionId() {
        return UUID.randomUUID().toString();
    }
    
    /**
     * Shutdowns the DTM instance, closing resources.
     */
    public void shutdown() {
        executorService.shutdown();
        try {
            if (!executorService.awaitTermination(5, TimeUnit.SECONDS)) {
                executorService.shutdownNow();
            }
        } catch (InterruptedException e) {
            executorService.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }
}