import java.util.*;
import java.util.concurrent.*;

public class Coordinator {
    private final long timeoutMs;
    private final List<BankServer> bankServers = new CopyOnWriteArrayList<>();
    private final ConcurrentMap<String, TransactionStatus> transactionStatusMap = new ConcurrentHashMap<>();

    public Coordinator(long timeoutMs) {
        this.timeoutMs = timeoutMs;
    }

    public void registerBankServers(List<BankServer> servers) {
        bankServers.clear();
        bankServers.addAll(servers);
    }

    public TransactionStatus getTransactionStatus(String transactionId) {
        return transactionStatusMap.get(transactionId);
    }

    public boolean executeTransaction(Transaction tx) {
        transactionStatusMap.put(tx.getId(), TransactionStatus.PENDING);
        ExecutorService executor = Executors.newFixedThreadPool(bankServers.size());
        List<Future<Boolean>> futures = new ArrayList<>();

        // Phase 1: Prepare phase - send prepare request concurrently.
        for (BankServer bank : bankServers) {
            List<Operation> ops = tx.getOperations(bank);
            Callable<Boolean> task = () -> bank.prepare(tx.getId(), ops);
            futures.add(executor.submit(task));
        }

        boolean allPrepared = true;
        for (Future<Boolean> future : futures) {
            try {
                boolean prepared = future.get(timeoutMs, TimeUnit.MILLISECONDS);
                if (!prepared) {
                    allPrepared = false;
                    break;
                }
            } catch (Exception e) {
                allPrepared = false;
                break;
            }
        }

        // Phase 2: Commit if all prepared; otherwise rollback.
        if (allPrepared) {
            for (BankServer bank : bankServers) {
                bank.commit(tx.getId());
            }
            transactionStatusMap.put(tx.getId(), TransactionStatus.COMMITTED);
            executor.shutdown();
            return true;
        } else {
            for (BankServer bank : bankServers) {
                bank.rollback(tx.getId());
            }
            transactionStatusMap.put(tx.getId(), TransactionStatus.ROLLEDBACK);
            executor.shutdown();
            return false;
        }
    }

    public void persistState() {
        // In an actual implementation, the state would be persisted to a durable store.
        // For simulation purposes, this is a no-op.
    }

    public static Coordinator recover(long timeoutMs) {
        // In an actual implementation, state would be reloaded from persistent storage.
        return new Coordinator(timeoutMs);
    }
}