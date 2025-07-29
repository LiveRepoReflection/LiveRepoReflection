import java.util.List;

public class DistributedTransactionManager {

    /**
     * Executes a distributed transaction using the two-phase commit protocol.
     *
     * Phase 1: Prepare all participants. If any participant fails to prepare, then the transaction will be aborted.
     * Phase 2: If all participants prepare successfully, commit the transaction; otherwise, rollback the transaction.
     *
     * @param participants List of participants involved in the transaction.
     * @return true if the transaction commits successfully; false if it is rolled back.
     */
    public boolean executeTransaction(List<TransactionParticipant> participants) {
        boolean allPrepared = true;
        
        // Phase 1: Prepare phase
        for (TransactionParticipant participant : participants) {
            boolean prepared = participant.prepare();
            if (!prepared) {
                allPrepared = false;
                break;
            }
        }
        
        // Phase 2: Commit or rollback phase based on the preparation results.
        if (allPrepared) {
            for (TransactionParticipant participant : participants) {
                participant.commit();
            }
            return true;
        } else {
            for (TransactionParticipant participant : participants) {
                participant.rollback();
            }
            return false;
        }
    }
}