package distributed_tx;

public interface Participant {
    // Simulate the prepare phase. Return true if voting commit, false otherwise.
    boolean prepare(String transactionId);
    
    // Process the commit command.
    void commit(String transactionId);
    
    // Process the abort command.
    void abort(String transactionId);
}