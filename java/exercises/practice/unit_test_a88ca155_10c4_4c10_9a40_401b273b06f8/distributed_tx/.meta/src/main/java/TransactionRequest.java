package distributed_tx;

public class TransactionRequest {
    public final String transactionId;
    public final String serviceAAccountId;
    public final String serviceBAccountId;
    public final double amount;
    public final int serviceAExpectedVersion;
    public final int serviceBExpectedVersion;

    public TransactionRequest(String transactionId, String serviceAAccountId, String serviceBAccountId, double amount, int serviceAExpectedVersion, int serviceBExpectedVersion) {
        this.transactionId = transactionId;
        this.serviceAAccountId = serviceAAccountId;
        this.serviceBAccountId = serviceBAccountId;
        this.amount = amount;
        this.serviceAExpectedVersion = serviceAExpectedVersion;
        this.serviceBExpectedVersion = serviceBExpectedVersion;
    }
}