package distributed_tx;

public interface Participant {
    boolean prepare();
    boolean commit();
    boolean rollback();
}