package distributed_tx;

public interface BranchService {
    boolean prepare(String transactionId);
    void commit(String transactionId);
    void rollback(String transactionId);
}