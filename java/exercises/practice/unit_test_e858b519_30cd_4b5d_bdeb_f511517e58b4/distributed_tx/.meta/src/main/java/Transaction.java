package distributed_tx;

public class Transaction {
    private String transactionId;
    private String sourceAccountId;
    private String destinationAccountId;
    private double amount;

    public Transaction(String transactionId, String sourceAccountId, String destinationAccountId, double amount) {
        this.transactionId = transactionId;
        this.sourceAccountId = sourceAccountId;
        this.destinationAccountId = destinationAccountId;
        this.amount = amount;
    }

    public String getTransactionId() {
        return transactionId;
    }

    public String getSourceAccountId() {
        return sourceAccountId;
    }

    public String getDestinationAccountId() {
        return destinationAccountId;
    }

    public double getAmount() {
        return amount;
    }
}