package distributed_tx;

public interface TransactionParticipant {
    boolean prepare() throws Exception;
    void commit() throws Exception;
    void rollback() throws Exception;
}