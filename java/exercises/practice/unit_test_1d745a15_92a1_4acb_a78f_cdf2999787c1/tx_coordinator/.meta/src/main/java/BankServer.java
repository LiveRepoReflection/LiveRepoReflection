public interface BankServer {
    boolean prepare(String transactionID, java.util.List<Operation> ops);
    void commit(String transactionID);
    void rollback(String transactionID);
}