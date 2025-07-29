package tx_manager;

public interface Participant {
    enum Vote {
        COMMIT,
        ABORT
    }

    Vote prepare(String transactionId);
    void commit(String transactionId);
    void rollback(String transactionId);
}