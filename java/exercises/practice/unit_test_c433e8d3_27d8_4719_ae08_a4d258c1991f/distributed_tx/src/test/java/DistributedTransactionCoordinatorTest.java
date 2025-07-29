import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.AfterEach;
import static org.junit.jupiter.api.Assertions.*;

import java.util.Map;
import java.util.HashMap;
import java.util.UUID;
import java.util.List;
import java.util.ArrayList;
import java.util.concurrent.Callable;
import java.util.concurrent.Future;
import java.util.concurrent.Executors;
import java.util.concurrent.ExecutorService;

public class DistributedTransactionCoordinatorTest {

    // Dummy Branch interface as defined in the problem
    interface Branch {
        boolean prepare(UUID transactionId, String operationDetails);
        void commit(UUID transactionId);
        void rollback(UUID transactionId);
    }

    // Dummy implementation of a TransactionCoordinator for testing purposes.
    // It is assumed that the actual implementation exists in the main project.
    // For unit testing, we will assume that the coordinator exposes a method:
    // boolean processTransaction(UUID transactionId, Map<Branch, String> operations)
    // and an optional constructor that accepts a timeout value in milliseconds.
    // The method returns true if the transaction commits,
    // and false if the transaction rolls back.
    static class TransactionCoordinator {
        private long timeoutMillis;

        public TransactionCoordinator() {
            // Default timeout is 500ms
            this.timeoutMillis = 500;
        }

        public TransactionCoordinator(long timeoutMillis) {
            this.timeoutMillis = timeoutMillis;
        }

        public boolean processTransaction(UUID transactionId, Map<Branch, String> operations) {
            // Phase 1: Prepare
            Map<Branch, Boolean> preparedResponses = new HashMap<>();
            long startTime = System.currentTimeMillis();
            for (Map.Entry<Branch, String> entry : operations.entrySet()) {
                Branch branch = entry.getKey();
                boolean prepared = false;
                try {
                    // Simulate potential delay in branch response
                    prepared = branch.prepare(transactionId, entry.getValue());
                    // Check for timeout within the loop
                    if (System.currentTimeMillis() - startTime > timeoutMillis) {
                        prepared = false;
                    }
                } catch (Exception e) {
                    prepared = false;
                }
                preparedResponses.put(branch, prepared);
                if (!prepared) {
                    // Abort immediately if one branch fails
                    rollbackAll(transactionId, operations.keySet());
                    return false;
                }
            }
            // Phase 2: Commit since all branches prepared successfully
            for (Branch branch : operations.keySet()) {
                branch.commit(transactionId);
            }
            return true;
        }

        private void rollbackAll(UUID transactionId, Iterable<Branch> branches) {
            for (Branch branch : branches) {
                try {
                    branch.rollback(transactionId);
                } catch (Exception e) {
                    // Ignore exceptions during rollback
                }
            }
        }
    }

    // Dummy branches for unit tests:

    // Always returns success on prepare.
    static class AlwaysSuccessBranch implements Branch {
        @Override
        public boolean prepare(UUID transactionId, String operationDetails) {
            return true;
        }
        @Override
        public void commit(UUID transactionId) { }
        @Override
        public void rollback(UUID transactionId) { }
    }

    // Always returns failure on prepare.
    static class AlwaysFailBranch implements Branch {
        @Override
        public boolean prepare(UUID transactionId, String operationDetails) {
            return false;
        }
        @Override
        public void commit(UUID transactionId) { }
        @Override
        public void rollback(UUID transactionId) { }
    }

    // Simulates a branch with a delay in response.
    static class DelayedBranch implements Branch {
        private long delayMillis;
        public DelayedBranch(long delayMillis) {
            this.delayMillis = delayMillis;
        }
        @Override
        public boolean prepare(UUID transactionId, String operationDetails) {
            try {
                Thread.sleep(delayMillis);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return false;
            }
            return true;
        }
        @Override
        public void commit(UUID transactionId) { }
        @Override
        public void rollback(UUID transactionId) { }
    }

    private ExecutorService executor;

    @BeforeEach
    public void setUp() {
        executor = Executors.newFixedThreadPool(5);
    }

    @AfterEach
    public void tearDown() {
        if (executor != null) {
            executor.shutdownNow();
        }
    }

    @Test
    public void testSuccessfulTransaction() {
        TransactionCoordinator coordinator = new TransactionCoordinator();
        Map<Branch, String> operations = new HashMap<>();
        AlwaysSuccessBranch branch1 = new AlwaysSuccessBranch();
        AlwaysSuccessBranch branch2 = new AlwaysSuccessBranch();
        operations.put(branch1, "Debit Account A by $100");
        operations.put(branch2, "Credit Account B by $100");

        boolean result = coordinator.processTransaction(UUID.randomUUID(), operations);
        assertTrue(result, "Transaction should commit successfully when all branches prepare successfully");
    }

    @Test
    public void testPrepareFailure() {
        TransactionCoordinator coordinator = new TransactionCoordinator();
        Map<Branch, String> operations = new HashMap<>();
        AlwaysSuccessBranch branch1 = new AlwaysSuccessBranch();
        AlwaysFailBranch branch2 = new AlwaysFailBranch();
        operations.put(branch1, "Debit Account X by $50");
        operations.put(branch2, "Credit Account Y by $50");

        boolean result = coordinator.processTransaction(UUID.randomUUID(), operations);
        assertFalse(result, "Transaction should roll back when at least one branch fails to prepare");
    }

    @Test
    public void testTimeoutTransaction() {
        // Set a shorter timeout of 100ms for testing timeout behavior.
        TransactionCoordinator coordinator = new TransactionCoordinator(100);
        Map<Branch, String> operations = new HashMap<>();
        // Create a delayed branch that will exceed the timeout.
        DelayedBranch delayedBranch = new DelayedBranch(200);
        AlwaysSuccessBranch branch2 = new AlwaysSuccessBranch();
        operations.put(delayedBranch, "Debit Account M by $75");
        operations.put(branch2, "Credit Account N by $75");

        boolean result = coordinator.processTransaction(UUID.randomUUID(), operations);
        assertFalse(result, "Transaction should roll back if a branch does not respond within the timeout period");
    }

    @Test
    public void testConcurrentTransactions() throws Exception {
        TransactionCoordinator coordinator = new TransactionCoordinator();
        int numTransactions = 5;
        List<Callable<Boolean>> tasks = new ArrayList<>();
        for (int i = 0; i < numTransactions; i++) {
            tasks.add(new Callable<Boolean>() {
                @Override
                public Boolean call() {
                    Map<Branch, String> ops = new HashMap<>();
                    ops.put(new AlwaysSuccessBranch(), "Debit Operation");
                    ops.put(new AlwaysSuccessBranch(), "Credit Operation");
                    return coordinator.processTransaction(UUID.randomUUID(), ops);
                }
            });
        }
        List<Future<Boolean>> futures = executor.invokeAll(tasks);
        for (Future<Boolean> future : futures) {
            assertTrue(future.get(), "Each concurrent transaction should commit successfully");
        }
    }
}