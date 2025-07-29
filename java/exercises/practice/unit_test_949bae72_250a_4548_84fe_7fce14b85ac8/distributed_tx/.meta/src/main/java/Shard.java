public interface Shard {
    boolean prepare(String transactionId, String data);
    void commit(String transactionId);
    void abort(String transactionId);
    TransactionStatus getStatus(String transactionId);
}