package distributed_tx;

public interface BankServer {
    boolean prepare(Transaction transaction) throws Exception;
    void commit(Transaction transaction) throws Exception;
    void rollback(Transaction transaction) throws Exception;
}