public class TransactionOperation {
    public String bankId;
    public String accountId;
    public double amount;
    public boolean readOnly;

    public TransactionOperation(String bankId, String accountId, double amount, boolean readOnly) {
        this.bankId = bankId;
        this.accountId = accountId;
        this.amount = amount;
        this.readOnly = readOnly;
    }
}