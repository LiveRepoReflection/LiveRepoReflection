import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.locks.ReadWriteLock;
import java.util.concurrent.locks.ReentrantReadWriteLock;

/**
 * Represents a distributed transaction with a unique ID and a list of participants.
 * This class is thread-safe to support concurrent access.
 */
public class Transaction {
    private final String id;
    private final List<Participant> participants;
    private final ReadWriteLock lock;
    
    /**
     * Constructs a new Transaction with the given ID.
     *
     * @param id The transaction ID
     */
    public Transaction(String id) {
        this.id = id;
        this.participants = new ArrayList<>();
        this.lock = new ReentrantReadWriteLock();
    }
    
    /**
     * Returns the transaction ID.
     *
     * @return The transaction ID
     */
    public String getId() {
        return id;
    }
    
    /**
     * Registers a participant with this transaction.
     *
     * @param participant The participant to register
     */
    public void registerParticipant(Participant participant) {
        lock.writeLock().lock();
        try {
            participants.add(participant);
        } finally {
            lock.writeLock().unlock();
        }
    }
    
    /**
     * Returns an unmodifiable list of participants in this transaction.
     *
     * @return The list of participants
     */
    public List<Participant> getParticipants() {
        lock.readLock().lock();
        try {
            return Collections.unmodifiableList(new ArrayList<>(participants));
        } finally {
            lock.readLock().unlock();
        }
    }
    
    @Override
    public String toString() {
        return "Transaction[id=" + id + ", participants=" + participants.size() + "]";
    }
}