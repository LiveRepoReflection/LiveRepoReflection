public interface BankService {
    boolean prepare(String transactionId, String accountId, double amount);
    boolean commit(String transactionId, String accountId, double amount);
    boolean rollback(String transactionId, String accountId, double amount);
    double getBalance(String accountId);
}