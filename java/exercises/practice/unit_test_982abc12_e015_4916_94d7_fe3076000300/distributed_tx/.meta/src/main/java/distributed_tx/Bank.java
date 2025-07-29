package distributed_tx;

public interface Bank {
    boolean prepare(String transactionId, String accountId, double amount);
    boolean commit(String transactionId, String accountId, double amount);
    boolean rollback(String transactionId, String accountId, double amount);
    String getName();
}