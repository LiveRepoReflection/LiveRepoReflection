package distributed_tx;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.*;
import java.util.concurrent.locks.ReentrantLock;

public class TransactionManager {
    private final List<TransactionParticipant> participants;
    private final ReentrantLock lock = new ReentrantLock();
    private long timeoutMs = 5000; // default timeout in milliseconds
    private final ExecutorService executor = Executors.newCachedThreadPool();

    public TransactionManager() {
        participants = new ArrayList<>();
    }

    public void setTimeout(long timeout) {
        this.timeoutMs = timeout;
    }

    public void registerParticipant(TransactionParticipant participant) {
        lock.lock();
        try {
            participants.add(participant);
        } finally {
            lock.unlock();
        }
    }

    public boolean executeTransaction() {
        // Simulate persisting transaction metadata with an in-memory state.
        TransactionState state = TransactionState.PREPARING;
        boolean allPrepared = true;
        List<Future<Boolean>> prepareFutures = new ArrayList<>();

        for (TransactionParticipant participant : participants) {
            Future<Boolean> future = executor.submit(() -> {
                try {
                    return participant.prepare();
                } catch (Exception e) {
                    return false;
                }
            });
            prepareFutures.add(future);
        }

        long endTime = System.currentTimeMillis() + timeoutMs;
        try {
            for (Future<Boolean> future : prepareFutures) {
                long timeLeft = endTime - System.currentTimeMillis();
                if (timeLeft <= 0) {
                    allPrepared = false;
                    break;
                }
                try {
                    boolean prepared = future.get(timeLeft, TimeUnit.MILLISECONDS);
                    if (!prepared) {
                        allPrepared = false;
                        break;
                    }
                } catch (TimeoutException | ExecutionException | InterruptedException e) {
                    allPrepared = false;
                    break;
                }
            }
        } catch (Exception e) {
            allPrepared = false;
        }

        if (allPrepared) {
            state = TransactionState.COMMITTING;
            // Persist metadata update for commit phase.
            List<Future<?>> commitFutures = new ArrayList<>();
            for (TransactionParticipant participant : participants) {
                Future<?> future = executor.submit(() -> {
                    try {
                        participant.commit();
                    } catch (Exception e) {
                        // Idempotency ensures that repeated calls are safe.
                    }
                });
                commitFutures.add(future);
            }
            try {
                for (Future<?> future : commitFutures) {
                    long timeLeft = endTime - System.currentTimeMillis();
                    if (timeLeft <= 0) {
                        break;
                    }
                    future.get(timeLeft, TimeUnit.MILLISECONDS);
                }
            } catch (Exception e) {
                // If commit phase times out or fails, we simply proceed.
            }
            state = TransactionState.COMMITTED;
            return true;
        } else {
            state = TransactionState.ABORTING;
            // On failure, rollback all participants.
            List<Future<?>> rollbackFutures = new ArrayList<>();
            for (TransactionParticipant participant : participants) {
                Future<?> future = executor.submit(() -> {
                    try {
                        participant.rollback();
                    } catch (Exception e) {
                        // Ignore rollback exceptions to ensure idempotency.
                    }
                });
                rollbackFutures.add(future);
            }
            try {
                for (Future<?> future : rollbackFutures) {
                    long timeLeft = endTime - System.currentTimeMillis();
                    if (timeLeft <= 0) {
                        break;
                    }
                    future.get(timeLeft, TimeUnit.MILLISECONDS);
                }
            } catch (Exception e) {
                // Not waiting any further.
            }
            state = TransactionState.ABORTED;
            return false;
        }
    }

    public void recoverTransaction(TransactionState state) {
        // Simulated recovery mechanism. In a real system, this would check persisted transaction metadata.
    }

    public void shutdown() {
        executor.shutdown();
    }

    public enum TransactionState {
        PREPARING,
        COMMITTING,
        COMMITTED,
        ABORTING,
        ABORTED
    }
}