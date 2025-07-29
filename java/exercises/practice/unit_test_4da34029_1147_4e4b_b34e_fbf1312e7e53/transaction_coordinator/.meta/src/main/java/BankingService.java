package transaction_coordinator;

public interface BankingService {
    boolean prepare(String transactionId);
    void commit(String transactionId);
    void rollback(String transactionId);
}