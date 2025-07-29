import java.util.List;

public interface Microservice {
    String prepare(int transactionId, List<Operation> operations);
    String commit(int transactionId);
    String rollback(int transactionId);
}