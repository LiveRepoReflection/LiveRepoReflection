package distributed_tx;

public interface Participant {
    boolean prepare();
    void commit();
    void rollback();
    String getName();
}