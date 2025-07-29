public interface ParticipantService {
    boolean prepare(String transactionId);
    boolean commit(String transactionId);
    boolean rollback(String transactionId);
}