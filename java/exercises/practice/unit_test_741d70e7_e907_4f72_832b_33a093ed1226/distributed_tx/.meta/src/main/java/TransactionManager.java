import java.util.*;
import java.util.concurrent.*;
import java.util.logging.Logger;

/**
 * The TransactionManager coordinates distributed transactions across multiple services.
 * It implements a simplified two-phase commit (2PC) protocol.
 */
public class TransactionManager {
    private static final Logger logger = Logger.getLogger(TransactionManager.class.getName());
    
    private final Map<String, Transaction> transactions;
    private final long timeoutMillis;
    private final ExecutorService executorService;
    
    /**
     * Creates a transaction manager with default timeout (30 seconds).
     */
    public TransactionManager() {
        this(30000); // Default 30 seconds timeout
    }
    
    /**
     * Creates a transaction manager with a specified timeout.
     * 
     * @param timeoutMillis the timeout in milliseconds for transaction operations
     */
    public TransactionManager(long timeoutMillis) {
        this.transactions = new ConcurrentHashMap<>();
        this.timeoutMillis = timeoutMillis;
        this.executorService = Executors.newCachedThreadPool();
    }
    
    /**
     * Begins a new transaction and returns a unique transaction ID.
     * 
     * @return the transaction ID
     */
    public String beginTransaction() {
        String transactionId = UUID.randomUUID().toString();
        Transaction transaction = new Transaction(transactionId);
        transactions.put(transactionId, transaction);
        logger.info("Started transaction: " + transactionId);
        return transactionId;
    }
    
    /**
     * Registers a participant for a specified transaction.
     * 
     * @param transactionId the transaction ID
     * @param participant the participant service
     * @throws IllegalArgumentException if the transaction is not found
     * @throws IllegalStateException if the transaction is not in ACTIVE state
     */
    public void registerParticipant(String transactionId, ParticipantService participant) {
        Transaction transaction = getTransaction(transactionId);
        if (transaction.getStatus() != TransactionStatus.ACTIVE) {
            throw new IllegalStateException("Cannot register participant: transaction is not active");
        }
        
        transaction.addParticipant(participant);
        logger.info(String.format("Registered %s for transaction %s", 
                participant.getName(), transactionId));
    }
    
    /**
     * Commits a transaction using the two-phase commit protocol.
     * 
     * @param transactionId the transaction ID
     * @return true if the transaction was committed successfully, false otherwise
     * @throws IllegalArgumentException if the transaction is not found
     */
    public boolean commitTransaction(String transactionId) {
        Transaction transaction = getTransaction(transactionId);
        
        if (transaction.getStatus() != TransactionStatus.ACTIVE) {
            logger.warning(String.format("Cannot commit transaction %s with status %s", 
                    transactionId, transaction.getStatus()));
            return false;
        }
        
        try {
            // Phase 1: Prepare
            logger.info("Beginning prepare phase for transaction: " + transactionId);
            if (!preparePhase(transaction)) {
                rollbackTransaction(transactionId);
                return false;
            }
            
            // Phase 2: Commit
            logger.info("Beginning commit phase for transaction: " + transactionId);
            commitPhase(transaction);
            transaction.setStatus(TransactionStatus.COMMITTED);
            logger.info("Transaction committed successfully: " + transactionId);
            return true;
            
        } catch (Exception e) {
            logger.severe(String.format("Error during commit of transaction %s: %s", 
                    transactionId, e.getMessage()));
            rollbackTransaction(transactionId);
            return false;
        }
    }
    
    /**
     * Rolls back a transaction.
     * 
     * @param transactionId the transaction ID
     * @throws IllegalArgumentException if the transaction is not found
     */
    public void rollbackTransaction(String transactionId) {
        Transaction transaction = getTransaction(transactionId);
        
        // If already rolled back, do nothing
        if (transaction.getStatus() == TransactionStatus.ROLLED_BACK) {
            return;
        }
        
        logger.info("Rolling back transaction: " + transactionId);
        
        // Signal all participants to rollback
        for (ParticipantService participant : transaction.getParticipants()) {
            try {
                participant.rollback(transactionId);
                logger.info(String.format("Participant %s rolled back transaction %s", 
                        participant.getName(), transactionId));
            } catch (Exception e) {
                logger.warning(String.format("Error rolling back participant %s for transaction %s: %s", 
                        participant.getName(), transactionId, e.getMessage()));
                // Continue with other participants even if one fails
            }
        }
        
        transaction.setStatus(TransactionStatus.ROLLED_BACK);
        logger.info("Transaction rolled back: " + transactionId);
    }
    
