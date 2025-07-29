import java.util.ArrayList;
import java.util.List;

public class DistTxCoordinator {
    private final long timeoutMillis;
    
    public DistTxCoordinator(long timeoutMillis) {
        this.timeoutMillis = timeoutMillis;
    }
    
    public boolean executeTransaction(Transaction transaction, Participant[] participants) {
        List<Participant> preparedParticipants = new ArrayList<>();
        long startTime;
        long elapsedTime;
        
        // Phase 1: Prepare Phase
        for (Participant p : participants) {
            startTime = System.currentTimeMillis();
            System.out.println("Sending prepare request to participant: " + p);
            boolean vote = p.prepare(transaction);
            elapsedTime = System.currentTimeMillis() - startTime;
            if (elapsedTime > timeoutMillis) {
                System.out.println("Participant timed out: " + p);
                vote = false;
            }
            if (vote) {
                System.out.println("Participant voted COMMIT: " + p);
                preparedParticipants.add(p);
            } else {
                System.out.println("Participant voted ABORT: " + p);
                rollbackAll(transaction, participants);
                return false;
            }
        }
        
        // Phase 2: Commit Phase
        for (Participant p : participants) {
            try {
                System.out.println("Sending commit request to participant: " + p);
                p.commit(transaction);
            } catch (Exception e) {
                System.out.println("Exception during commit for participant: " + p + ". Exception: " + e);
            }
        }
        return true;
    }
    
    private void rollbackAll(Transaction transaction, Participant[] participants) {
        for (Participant p : participants) {
            try {
                System.out.println("Sending rollback request to participant: " + p);
                p.rollback(transaction);
            } catch (Exception e) {
                System.out.println("Exception during rollback for participant: " + p + ". Exception: " + e);
            }
        }
    }
}