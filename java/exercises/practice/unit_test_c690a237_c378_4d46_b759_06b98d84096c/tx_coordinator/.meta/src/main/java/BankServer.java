import java.util.List;

public interface BankServer {
    boolean prepare(String transactionId, List<Operation> operations) throws Exception;
    void commit(String transactionId);
    void rollback(String transactionId);
}