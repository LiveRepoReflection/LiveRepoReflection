import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class TransactionOrchestrator {
    public TransactionResult execute(List<Transaction> transactions) {
        if (transactions == null) {
            throw new IllegalArgumentException("Transaction list cannot be null");
        }

        if (transactions.isEmpty()) {
            return new TransactionResult(true, Collections.emptyList());
        }

        List<TransactionStatus> statuses = new ArrayList<>();
        List<Transaction> committedTransactions = new ArrayList<>();
        boolean overallSuccess = true;

        try {
            // Commit phase
            for (Transaction tx : transactions) {
                try {
                    boolean commitSuccess = tx.commit();
                    if (commitSuccess) {
                        statuses.add(new TransactionStatus(TransactionStatus.Status.COMMITTED, null));
                        committedTransactions.add(tx);
                    } else {
                        statuses.add(new TransactionStatus(TransactionStatus.Status.COMMIT_FAILED, "Commit failed"));
                        overallSuccess = false;
                        break;
                    }
                } catch (Exception e) {
                    statuses.add(new TransactionStatus(TransactionStatus.Status.COMMIT_FAILED, e.getMessage()));
                    overallSuccess = false;
                    break;
                }
            }

            // If commit phase failed, rollback
            if (!overallSuccess) {
                Collections.reverse(committedTransactions);
                for (Transaction tx : committedTransactions) {
                    try {
                        boolean rollbackSuccess = tx.rollback();
                        if (rollbackSuccess) {
                            statuses.add(new TransactionStatus(TransactionStatus.Status.ROLLED_BACK, null));
                        } else {
                            statuses.add(new TransactionStatus(TransactionStatus.Status.ROLLBACK_FAILED, "Rollback failed"));
                        }
                    } catch (Exception e) {
                        statuses.add(new TransactionStatus(TransactionStatus.Status.ROLLBACK_FAILED, e.getMessage()));
                    }
                }
            }

            return new TransactionResult(overallSuccess, statuses);
        } catch (Exception e) {
            return new TransactionResult(false, statuses);
        }
    }
}