public interface BankService {
    boolean debit(String accountId, double amount);
    boolean credit(String accountId, double amount);
    boolean prepareDebit(String accountId, double amount);
    boolean prepareCredit(String accountId, double amount);
    boolean commitDebit(String accountId, double amount);
    boolean commitCredit(String accountId, double amount);
    boolean rollbackDebit(String accountId, double amount);
    boolean rollbackCredit(String accountId, double amount);
    boolean isAlive();
}