package distributed_tx;

import java.util.*;
import java.util.concurrent.*;
import java.util.stream.Collectors;

public class TransactionCoordinator {
    private final List<Bank> banks;
    private final long timeoutMillis;
    private Bank leader;
    private final ExecutorService executor;

    public TransactionCoordinator(List<Bank> banks) {
        this(banks, 5000);
    }

    public TransactionCoordinator(List<Bank> banks, long timeoutMillis) {
        this.banks = Collections.synchronizedList(new ArrayList<>(banks));
        this.timeoutMillis = timeoutMillis;
        this.executor = Executors.newCachedThreadPool();
        electLeader();
    }

    private synchronized void electLeader() {
        if (!banks.isEmpty()) {
            leader = banks.get(0);
        } else {
            leader = null;
        }
    }

    public synchronized Bank getLeader() {
        return leader;
    }

    public synchronized void simulateLeaderFailure(Bank failedLeader) {
        if (leader != null && leader.getName().equals(failedLeader.getName())) {
            banks.removeIf(bank -> bank.getName().equals(failedLeader.getName()));
            electLeader();
        }
    }

    public TransactionResult executeTransaction(String transactionId, Map<String, TransactionOperation> operations) {
        List<Bank> participants = banks.stream()
                .filter(bank -> operations.containsKey(bank.getName()))
                .collect(Collectors.toList());

        List<Future<Boolean>> prepareFutures = new ArrayList<>();
        for (Bank bank : participants) {
            TransactionOperation op = operations.get(bank.getName());
            Callable<Boolean> task = () -> bank.prepare(transactionId, op.getAccountId(), op.getAmount());
            Future<Boolean> future = executor.submit(task);
            prepareFutures.add(future);
        }

        boolean allPrepared = true;
        for (Future<Boolean> future : prepareFutures) {
            try {
                boolean result = future.get(timeoutMillis, TimeUnit.MILLISECONDS);
                if (!result) {
                    allPrepared = false;
                }
            } catch (TimeoutException | InterruptedException | ExecutionException e) {
                allPrepared = false;
            }
        }

        List<Callable<Boolean>> phaseTwoTasks = new ArrayList<>();
        if (allPrepared) {
            int yesCount = 0;
            for (Future<Boolean> future : prepareFutures) {
                try {
                    if (future.get()) {
                        yesCount++;
                    }
                } catch (Exception e) {
                    // Already handled in prepare phase logic.
                }
            }
            int majority = (participants.size() / 2) + 1;
            if (yesCount < majority) {
                allPrepared = false;
            }
        }

        if (allPrepared) {
            for (Bank bank : participants) {
                TransactionOperation op = operations.get(bank.getName());
                Callable<Boolean> commitTask = () -> bank.commit(transactionId, op.getAccountId(), op.getAmount());
                phaseTwoTasks.add(commitTask);
            }
            try {
                List<Future<Boolean>> commitFutures = executor.invokeAll(phaseTwoTasks, timeoutMillis, TimeUnit.MILLISECONDS);
                for (Future<Boolean> future : commitFutures) {
                    boolean commitResult = future.get();
                    if (!commitResult) {
                        return new TransactionResult(false);
                    }
                }
            } catch (InterruptedException | ExecutionException e) {
                return new TransactionResult(false);
            }
            return new TransactionResult(true);
        } else {
            for (Bank bank : participants) {
                TransactionOperation op = operations.get(bank.getName());
                Callable<Boolean> rollbackTask = () -> bank.rollback(transactionId, op.getAccountId(), op.getAmount());
                phaseTwoTasks.add(rollbackTask);
            }
            try {
                List<Future<Boolean>> rollbackFutures = executor.invokeAll(phaseTwoTasks, timeoutMillis, TimeUnit.MILLISECONDS);
                for (Future<Boolean> future : rollbackFutures) {
                    boolean rollbackResult = future.get();
                    if (!rollbackResult) {
                        // In a full implementation, rollback failures would be handled.
                    }
                }
            } catch (InterruptedException | ExecutionException e) {
                // Suppress rollback exceptions.
            }
            return new TransactionResult(false);
        }
    }
}