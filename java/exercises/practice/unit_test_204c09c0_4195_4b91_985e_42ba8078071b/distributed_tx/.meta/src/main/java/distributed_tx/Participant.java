package distributed_tx;

public interface Participant {
    boolean prepare() throws Exception;
    void commit() throws Exception;
    void rollback() throws Exception;
}