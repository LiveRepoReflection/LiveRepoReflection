package distributed_tx;

public class TransactionOperation {
    private final String accountId;
    private final double amount;

    public TransactionOperation(String accountId, double amount) {
        this.accountId = accountId;
        this.amount = amount;
    }

    public String getAccountId() {
        return accountId;
    }

    public double getAmount() {
        return amount;
    }
}