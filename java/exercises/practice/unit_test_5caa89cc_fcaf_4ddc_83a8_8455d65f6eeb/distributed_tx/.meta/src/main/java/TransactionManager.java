import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * TransactionManager is the core component of the Distributed Transaction Manager.
 * It handles the two-phase commit protocol for coordinating transactions across multiple participants.
 */
public class TransactionManager {
    private static final Logger LOGGER = Logger.getLogger(TransactionManager.class.getName());
    
    // Default timeout for prepare phase in milliseconds
    private long timeout = 5000;
    
    // Thread pool for executing prepare operations concurrently
    private final ExecutorService executorService;
    
    // Map to store active transactions
    private final Map<String, Transaction> transactions;
    
    /**
     * Constructs a new TransactionManager with a default thread pool.
     */
    public TransactionManager() {
        // Using a cached thread pool to adapt to the workload dynamically
        this.executorService = Executors.newCachedThreadPool(r -> {
            Thread thread = new Thread(r, "DTM-Worker");
            thread.setDaemon(true); // Using daemon threads to avoid preventing JVM shutdown
            return thread;
        });
        this.transactions = new ConcurrentHashMap<>();
    }
    
    /**
     * Starts a new transaction and returns its ID.
     *
     * @return The transaction ID
     */
    public String startTransaction() {
        String txId = UUID.randomUUID().toString();
        LOGGER.log(Level.INFO, "Starting transaction: {0}", txId);
        
        transactions.put(txId, new Transaction(txId));
        return txId;
    }
    
    /**
     * Registers a participant with a transaction.
     *
     * @param txId The transaction ID
     * @param participant The participant to register
     * @throws IllegalArgumentException If the transaction does not exist
     */
    public void registerParticipant(String txId, Participant participant) {
        Transaction tx = transactions.get(txId);
        if (tx == null) {
            throw new IllegalArgumentException("Transaction not found: " + txId);
        }
        
        tx.registerParticipant(participant);
        LOGGER.log(Level.INFO, "Registered participant {0} with transaction {1}", 
                new Object[]{participant, txId});
    }
    
    /**
     * Executes a transaction using the two-phase commit protocol.
     *
     * @param txId The transaction ID
     * @return true if the transaction was committed, false if it was rolled back
     * @throws IllegalArgumentException If the transaction does not exist
     */
    public boolean executeTransaction(String txId) {
        Transaction tx = transactions.get(txId);
        if (tx == null) {
            throw new IllegalArgumentException("Transaction not found: " + txId);
        }
        
        try {
            LOGGER.log(Level.INFO, "Executing transaction: {0}", txId);
            
            // Phase 1: Prepare
            boolean prepareSuccess = preparePhase(tx);
            
            // Phase 2: Commit or Rollback
            if (prepareSuccess) {
                commitPhase(tx);
                LOGGER.log(Level.INFO, "Transaction {0} committed successfully", txId);
                return true;
            } else {
                rollbackPhase(tx);
                LOGGER.log(Level.INFO, "Transaction {0} rolled back after prepare failure", txId);
                return false;
            }
        } catch (Exception e) {
            LOGGER.log(Level.SEVERE, "Error executing transaction " + txId, e);
            rollbackPhase(tx);
            return false;
        } finally {
            // Clean up the transaction
            transactions.remove(txId);
        }
    }
    
    /**
     * Executes the prepare phase of the two-phase commit protocol.
     *
     * @param tx The transaction
     * @return true if all participants prepared successfully, false otherwise
     */
    private boolean preparePhase(Transaction tx) {
        List<Participant> participants = tx.getParticipants();
        if (participants.isEmpty()) {
            LOGGER.log(Level.WARNING, "Transaction {0} has no participants", tx.getId());
            return true;
        }
        
        LOGGER.log(Level.INFO, "Starting prepare phase for transaction {0} with {1} participants",
                new Object[]{tx.getId(), participants.size()});
        
        List<Future<Boolean>> futures = new ArrayList<>();
        
        // Submit prepare tasks to executor service for concurrent execution
        for (Participant participant : participants) {
            futures.add(executorService.submit(() -> {
                try {
                    LOGGER.log(Level.FINE, "Preparing participant {0} for transaction {1}", 
                            new Object[]{participant, tx.getId()});
                    return participant.prepare();
                } catch (Exception e) {
                    LOGGER.log(Level.SEVERE, "Error preparing participant " + participant, e);
                    return false;
                }
            }));
        }
        
        // Wait for all prepare operations to complete or timeout
        for (int i = 0; i < futures.size(); i++) {
            try {
                boolean result = futures.get(i).get(timeout, TimeUnit.MILLISECONDS);
                if (!result) {
                    LOGGER.log(Level.WARNING, "Participant {0} failed to prepare for transaction {1}",
                            new Object[]{participants.get(i), tx.getId()});
                    return false;
                }
            } catch (TimeoutException e) {
                LOGGER.log(Level.WARNING, "Timeout waiting for participant {0} to prepare for transaction {1}",
                        new Object[]{participants.get(i), tx.getId()});
                futures.get(i).cancel(true);
                return false;
            } catch (Exception e) {
                LOGGER.log(Level.SEVERE, "Error waiting for participant " + participants.get(i) + " to prepare", e);
                return false;
            }
        }
        
        LOGGER.log(Level.INFO, "All participants prepared successfully for transaction {0}", tx.getId());
        return true;
    }
    
    /**
     * Executes the commit phase of the two-phase commit protocol.
     *
     * @param tx The transaction
     */
    private void commitPhase(Transaction tx) {
        List<Participant> participants = tx.getParticipants();
        
        LOGGER.log(Level.INFO, "Starting commit phase for transaction {0}", tx.getId());
        
        for (Participant participant : participants) {
            try {
                LOGGER.log(Level.FINE, "Committing participant {0} for transaction {1}", 
                        new Object[]{participant, tx.getId()});
                participant.commit();
            } catch (Exception e) {
                // Log error but continue with other participants
                // In a real system, we might need more sophisticated recovery mechanisms
                LOGGER.log(Level.SEVERE, "Error committing participant " + participant, e);
            }
        }
    }
    
    /**
     * Executes the rollback phase of the two-phase commit protocol.
     *
     * @param tx The transaction
     */
    private void rollbackPhase(Transaction tx) {
        List<Participant> participants = tx.getParticipants();
        
        LOGGER.log(Level.INFO, "Starting rollback phase for transaction {0}", tx.getId());
        
        for (Participant participant : participants) {
            try {
                LOGGER.log(Level.FINE, "Rolling back participant {0} for transaction {1}", 
                        new Object[]{participant, tx.getId()});
                participant.rollback();
            } catch (Exception e) {
                // Log error but continue with other participants
                LOGGER.log(Level.SEVERE, "Error rolling back participant " + participant, e);
            }
        }
    }
    
    /**
     * Sets the timeout for the prepare phase in milliseconds.
     *
     * @param timeout The timeout in milliseconds
     */
    public void setTimeout(long timeout) {
        this.timeout = timeout;
    }
    
    /**
     * Shuts down the transaction manager, releasing any resources.
     */
    public void shutdown() {
        executorService.shutdown();
        try {
            if (!executorService.awaitTermination(10, TimeUnit.SECONDS)) {
                executorService.shutdownNow();
            }
        } catch (InterruptedException e) {
            executorService.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }
}