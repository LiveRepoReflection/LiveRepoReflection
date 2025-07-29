import java.util.*;
import java.util.concurrent.*;

public class TransactionCoordinator {

    private static final long TIMEOUT_MS = 2000;
    private static final ExecutorService executor = Executors.newCachedThreadPool();

    // Map of transaction id to list of enlisted bank services.
    private final ConcurrentMap<String, List<BankService>> transactionMap = new ConcurrentHashMap<>();

    public String beginTransaction() {
        String transactionId = UUID.randomUUID().toString();
        transactionMap.put(transactionId, Collections.synchronizedList(new ArrayList<>()));
        System.out.println("Transaction begun: " + transactionId);
        return transactionId;
    }

    public void enlistBankService(String transactionId, BankService bankService) {
        List<BankService> services = transactionMap.get(transactionId);
        if (services == null) {
            throw new IllegalArgumentException("Transaction not found: " + transactionId);
        }
        services.add(bankService);
        System.out.println("BankService enlisted for transaction: " + transactionId);
    }

    public void transfer(String transactionId, BankService fromBankService, String fromAccountId,
                         BankService toBankService, String toAccountId, double amount) {
        List<BankService> services = transactionMap.get(transactionId);
        if (services == null || services.isEmpty()) {
            throw new IllegalArgumentException("No bank services enlisted for transaction: " + transactionId);
        }

        System.out.println("Starting transfer for transaction: " + transactionId + ", amount: " + amount);

        // Phase 1: Prepare phase executed concurrently.
        List<Callable<Boolean>> tasks = new ArrayList<>();
        for (BankService service : services) {
            tasks.add(() -> {
                boolean result = service.prepare(transactionId);
                System.out.println("Prepare on service " + service + " returned: " + result + " for txn: " + transactionId);
                return result;
            });
        }

        boolean allPrepared = true;
        List<Future<Boolean>> futures = new ArrayList<>();
        for (Callable<Boolean> task : tasks) {
            futures.add(executor.submit(task));
        }
        for (Future<Boolean> future : futures) {
            try {
                boolean result = future.get(TIMEOUT_MS, TimeUnit.MILLISECONDS);
                if (!result) {
                    allPrepared = false;
                }
            } catch (TimeoutException e) {
                System.out.println("Timeout during prepare phase for txn: " + transactionId);
                allPrepared = false;
                future.cancel(true);
            } catch (Exception e) {
                System.out.println("Exception during prepare phase for txn: " + transactionId + " error: " + e.getMessage());
                allPrepared = false;
            }
        }

        // Phase 2: Commit or Rollback based on prepare phase results.
        if (allPrepared) {
            System.out.println("All services prepared successfully for txn: " + transactionId + ". Committing transaction.");
            for (BankService service : services) {
                try {
                    service.commit(transactionId);
                    System.out.println("Committed on service: " + service + " for txn: " + transactionId);
                } catch (Exception e) {
                    System.out.println("Exception during commit on service: " + service + " for txn: " + transactionId + " error: " + e.getMessage());
                }
            }
        } else {
            System.out.println("Preparation failed for one or more services for txn: " + transactionId + ". Rolling back transaction.");
            for (BankService service : services) {
                try {
                    service.rollback(transactionId);
                    System.out.println("Rolled back on service: " + service + " for txn: " + transactionId);
                } catch (Exception e) {
                    System.out.println("Exception during rollback on service: " + service + " for txn: " + transactionId + " error: " + e.getMessage());
                }
            }
        }
        endTransaction(transactionId);
    }

    public void endTransaction(String transactionId) {
        transactionMap.remove(transactionId);
        System.out.println("Ended transaction: " + transactionId);
    }
}