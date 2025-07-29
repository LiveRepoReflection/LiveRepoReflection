import java.util.concurrent.ConcurrentHashMap;
import java.util.logging.Logger;

public class ParticipantImpl implements Participant {
    private static final Logger LOGGER = Logger.getLogger(ParticipantImpl.class.getName());
    
    private final String participantId;
    private final ConcurrentHashMap<String, TransactionState> transactionStates;

    public ParticipantImpl(String participantId) {
        this.participantId = participantId;
        this.transactionStates = new ConcurrentHashMap<>();
    }

    @Override
    public Vote prepare(Transaction transaction) throws Exception {
        LOGGER.info(participantId + ": Preparing transaction " + transaction.getId());
        
        // Simulate resource checking and preparation
        if (canCommit(transaction)) {
            transactionStates.put(transaction.getId(), TransactionState.PREPARED);
            return Vote.COMMIT;
        }
        
        return Vote.ROLLBACK;
    }

    @Override
    public void commit(Transaction transaction) throws Exception {
        LOGGER.info(participantId + ": Committing transaction " + transaction.getId());
        
        // Only commit if we're in the PREPARED state
        if (transactionStates.get(transaction.getId()) == TransactionState.PREPARED) {
            // Perform the actual commit operation
            doCommit(transaction);
            transactionStates.put(transaction.getId(), TransactionState.COMMITTED);
        }
    }

    @Override
    public void rollback(Transaction transaction) throws Exception {
        LOGGER.info(participantId + ": Rolling back transaction " + transaction.getId());
        
        // Perform the rollback operation
        doRollback(transaction);
        transactionStates.put(transaction.getId(), TransactionState.ROLLED_BACK);
    }

    private boolean canCommit(Transaction transaction) {
        // Implement actual resource checking logic here
        return true;
    }

    private void doCommit(Transaction transaction) {
        // Implement actual commit logic here
    }

    private void doRollback(Transaction transaction) {
        // Implement actual rollback logic here
    }
}