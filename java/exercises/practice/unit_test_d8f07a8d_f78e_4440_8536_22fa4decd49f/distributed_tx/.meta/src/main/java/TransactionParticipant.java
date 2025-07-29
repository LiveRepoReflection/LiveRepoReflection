/**
 * Interface that must be implemented by all services that participate in distributed transactions.
 * This interface defines the callback methods required for the Two-Phase Commit protocol.
 */
public interface TransactionParticipant {
    
    /**
     * Phase 1 of the Two-Phase Commit protocol.
     * Services should attempt to prepare the transaction but not commit it yet.
     * This typically involves validating the data and acquiring necessary resources.
     * 
     * @param txId The unique transaction identifier
     * @param data The data to be processed as part of this transaction
     * @return true if the service successfully prepared, false if it cannot proceed
     */
    boolean prepare(String txId, Object data);
    
    /**
     * Phase 2 of the Two-Phase Commit protocol - commit.
     * Called if all participating services successfully completed the prepare phase.
     * Services should finalize the changes initiated during the prepare phase.
     * 
     * @param txId The unique transaction identifier
     */
    void commit(String txId);
    
    /**
     * Phase 2 of the Two-Phase Commit protocol - rollback.
     * Called if any participating service failed during the prepare phase.
     * Services should undo any changes made during the prepare phase.
     * 
     * @param txId The unique transaction identifier
     */
    void rollback(String txId);
}