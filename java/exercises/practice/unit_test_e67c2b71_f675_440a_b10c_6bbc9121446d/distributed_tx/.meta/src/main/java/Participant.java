package distributed_tx;

public interface Participant {
    String getId();
    boolean prepare(Transaction tx);
    boolean commit(Transaction tx);
    boolean rollback(Transaction tx);
}