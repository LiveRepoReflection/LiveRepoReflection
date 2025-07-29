package distributed_tx;

public interface Participant {
    ParticipantResponse prepare(Transaction transaction) throws InterruptedException;
    void commit(Transaction transaction);
    void abort(Transaction transaction);
    void recover(Transaction transaction);
}