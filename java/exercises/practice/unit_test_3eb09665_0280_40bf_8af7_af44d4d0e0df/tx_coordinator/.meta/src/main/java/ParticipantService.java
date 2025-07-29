package tx_coordinator;

public interface ParticipantService {
    boolean prepare(String txId);
    boolean commit(String txId);
    boolean rollback(String txId);
}