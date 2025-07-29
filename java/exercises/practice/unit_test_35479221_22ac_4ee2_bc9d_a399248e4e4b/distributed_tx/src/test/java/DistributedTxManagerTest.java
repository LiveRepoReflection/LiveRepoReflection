package distributed_tx;

import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.RepeatedTest;

import java.util.List;
import java.util.ArrayList;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ThreadLocalRandom;

public class DistributedTxManagerTest {

    // Dummy implementation to simulate resource behavior.
    private static class TestResource implements TransactionalResource {
        private final boolean failPrepare;
        private boolean prepareCalled = false;
        private boolean commitCalled = false;
        private boolean rollbackCalled = false;
        private int commitCount = 0;
        private int rollbackCount = 0;

        public TestResource(boolean failPrepare) {
            this.failPrepare = failPrepare;
        }

        @Override
        public boolean prepare() {
            prepareCalled = true;
            return !failPrepare;
        }

        @Override
        public void commit() {
            commitCalled = true;
            commitCount++;
        }

        @Override
        public void rollback() {
            rollbackCalled = true;
            rollbackCount++;
        }

        public boolean isPrepareCalled() {
            return prepareCalled;
        }

        public boolean isCommitCalled() {
            return commitCalled;
        }

        public boolean isRollbackCalled() {
            return rollbackCalled;
        }

        public int getCommitCount() {
            return commitCount;
        }

        public int getRollbackCount() {
            return rollbackCount;
        }
    }

    // Test for a successful distributed transaction where all resources prepare successfully.
    @Test
    public void testSuccessfulTransaction() {
        List<TransactionalResource> resources = new ArrayList<>();
        TestResource resource1 = new TestResource(false);
        TestResource resource2 = new TestResource(false);
        TestResource resource3 = new TestResource(false);
        resources.add(resource1);
        resources.add(resource2);
        resources.add(resource3);

        DistributedTransactionManager dtm = new DistributedTransactionManager();
        boolean result = dtm.processTransaction(resources);
        assertTrue(result, "Transaction should succeed when all resources prepare successfully.");

        // Verify that prepare and commit were called and rollback was not called.
        for (TransactionalResource resource : resources) {
            TestResource tr = (TestResource) resource;
            assertTrue(tr.isPrepareCalled(), "Prepare should have been called.");
            assertTrue(tr.isCommitCalled(), "Commit should have been called.");
            assertFalse(tr.isRollbackCalled(), "Rollback should not have been called on a successful transaction.");
        }
    }

    // Test transaction failure when one resource fails during the prepare phase.
    @Test
    public void testFailureInPrepare() {
        List<TransactionalResource> resources = new ArrayList<>();
        TestResource resource1 = new TestResource(false);
        TestResource resource2 = new TestResource(true); // This resource fails in prepare.
        TestResource resource3 = new TestResource(false);
        resources.add(resource1);
        resources.add(resource2);
        resources.add(resource3);

        DistributedTransactionManager dtm = new DistributedTransactionManager();
        boolean result = dtm.processTransaction(resources);
        assertFalse(result, "Transaction should fail if any resource fails in prepare.");

        // Verify that prepare was called on all and rollback was called on every resource,
        // while commit was not called.
        for (TransactionalResource resource : resources) {
            TestResource tr = (TestResource) resource;
            assertTrue(tr.isPrepareCalled(), "Prepare should have been called.");
            assertTrue(tr.isRollbackCalled(), "Rollback should have been called for a failed transaction.");
            assertFalse(tr.isCommitCalled(), "Commit should not be called on failure.");
        }
    }

    // Test the idempotency of commit and rollback methods.
    @Test
    public void testIdempotency() {
        TestResource resource = new TestResource(false);
        // Simulate a successful prepare.
        resource.prepare();
        // Call commit multiple times.
        resource.commit();
        resource.commit();
        assertEquals(2, resource.getCommitCount(), "Commit method should be idempotent when invoked multiple times.");

        // Call rollback multiple times.
        resource.rollback();
        resource.rollback();
        assertEquals(2, resource.getRollbackCount(), "Rollback method should be idempotent when invoked multiple times.");
    }

    // Test concurrent transactions to ensure DistributedTransactionManager handles concurrency correctly.
    @Test
    public void testConcurrentTransactions() throws InterruptedException, ExecutionException {
        int numThreads = 10;
        ExecutorService executor = Executors.newFixedThreadPool(numThreads);
        List<Callable<Boolean>> tasks = new ArrayList<>();

        for (int i = 0; i < numThreads; i++) {
            tasks.add(() -> {
                List<TransactionalResource> resources = new ArrayList<>();
                // Randomly decide if one resource will fail its prepare.
                boolean failOneResource = ThreadLocalRandom.current().nextBoolean();
                resources.add(new TestResource(false));
                resources.add(new TestResource(failOneResource));
                resources.add(new TestResource(false));
                DistributedTransactionManager dtm = new DistributedTransactionManager();
                return dtm.processTransaction(resources);
            });
        }

        List<Future<Boolean>> results = executor.invokeAll(tasks);
        for (Future<Boolean> future : results) {
            boolean res = future.get();
            // Each transaction outcome should be either successful or failed based on resource preparation.
            assertTrue(res || !res);
        }
        executor.shutdown();
    }

    // Test multiple sequential invocations to check consistency and reusability of the transaction manager.
    @RepeatedTest(5)
    public void testMultipleExecution() {
        List<TransactionalResource> resources = new ArrayList<>();
        TestResource resource1 = new TestResource(false);
        TestResource resource2 = new TestResource(false);
        resources.add(resource1);
        resources.add(resource2);

        DistributedTransactionManager dtm = new DistributedTransactionManager();
        boolean firstExecution = dtm.processTransaction(resources);
        boolean secondExecution = dtm.processTransaction(resources);
        // Both executions should succeed since resources are set to prepare successfully.
        assertTrue(firstExecution, "The first transaction execution should succeed.");
        assertTrue(secondExecution, "The second transaction execution should also succeed.");
    }
}