/**
 * Represents an operation to be executed on a shard in a distributed transaction.
 */
public class Operation {
    private final int shardId;
    private final OperationType operationType;
    private final String key;
    private final String value; // Only used for WRITE operations
    
    /**
     * Constructs a new Operation.
     * 
     * @param shardId The ID of the target shard.
     * @param operationType The type of operation (READ or WRITE).
     * @param key The key to access in the shard.
     * @param value The value to write (only for WRITE operations, can be null for READ operations).
     */
    public Operation(int shardId, OperationType operationType, String key, String value) {
        this.shardId = shardId;
        this.operationType = operationType;
        this.key = key;
        this.value = value;
    }
    
    /**
     * Gets the ID of the target shard.
     * 
     * @return The shard ID.
     */
    public int getShardId() {
        return shardId;
    }
    
    /**
     * Gets the type of operation.
     * 
     * @return The operation type.
     */
    public OperationType getOperationType() {
        return operationType;
    }
    
    /**
     * Gets the key to access in the shard.
     * 
     * @return The key.
     */
    public String getKey() {
        return key;
    }
    
    /**
     * Gets the value to write (only for WRITE operations).
     * 
     * @return The value, or null for READ operations.
     */
    public String getValue() {
        return value;
    }
    
    @Override
    public String toString() {
        return "Operation{" +
                "shardId=" + shardId +
                ", operationType=" + operationType +
                ", key='" + key + '\'' +
                ", value='" + value + '\'' +
                '}';
    }
}