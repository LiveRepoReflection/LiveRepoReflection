package transaction_saga;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class TransactionSaga {
    private final List<Operation> operations;
    private final int maxRetries;

    /**
     * Constructs a TransactionSaga with a list of operations and maximum retry count.
     *
     * @param operations the list of operations to execute in the transaction.
     * @param maxRetries maximum number of retries for each operation before invoking compensation.
     */
    public TransactionSaga(List<Operation> operations, int maxRetries) {
        if (operations == null) {
            this.operations = new ArrayList<>();
        } else {
            this.operations = operations;
        }
        this.maxRetries = maxRetries;
    }

    /**
     * Executes all operations in the defined order. For each operation, if execution fails after
     * the allowed number of retries, previously successful operations are compensated (rolled back)
     * in reverse order.
     *
     * @return true if the entire transaction succeeds; false if rollback is performed due to failure.
     */
    public boolean execute() {
        List<Operation> executed = new ArrayList<>();
        for (Operation op : operations) {
            boolean success = false;
            int retries = 0;
            // Retry until maxRetries reached.
            while (retries <= maxRetries) {
                if (op.execute()) {
                    success = true;
                    break;
                }
                retries++;
            }
            if (!success) {
                // Rollback previously executed operations in reverse order.
                Collections.reverse(executed);
                for (Operation executedOp : executed) {
                    executedOp.compensate();
                }
                return false;
            }
            executed.add(op);
        }
        return true;
    }
}