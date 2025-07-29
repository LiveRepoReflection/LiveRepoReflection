import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;

import java.util.*;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

public class TransactionSagaTest {

    interface Operation {
        boolean execute();
        boolean compensate();
        String getName();
    }

    class DummyOperation implements Operation {
        private String name;
        private boolean shouldFail;
        public int executeCount = 0;
        public int compensateCount = 0;

        public DummyOperation(String name, boolean shouldFail) {
            this.name = name;
            this.shouldFail = shouldFail;
        }

        @Override
        public boolean execute() {
            executeCount++;
            // Default behavior: if shouldFail and not overridden, always fail.
            if (shouldFail) {
                return false;
            }
            return true;
        }

        @Override
        public boolean compensate() {
            compensateCount++;
            return true;
        }

        @Override
        public String getName() {
            return name;
        }
    }

    class TransactionSaga {
        private List<Operation> operations;
        private int maxRetries;

        public TransactionSaga(List<Operation> operations, int maxRetries) {
            this.operations = operations;
            this.maxRetries = maxRetries;
        }

        /**
         * Executes the transaction by processing each operation in order.
         * If any operation fails after the allowed number of retries, all previously
         * executed operations are compensated in reverse order.
         *
         * @return true if the transaction completed successfully; false if it was rolled back.
         */
        public boolean execute() {
            List<Operation> executed = new ArrayList<>();
            for (Operation op : operations) {
                boolean success = false;
                int retries = 0;
                while (retries <= maxRetries) {
                    if (op.execute()) {
                        success = true;
                        break;
                    }
                    retries++;
                    // Exponential backoff simulation (can be enhanced with Thread.sleep in a real system)
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

    @BeforeEach
    public void setup() {
        // Setup for tests if needed
    }

    @Test
    public void testSuccessfulTransaction() {
        DummyOperation op1 = new DummyOperation("Inventory", false);
        DummyOperation op2 = new DummyOperation("Payment", false);
        DummyOperation op3 = new DummyOperation("Order", false);
        DummyOperation op4 = new DummyOperation("Shipping", false);

        List<Operation> ops = Arrays.asList(op1, op2, op3, op4);
        TransactionSaga saga = new TransactionSaga(ops, 3);

        boolean result = saga.execute();
        assertTrue(result, "Transaction should succeed when all operations are successful");

        assertEquals(1, op1.executeCount, "Inventory should execute once");
        assertEquals(1, op2.executeCount, "Payment should execute once");
        assertEquals(1, op3.executeCount, "Order should execute once");
        assertEquals(1, op4.executeCount, "Shipping should execute once");

        // No compensation should have been triggered.
        assertEquals(0, op1.compensateCount, "No compensation for Inventory");
        assertEquals(0, op2.compensateCount, "No compensation for Payment");
        assertEquals(0, op3.compensateCount, "No compensation for Order");
        assertEquals(0, op4.compensateCount, "No compensation for Shipping");
    }

    @Test
    public void testFailedTransactionWithRollback() {
        DummyOperation op1 = new DummyOperation("Inventory", false);
        // Payment operation that always fails.
        DummyOperation op2 = new DummyOperation("Payment", true) {
            @Override
            public boolean execute() {
                executeCount++;
                return false;
            }
        };
        DummyOperation op3 = new DummyOperation("Order", false);
        DummyOperation op4 = new DummyOperation("Shipping", false);

        List<Operation> ops = Arrays.asList(op1, op2, op3, op4);
        TransactionSaga saga = new TransactionSaga(ops, 2);

        boolean result = saga.execute();
        assertFalse(result, "Transaction should fail and trigger rollback when an operation fails");

        // op1 should have executed once.
        assertEquals(1, op1.executeCount, "Inventory should execute once");
        // op2 should be retried maxRetries+1 times (i.e., 3 times total).
        assertEquals(3, op2.executeCount, "Payment should execute three times due to retries");

        // Compensation should be called for op1 because it succeeded before failure.
        assertEquals(1, op1.compensateCount, "Inventory should be compensated once after failure");
        // No compensation for op2 because it did not complete successfully.
        assertEquals(0, op2.compensateCount, "Payment should not be compensated as it never succeeded");
    }

    @Test
    public void testPartialRetrySuccess() {
        DummyOperation op1 = new DummyOperation("Inventory", false);
        // Payment operation fails on first attempt but succeeds on retry.
        DummyOperation op2 = new DummyOperation("Payment", true) {
            @Override
            public boolean execute() {
                executeCount++;
                if (executeCount == 1) {
                    return false;
                }
                return true;
            }
        };
        DummyOperation op3 = new DummyOperation("Order", false);
        DummyOperation op4 = new DummyOperation("Shipping", false);

        List<Operation> ops = Arrays.asList(op1, op2, op3, op4);
        TransactionSaga saga = new TransactionSaga(ops, 2);

        boolean result = saga.execute();
        assertTrue(result, "Transaction should eventually succeed after Payment retries");

        assertEquals(1, op1.executeCount, "Inventory should execute once");
        assertEquals(2, op2.executeCount, "Payment should execute twice due to one retry");
        assertEquals(1, op3.executeCount, "Order should execute once");
        assertEquals(1, op4.executeCount, "Shipping should execute once");

        // Since the transaction succeeded, no compensations should occur.
        assertEquals(0, op1.compensateCount, "No compensation for Inventory");
        assertEquals(0, op2.compensateCount, "No compensation for Payment");
    }

    @Test
    public void testConcurrentTransactions() throws InterruptedException, ExecutionException {
        Callable<Boolean> transactionTask = () -> {
            DummyOperation op1 = new DummyOperation("Inventory", false);
            DummyOperation op2 = new DummyOperation("Payment", false);
            DummyOperation op3 = new DummyOperation("Order", false);
            DummyOperation op4 = new DummyOperation("Shipping", false);
            List<Operation> ops = Arrays.asList(op1, op2, op3, op4);
            TransactionSaga saga = new TransactionSaga(ops, 2);
            return saga.execute();
        };

        ExecutorService executor = Executors.newFixedThreadPool(10);
        List<Future<Boolean>> futures = new ArrayList<>();
        for (int i = 0; i < 20; i++) {
            futures.add(executor.submit(transactionTask));
        }

        for (Future<Boolean> future : futures) {
            assertTrue(future.get(), "Each concurrent transaction should succeed");
        }
        executor.shutdown();
    }

    @Test
    public void testNoOperationTransaction() {
        // Testing a transaction with no operations should succeed trivially.
        List<Operation> ops = new ArrayList<>();
        TransactionSaga saga = new TransactionSaga(ops, 2);
        boolean result = saga.execute();
        assertTrue(result, "An empty transaction should succeed");
    }
}