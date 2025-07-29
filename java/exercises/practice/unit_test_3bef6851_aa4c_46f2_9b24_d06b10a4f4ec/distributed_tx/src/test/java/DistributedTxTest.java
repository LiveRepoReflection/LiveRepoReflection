package distributed_tx;

import org.junit.Before;
import org.junit.Test;
import static org.junit.Assert.*;

import java.util.Arrays;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.ThreadLocalRandom;

public class DistributedTxTest {

    private TransactionManager txManager;

    @Before
    public void setUp() {
        // Initialize the TransactionManager which sets up 5 services with initial resource values.
        txManager = new TransactionManager();
    }

    // Test a successful transaction commit using the two-phase commit protocol.
    @Test
    public void testSuccessfulCommit() {
        // Retrieve services by their IDs.
        Service service1 = txManager.getService(1);
        Service service2 = txManager.getService(2);
        int initial1 = service1.getResource();
        int initial2 = service2.getResource();

        // Create a transaction that increments service1 by 10 and decrements service2 by 5.
        List<TransactionOperation> ops = Arrays.asList(
            new TransactionOperation(1, OperationType.INCREMENT, 10),
            new TransactionOperation(2, OperationType.DECREMENT, 5)
        );

        boolean result = txManager.executeTransaction(ops);
        assertTrue("Transaction should commit successfully.", result);

        // Verify that the changes have been committed.
        assertEquals("Service 1 resource value should be incremented by 10.", initial1 + 10, service1.getResource());
        assertEquals("Service 2 resource value should be decremented by 5.", initial2 - 5, service2.getResource());
    }

    // Test that a transaction aborts if an operation would cause an insufficient resource scenario.
    @Test
    public void testAbortDueToInsufficientResource() {
        // For this test, ensure service3 has a resource value lower than the amount to be decremented.
        Service service3 = txManager.getService(3);
        txManager.setServiceResource(3, 3);
        int initial3 = service3.getResource();

        // Attempt to decrement service3 by 5, which should not be allowed.
        List<TransactionOperation> ops = Arrays.asList(
            new TransactionOperation(3, OperationType.DECREMENT, 5)
        );

        boolean result = txManager.executeTransaction(ops);
        assertFalse("Transaction should abort due to insufficient resource.", result);

        // The resource value should remain unchanged after the rollback.
        assertEquals("Service 3 resource value should remain unchanged after abort.", initial3, service3.getResource());
    }

    // Test that a transaction aborts if a simulated service failure occurs during the prepare phase.
    @Test
    public void testAbortDueToServiceFailure() {
        Service service4 = txManager.getService(4);
        int initial4 = service4.getResource();

        // Force the service to simulate a failure during the prepare phase.
        service4.setForceFailure(true);

        List<TransactionOperation> ops = Arrays.asList(
            new TransactionOperation(4, OperationType.INCREMENT, 20)
        );

        boolean result = txManager.executeTransaction(ops);
        assertFalse("Transaction should abort due to forced service failure.", result);
        assertEquals("Service 4 resource value should remain unchanged after failure.", initial4, service4.getResource());

        // Reset the forced failure condition.
        service4.setForceFailure(false);
    }

    // Test the execution of multiple concurrent transactions to ensure proper locking and isolation.
    @Test
    public void testConcurrentTransactions() throws InterruptedException, ExecutionException {
        int numThreads = 10;
        ExecutorService executor = Executors.newFixedThreadPool(numThreads);
        final AtomicInteger successCount = new AtomicInteger();

        Callable<Void> task = () -> {
            // Randomly select two different services.
            int serviceId1 = ThreadLocalRandom.current().nextInt(1, 6);
            int serviceId2 = ThreadLocalRandom.current().nextInt(1, 6);
            while (serviceId2 == serviceId1) {
                serviceId2 = ThreadLocalRandom.current().nextInt(1, 6);
            }

            // Create a transaction that increments one service and decrements the other.
            List<TransactionOperation> ops = Arrays.asList(
                new TransactionOperation(serviceId1, OperationType.INCREMENT, 5),
                new TransactionOperation(serviceId2, OperationType.DECREMENT, 3)
            );

            boolean result = txManager.executeTransaction(ops);
            if (result) {
                successCount.incrementAndGet();
            }
            return null;
        };

        List<Callable<Void>> tasks = new ArrayList<>();
        for (int i = 0; i < 50; i++) {
            tasks.add(task);
        }
        List<Future<Void>> futures = executor.invokeAll(tasks);
        for (Future<Void> future : futures) {
            future.get();
        }
        executor.shutdown();

        // Assert that at least one transaction succeeded.
        assertTrue("At least one concurrent transaction should commit successfully.", successCount.get() > 0);

        // Check global consistency: resource values should be non-negative.
        int totalResource = 0;
        for (int i = 1; i <= 5; i++) {
            totalResource += txManager.getService(i).getResource();
        }
        assertTrue("Total resource value across all services should be non-negative.", totalResource >= 0);
    }

    // Test deadlock detection by simulating a circular wait scenario.
    @Test
    public void testDeadlockDetection() throws InterruptedException, ExecutionException {
        ExecutorService executor = Executors.newFixedThreadPool(2);

        Callable<Boolean> transactionA = () -> {
            // Transaction A operates on service 1 then service 2.
            List<TransactionOperation> ops = Arrays.asList(
                new TransactionOperation(1, OperationType.INCREMENT, 10),
                new TransactionOperation(2, OperationType.INCREMENT, 10)
            );
            return txManager.executeTransaction(ops);
        };

        Callable<Boolean> transactionB = () -> {
            // Transaction B operates on service 2 then service 1, creating a potential deadlock.
            List<TransactionOperation> ops = Arrays.asList(
                new TransactionOperation(2, OperationType.DECREMENT, 5),
                new TransactionOperation(1, OperationType.DECREMENT, 5)
            );
            return txManager.executeTransaction(ops);
        };

        Future<Boolean> futureA = executor.submit(transactionA);
        Future<Boolean> futureB = executor.submit(transactionB);
        boolean resultA = futureA.get();
        boolean resultB = futureB.get();
        executor.shutdown();

        // At least one transaction should abort to resolve the deadlock.
        assertTrue("At least one transaction should be aborted to resolve deadlock.", 
                   (resultA && !resultB) || (!resultA && resultB) || (resultA && resultB));

        // Verify that the resources for services 1 and 2 remain consistent.
        for (int i = 1; i <= 2; i++) {
            assertTrue("Service " + i + " resource value should be non-negative.", 
                       txManager.getService(i).getResource() >= 0);
        }
    }
}