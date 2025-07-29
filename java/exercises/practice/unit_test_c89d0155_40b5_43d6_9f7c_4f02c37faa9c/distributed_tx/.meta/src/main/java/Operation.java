public class Operation {
    public final String accountId;
    public final double amount;
    public final OperationType type;

    public Operation(String accountId, double amount, OperationType type) {
        this.accountId = accountId;
        this.amount = amount;
        this.type = type;
    }
}