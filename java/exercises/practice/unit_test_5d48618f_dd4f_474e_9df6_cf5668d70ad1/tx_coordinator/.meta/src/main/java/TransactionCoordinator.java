import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

public class TransactionCoordinator {

    private static final ExecutorService executor = Executors.newCachedThreadPool();

    private enum Status {
        PENDING,
        COMMITTED,
        ROLLED_BACK
    }

    private static class TransactionContext {
        List<Service> services;
        Status status;

        TransactionContext() {
            services = new ArrayList<>();
            status = Status.PENDING;
        }
    }

    private final Map<String, TransactionContext> transactions = new ConcurrentHashMap<>();

    public String begin() {
        String transactionId = UUID.randomUUID().toString();
        TransactionContext context = new TransactionContext();
        transactions.put(transactionId, context);
        return transactionId;
    }

    public void enlistService(String transactionId, Service service) {
        TransactionContext context = transactions.get(transactionId);
        if (context == null) {
            throw new IllegalArgumentException("Transaction not found: " + transactionId);
        }
        synchronized (context) {
            if (context.status != Status.PENDING) {
                throw new IllegalStateException("Cannot enlist service to a transaction that is not pending.");
            }
            context.services.add(service);
        }
    }

    public boolean commit(String transactionId) {
        TransactionContext context = transactions.get(transactionId);
        if (context == null) {
            throw new IllegalArgumentException("Transaction not found: " + transactionId);
        }
        synchronized (context) {
            if (context.status == Status.COMMITTED) {
                return true;
            }
            if (context.status == Status.ROLLED_BACK) {
                return false;
            }
        }

        // Phase 1: Prepare phase - run concurrently.
        List<Callable<Boolean>> prepareTasks = new ArrayList<>();
        for (Service service : context.services) {
            prepareTasks.add(() -> {
                try {
                    return service.prepare(transactionId);
                } catch (Exception e) {
                    System.out.println("Error during prepare: " + e.getMessage());
                    return false;
                }
            });
        }
        try {
            List<Future<Boolean>> prepareResults = executor.invokeAll(prepareTasks);
            for (Future<Boolean> future : prepareResults) {
                if (!future.get()) {
                    rollback(transactionId);
                    synchronized (context) {
                        context.status = Status.ROLLED_BACK;
                    }
                    return false;
                }
            }
        } catch (Exception e) {
            System.out.println("Exception during prepare phase: " + e.getMessage());
            rollback(transactionId);
            synchronized (context) {
                context.status = Status.ROLLED_BACK;
            }
            return false;
        }

        // Phase 2: Commit phase - run concurrently.
        List<Callable<Boolean>> commitTasks = new ArrayList<>();
        for (Service service : context.services) {
            commitTasks.add(() -> {
                try {
                    return service.commit(transactionId);
                } catch (Exception e) {
                    System.out.println("Error during commit: " + e.getMessage());
                    return false;
                }
            });
        }
        boolean commitSuccess = true;
        try {
            List<Future<Boolean>> commitResults = executor.invokeAll(commitTasks);
            for (Future<Boolean> future : commitResults) {
                if (!future.get()) {
                    commitSuccess = false;
                    break;
                }
            }
        } catch (Exception e) {
            System.out.println("Exception during commit phase: " + e.getMessage());
            commitSuccess = false;
        }

        if (!commitSuccess) {
            rollback(transactionId);
            synchronized (context) {
                context.status = Status.ROLLED_BACK;
            }
            return false;
        }

        synchronized (context) {
            context.status = Status.COMMITTED;
        }
        return true;
    }

    public boolean rollback(String transactionId) {
        TransactionContext context = transactions.get(transactionId);
        if (context == null) {
            throw new IllegalArgumentException("Transaction not found: " + transactionId);
        }
        synchronized (context) {
            if (context.status == Status.ROLLED_BACK) {
                return false;
            }
            context.status = Status.ROLLED_BACK;
        }
        List<Callable<Boolean>> rollbackTasks = new ArrayList<>();
        for (Service service : context.services) {
            rollbackTasks.add(() -> {
                try {
                    return service.rollback(transactionId);
                } catch (Exception e) {
                    System.out.println("Error during rollback: " + e.getMessage());
                    return false;
                }
            });
        }
        try {
            List<Future<Boolean>> rollbackResults = executor.invokeAll(rollbackTasks);
            for (Future<Boolean> future : rollbackResults) {
                future.get();
            }
        } catch (Exception e) {
            System.out.println("Exception during rollback phase: " + e.getMessage());
        }
        return false;
    }
}