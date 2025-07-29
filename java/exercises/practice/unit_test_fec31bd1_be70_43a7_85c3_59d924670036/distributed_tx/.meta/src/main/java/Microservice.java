import java.io.Serializable;

public interface Microservice {
    boolean prepare(TransactionContext context);
    void commit(TransactionContext context);
    void rollback(TransactionContext context);
}