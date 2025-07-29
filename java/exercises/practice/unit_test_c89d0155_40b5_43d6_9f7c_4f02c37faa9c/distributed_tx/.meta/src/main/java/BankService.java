public interface BankService {
    boolean debit(String accountId, double amount) throws InsufficientFundsException;
    boolean credit(String accountId, double amount);
    boolean prepare(String transactionId, java.util.List<Operation> operations);
    boolean commit(String transactionId);
    boolean rollback(String transactionId);
}