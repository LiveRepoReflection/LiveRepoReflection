public interface BankService {
    boolean prepare(String transactionId);
    void commit(String transactionId);
    void rollback(String transactionId);
}