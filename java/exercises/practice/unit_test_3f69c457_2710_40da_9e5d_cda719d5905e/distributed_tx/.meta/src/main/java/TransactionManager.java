package distributed_tx;

public class TransactionManager {
    private long timeout = 1000;
    private int maxRetries = 3;
    private long retryInterval = 500;

    public Transaction createTransaction() {
        return new Transaction(timeout, maxRetries, retryInterval);
    }

    public void setTimeout(long timeout) {
        this.timeout = timeout;
    }

    public void setMaxRetries(int maxRetries) {
        this.maxRetries = maxRetries;
    }

    public void setRetryInterval(long retryInterval) {
        this.retryInterval = retryInterval;
    }
}