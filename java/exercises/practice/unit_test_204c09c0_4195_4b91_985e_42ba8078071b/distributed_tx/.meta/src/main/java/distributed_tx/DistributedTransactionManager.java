package distributed_tx;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.concurrent.atomic.AtomicInteger;

public class DistributedTransactionManager {
    private final long prepareTimeoutMillis;
    private final int maxRetries;
    private final ConcurrentMap<String, Transaction> transactions = new ConcurrentHashMap<>();
    private final ExecutorService executor = Executors.newCachedThreadPool();
    private final AtomicInteger txCounter = new AtomicInteger(0);

    private static class Transaction {
        private final List<Participant> participants = new ArrayList<>();
        private String status; // INIT, COMMITTED, ROLLED_BACK

        Transaction() {
            this.status = "INIT";
        }
    }

    public DistributedTransactionManager(long prepareTimeoutMillis, int maxRetries) {
        this.prepareTimeoutMillis = prepareTimeoutMillis;
        this.maxRetries = maxRetries;
    }

    public String beginTransaction() {
        String txId = "TX" + txCounter.incrementAndGet();
        Transaction tx = new Transaction();
        transactions.put(txId, tx);
        log("Transaction " + txId + " initiated.");
        return txId;
    }

    public void registerParticipant(String txId, Participant participant) {
        Transaction tx = transactions.get(txId);
        if (tx == null) {
            throw new IllegalArgumentException("Transaction not found: " + txId);
        }
        synchronized (tx) {
            tx.participants.add(participant);
        }
        log("Participant registered for transaction " + txId + ".");
    }

    public void executeTransaction(String txId) throws Exception {
        Transaction tx = transactions.get(txId);
        if (tx == null) {
            throw new IllegalArgumentException("Transaction not found: " + txId);
        }
        // Phase 1: Prepare Phase
        List<Participant> participants;
        synchronized (tx) {
            participants = new ArrayList<>(tx.participants);
        }
        CountDownLatch latch = new CountDownLatch(participants.size());
        List<Future<Boolean>> prepareFutures = new ArrayList<>();

        for (Participant participant : participants) {
            Callable<Boolean> task = () -> {
                try {
                    boolean result = participant.prepare();
                    log("Participant prepare returned: " + result);
                    return result;
                } catch (Exception e) {
                    log("Exception during prepare: " + e.getMessage());
                    return false;
                } finally {
                    latch.countDown();
                }
            };
            prepareFutures.add(executor.submit(task));
        }

        boolean prepareFailed = false;
        for (Future<Boolean> future : prepareFutures) {
            try {
                Boolean result = future.get(prepareTimeoutMillis, TimeUnit.MILLISECONDS);
                if (result == null || !result) {
                    prepareFailed = true;
                }
            } catch (TimeoutException te) {
                log("Prepare phase timeout: " + te.getMessage());
                prepareFailed = true;
            } catch (Exception ex) {
                log("Exception during prepare phase: " + ex.getMessage());
                prepareFailed = true;
            }
        }

        if (prepareFailed) {
            log("Prepare phase failed for transaction " + txId + ". Initiating rollback.");
            for (Participant participant : participants) {
                try {
                    participant.rollback();
                    log("Participant rolled back.");
                } catch (Exception e) {
                    log("Exception during rollback: " + e.getMessage());
                }
            }
            tx.status = "ROLLED_BACK";
        } else {
            // Phase 2: Commit Phase
            log("All participants prepared for transaction " + txId + ". Initiating commit.");
            boolean commitFailure = false;
            for (Participant participant : participants) {
                int attempt = 0;
                boolean committed = false;
                while (attempt < maxRetries && !committed) {
                    try {
                        participant.commit();
                        committed = true;
                        log("Participant committed.");
                    } catch (Exception e) {
                        attempt++;
                        log("Commit attempt " + attempt + " failed: " + e.getMessage());
                        if (attempt >= maxRetries) {
                            commitFailure = true;
                        }
                    }
                }
            }
            if (commitFailure) {
                log("Commit phase failed for transaction " + txId + ". Initiating rollback.");
                for (Participant participant : participants) {
                    try {
                        participant.rollback();
                        log("Participant rolled back after commit failure.");
                    } catch (Exception e) {
                        log("Exception during rollback after commit failure: " + e.getMessage());
                    }
                }
                tx.status = "ROLLED_BACK";
            } else {
                tx.status = "COMMITTED";
            }
        }
        log("Transaction " + txId + " completed with status: " + tx.status);
    }

    public String getTransactionStatus(String txId) {
        Transaction tx = transactions.get(txId);
        if (tx == null) {
            throw new IllegalArgumentException("Transaction not found: " + txId);
        }
        return tx.status;
    }

    private void log(String message) {
        System.out.println("[DTM] " + message);
    }
}