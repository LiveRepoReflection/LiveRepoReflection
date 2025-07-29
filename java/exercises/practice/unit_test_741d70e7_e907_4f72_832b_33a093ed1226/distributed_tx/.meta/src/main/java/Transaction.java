import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;

/**
 * Represents a distributed transaction.
 */
public class Transaction {
    private final String id;
    private TransactionStatus status;
    private final List<ParticipantService> participants;
    
    /**
     * Creates a new transaction with the given ID.
     * 
     * @param id the transaction ID
     */
    public Transaction(String id) {
        this.id = id;
        this.status = TransactionStatus.ACTIVE;
        this.participants = new CopyOnWriteArrayList<>();
    }
    
    /**
     * Returns the ID of this transaction.
     * 
     * @return the transaction ID
     */
    public String getId() {
        return id;
    }
    
    /**
     * Returns the current status of this transaction.
     * 
     * @return the transaction status
     */
    public TransactionStatus getStatus() {
        return status;
    }
    
    /**
     * Sets the status of this transaction.
     * 
     * @param status the new transaction status
     */
    public void setStatus(TransactionStatus status) {
        this.status = status;
    }
    
    /**
     * Adds a participant to this transaction.
     * 
     * @param participant the participant service
     */
    public void addParticipant(ParticipantService participant) {
        participants.add(participant);
    }
    
    /**
     * Returns a list of all participants in this transaction.
     * 
     * @return the list of participants
     */
    public List<ParticipantService> getParticipants() {
        return new ArrayList<>(participants);
    }
}