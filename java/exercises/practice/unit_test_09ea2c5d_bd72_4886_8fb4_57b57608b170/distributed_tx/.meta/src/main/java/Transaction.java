package distributed_tx;

public class Transaction {
    private final String transactionId;
    private final double amount;
    private final String fromAccount;
    private final String toAccount;

    public Transaction(String transactionId, double amount, String fromAccount, String toAccount) {
        this.transactionId = transactionId;
        this.amount = amount;
        this.fromAccount = fromAccount;
        this.toAccount = toAccount;
    }

    public String getTransactionId() {
        return transactionId;
    }

    public double getAmount() {
        return amount;
    }

    public String getFromAccount() {
        return fromAccount;
    }

    public String getToAccount() {
        return toAccount;
    }
}