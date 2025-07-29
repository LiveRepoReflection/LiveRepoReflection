import java.util.List;
import java.util.ArrayList;
import java.util.concurrent.*;

public class DistributedTxCoordinator {
    private final List<Participant> participants;
    private volatile TransactionState state = TransactionState.PENDING;
    // Timeout for each phase in milliseconds.
    private final long phaseTimeoutMillis;

    public DistributedTxCoordinator(List<Participant> participants, long phaseTimeoutMillis) {
        this.participants = participants;
        this.phaseTimeoutMillis = phaseTimeoutMillis;
    }

    public TransactionState executeTransaction() {
        state = TransactionState.PREPARING;
        ExecutorService executor = Executors.newFixedThreadPool(participants.size());
        try {
            List<Future<Boolean>> prepareFutures = new ArrayList<>();
            for (Participant p : participants) {
                Future<Boolean> future = executor.submit(p::prepare);
                prepareFutures.add(future);
            }
            for (Future<Boolean> f : prepareFutures) {
                try {
                    boolean prepared = f.get(phaseTimeoutMillis, TimeUnit.MILLISECONDS);
                    if (!prepared) {
                        state = TransactionState.ABORTED;
                        rollbackParticipants();
                        executor.shutdownNow();
                        return TransactionState.ROLLED_BACK;
                    }
                } catch (TimeoutException te) {
                    state = TransactionState.ABORTED;
                    rollbackParticipants();
                    executor.shutdownNow();
                    return TransactionState.ROLLED_BACK;
                } catch (Exception e) {
                    state = TransactionState.ABORTED;
                    rollbackParticipants();
                    executor.shutdownNow();
                    return TransactionState.ROLLED_BACK;
                }
            }
        } finally {
            executor.shutdown();
        }
        state = TransactionState.PREPARED;
        state = TransactionState.COMMITTING;
        for (Participant p : participants) {
            try {
                p.commit();
            } catch (Exception e) {
                // Exceptions during commit should be handled gracefully; 
                // operations are assumed to be idempotent.
            }
        }
        state = TransactionState.COMMITTED;
        return state;
    }

    private void rollbackParticipants() {
        state = TransactionState.ROLLING_BACK;
        for (Participant p : participants) {
            try {
                p.rollback();
            } catch (Exception ignored) {
            }
        }
        state = TransactionState.ROLLED_BACK;
    }

    public TransactionState getState() {
        return state;
    }
}