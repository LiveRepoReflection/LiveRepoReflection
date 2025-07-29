public interface TransactionParticipant {
    boolean prepare(String txId);
    boolean commit(String txId);
    boolean rollback(String txId);
}