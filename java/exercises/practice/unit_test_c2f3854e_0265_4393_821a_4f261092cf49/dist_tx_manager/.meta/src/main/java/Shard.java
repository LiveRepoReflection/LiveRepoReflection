import java.util.List;

/**
 * Interface representing a database shard in a distributed database system.
 */
public interface Shard {
    
    /**
     * Reads the value associated with the given key from the shard.
     * 
     * @param key The key to read.
     * @return The value associated with the key, or null if the key does not exist.
     */
    String read(String key);
    
    /**
     * Writes the given value to the given key in the shard.
     * 
     * @param key The key to write to.
     * @param value The value to write.
     * @return true if the write was successful, false otherwise.
     */
    boolean write(String key, String value);
    
    /**
     * Prepares the shard for a transaction, verifying that the operations can be executed.
     * This is the first phase of the two-phase commit protocol.
     * 
     * @param transactionId The ID of the transaction.
     * @param operations The list of operations to prepare.
     * @return true if the shard is prepared to execute the operations, false otherwise.
     */
    boolean prepare(String transactionId, List<Operation> operations);
    
    /**
     * Commits the transaction on the shard.
     * This is the second phase of the two-phase commit protocol.
     * 
     * @param transactionId The ID of the transaction to commit.
     * @return true if the commit was successful, false otherwise.
     */
    boolean commit(String transactionId);
    
    /**
     * Rolls back the transaction on the shard.
     * 
     * @param transactionId The ID of the transaction to roll back.
     * @return true if the rollback was successful, false otherwise.
     */
    boolean rollback(String transactionId);
}