    /**
     * Returns the current status of a transaction.
     * 
     * @param transactionId the transaction ID
     * @return the transaction status
     * @throws IllegalArgumentException if the transaction is not found
     */
    public TransactionStatus getTransactionStatus(String transactionId) {
        return getTransaction(transactionId).getStatus();
    }
    
    /**
     * Handles the prepare phase of the two-phase commit protocol.
     * 
     * @param transaction the transaction
     * @return true if all participants successfully prepared, false otherwise
     */
    private boolean preparePhase(Transaction transaction) {
        List<ParticipantService> participants = transaction.getParticipants();
        
        if (participants.isEmpty()) {
            // No participants, consider the transaction prepared
            return true;
        }
        
        transaction.setStatus(TransactionStatus.PREPARING);
        
        // Create a list to hold future results
        List<Future<ParticipantStatus>> prepareFutures = new ArrayList<>();
        
        // Ask each participant to prepare
        for (ParticipantService participant : participants) {
            Future<ParticipantStatus> future = executorService.submit(() -> {
                try {
                    ParticipantStatus status = participant.prepare(transaction.getId());
                    logger.info(String.format("Participant %s returned status %s for transaction %s", 
                            participant.getName(), status, transaction.getId()));
                    return status;
                } catch (Exception e) {
                    logger.warning(String.format("Participant %s failed during prepare for transaction %s: %s", 
                            participant.getName(), transaction.getId(), e.getMessage()));
                    return ParticipantStatus.ABORT;
                }
            });
            
            prepareFutures.add(future);
        }
        
        // Wait for all participants to respond
        try {
            for (Future<ParticipantStatus> future : prepareFutures) {
                ParticipantStatus status = future.get(timeoutMillis, TimeUnit.MILLISECONDS);
                if (status != ParticipantStatus.PREPARED) {
                    // If any participant is not prepared, abort
                    logger.warning("Participant not prepared, aborting transaction: " + transaction.getId());
                    return false;
                }
            }
            
            transaction.setStatus(TransactionStatus.PREPARED);
            return true;
            
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            logger.severe("Thread interrupted during prepare phase");
            return false;
        } catch (ExecutionException e) {
            logger.severe("Execution error during prepare phase: " + e.getMessage());
            return false;
        } catch (TimeoutException e) {
            logger.severe("Timeout occurred during prepare phase");
            return false;
        }
    }
    
    /**
     * Handles the commit phase of the two-phase commit protocol.
     * 
     * @param transaction the transaction
     */
    private void commitPhase(Transaction transaction) {
        transaction.setStatus(TransactionStatus.COMMITTING);
        
        // Create a list to hold future results
        List<Future<Void>> commitFutures = new ArrayList<>();
        
        // Ask each participant to commit
        for (ParticipantService participant : transaction.getParticipants()) {
            Future<Void> future = executorService.submit(() -> {
                try {
                    participant.commit(transaction.getId());
                    logger.info(String.format("Participant %s committed transaction %s", 
                            participant.getName(), transaction.getId()));
                    return null;
                } catch (Exception e) {
                    logger.severe(String.format("Participant %s failed during commit for transaction %s: %s", 
                            participant.getName(), transaction.getId(), e.getMessage()));
                    throw e; // Re-throw to be caught by future.get()
                }
            });
            
            commitFutures.add(future);
        }
        
        // Wait for all participants to commit
        try {
            for (Future<Void> future : commitFutures) {
                future.get(timeoutMillis, TimeUnit.MILLISECONDS);
            }
        } catch (Exception e) {
            logger.severe(String.format("Error during commit phase: %s. Transaction is in an inconsistent state.", 
                    e.getMessage()));
            // In a real system, we would need a recovery mechanism here
            // For this simplified version, we'll just log the error
        }
    }
    
    /**
     * Helper method to get a transaction by ID.
     * 
     * @param transactionId the transaction ID
     * @return the transaction
     * @throws IllegalArgumentException if the transaction is not found
     */
    private Transaction getTransaction(String transactionId) {
        Transaction transaction = transactions.get(transactionId);
        if (transaction == null) {
            throw new IllegalArgumentException("Transaction not found: " + transactionId);
        }
        return transaction;
    }
    
    /**
     * Shutdown the transaction manager.
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