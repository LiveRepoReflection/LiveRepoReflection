package distributed_tx;

public interface Participant {
    boolean prepare(Transaction tx) throws Exception;
    void commit(Transaction tx) throws Exception;
    void abort(Transaction tx) throws Exception;
}