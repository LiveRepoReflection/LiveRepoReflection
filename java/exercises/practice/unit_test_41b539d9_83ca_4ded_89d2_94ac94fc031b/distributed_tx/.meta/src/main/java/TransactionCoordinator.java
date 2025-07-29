import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;

public class TransactionCoordinator {
    private final int PREPARE_TIMEOUT_SEC = 5;
    private final int COMMIT_RETRIES = 3;
    private final long INITIAL_BACKOFF_MS = 100;

    public boolean transfer(String fromAccountId, String toAccountId, double amount, List<BankService> bankServices) {
        if (bankServices == null || bankServices.size() != 2) {
            System.out.println("Exactly two bank services required: one for debit and one for credit.");
            return false;
        }
        BankService debitService = bankServices.get(0);
        BankService creditService = bankServices.get(1);

        ExecutorService executor = Executors.newFixedThreadPool(2);
        try {
            Callable<Boolean> debitPrepareTask = () -> debitService.prepareDebit(fromAccountId, amount);
            Callable<Boolean> creditPrepareTask = () -> creditService.prepareCredit(toAccountId, amount);
            Future<Boolean> debitFuture = executor.submit(debitPrepareTask);
            Future<Boolean> creditFuture = executor.submit(creditPrepareTask);
            boolean debitPrepared = false;
            boolean creditPrepared = false;
            try {
                debitPrepared = debitFuture.get(PREPARE_TIMEOUT_SEC, TimeUnit.SECONDS);
            } catch (Exception e) {
                System.out.println("Timeout or exception during debit prepare: " + e.getMessage());
                debitPrepared = false;
            }
            try {
                creditPrepared = creditFuture.get(PREPARE_TIMEOUT_SEC, TimeUnit.SECONDS);
            } catch (Exception e) {
                System.out.println("Timeout or exception during credit prepare: " + e.getMessage());
                creditPrepared = false;
            }
            if (!debitPrepared || !creditPrepared) {
                System.out.println("Prepare phase failed. Initiating rollback.");
                if (debitPrepared) {
                    debitService.rollbackDebit(fromAccountId, amount);
                    System.out.println("Rolled back debit service.");
                }
                if (creditPrepared) {
                    creditService.rollbackCredit(toAccountId, amount);
                    System.out.println("Rolled back credit service.");
                }
                return false;
            }
            // Both services successfully prepared.
            boolean debitCommitted = commitWithRetry(() -> debitService.commitDebit(fromAccountId, amount));
            boolean creditCommitted = commitWithRetry(() -> creditService.commitCredit(toAccountId, amount));
            if (!debitCommitted || !creditCommitted) {
                System.out.println("Commit phase failed. Initiating rollback.");
                debitService.rollbackDebit(fromAccountId, amount);
                creditService.rollbackCredit(toAccountId, amount);
                return false;
            }
            System.out.println("Transaction committed successfully.");
            return true;
        } finally {
            executor.shutdownNow();
        }
    }

    private boolean commitWithRetry(Callable<Boolean> commitOperation) {
        long backoff = INITIAL_BACKOFF_MS;
        for (int attempt = 1; attempt <= COMMIT_RETRIES; attempt++) {
            try {
                if (commitOperation.call()) {
                    return true;
                } else {
                    System.out.println("Commit attempt " + attempt + " failed. Retrying in " + backoff + "ms.");
                    Thread.sleep(backoff);
                    backoff *= 2;
                }
            } catch (Exception e) {
                System.out.println("Exception during commit attempt " + attempt + ": " + e.getMessage());
                try {
                    Thread.sleep(backoff);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    return false;
                }
                backoff *= 2;
            }
        }
        return false;
    }
}