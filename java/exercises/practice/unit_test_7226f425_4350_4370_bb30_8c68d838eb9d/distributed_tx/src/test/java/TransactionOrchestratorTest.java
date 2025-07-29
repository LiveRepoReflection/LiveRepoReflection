package distributed_tx;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.concurrent.Callable;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.ExecutionException;

public class TransactionOrchestratorTest {

    private TransactionOrchestrator orchestrator;

    @BeforeEach
    public void setup() {
        // Assume TransactionOrchestrator has a default constructor.
        orchestrator = new TransactionOrchestrator();
    }

    // Test case for a successful transaction execution.
    @Test
    public void testSuccessfulTransaction() {
        Order order = new Order("order123", Order.Status.NEW);
        TransactionResult result = orchestrator.processOrder(order);
        assertNotNull(result, "Result should not be null.");
        assertEquals(TransactionResult.Status.SUCCESS, result.getStatus(), "Transaction should succeed.");
    }

    // Test case where a failure in the Payment Service should trigger compensation across all services.
    @Test
    public void testPaymentFailureTransaction() {
        Order order = new Order("orderPaymentFail", Order.Status.NEW);
        order.setSimulatePaymentFailure(true);
        TransactionResult result = orchestrator.processOrder(order);
        assertNotNull(result, "Result should not be null.");
        assertEquals(TransactionResult.Status.FAILED, result.getStatus(), "Transaction should fail due to payment error.");
        // Verify that compensation is executed in case of failure.
        assertTrue(order.isCompensationExecuted(), "Compensation should be executed upon failure.");
    }

    // Test idempotency: Processing the same order twice should not duplicate actions.
    @Test
    public void testIdempotency() {
        Order order = new Order("orderIdempotent", Order.Status.NEW);
        TransactionResult firstResult = orchestrator.processOrder(order);
        TransactionResult secondResult = orchestrator.processOrder(order);
        assertNotNull(firstResult, "First result should not be null.");
        assertNotNull(secondResult, "Second result should not be null.");
        assertEquals(firstResult.getStatus(), secondResult.getStatus(), "Both transactions should have the same status.");
        assertEquals(1, order.getProcessingCount(), "Order should be processed only once.");
    }

    // Test concurrent processing of multiple orders.
    @Test
    public void testConcurrentTransactions() throws InterruptedException, ExecutionException {
        int numOrders = 20;
        ExecutorService executor = Executors.newFixedThreadPool(5);
        Callable<TransactionResult>[] tasks = new Callable[numOrders];
        Order[] orders = new Order[numOrders];

        for (int i = 0; i < numOrders; i++) {
            final int idx = i;
            orders[i] = new Order("order_" + idx, Order.Status.NEW);
            tasks[i] = () -> orchestrator.processOrder(orders[idx]);
        }

        Future<TransactionResult>[] futures = new Future[numOrders];
        for (int i = 0; i < numOrders; i++) {
            futures[i] = executor.submit(tasks[i]);
        }

        for (int i = 0; i < numOrders; i++) {
            TransactionResult result = futures[i].get();
            assertNotNull(result, "Result should not be null for order " + i);
            assertEquals(TransactionResult.Status.SUCCESS, result.getStatus(), "Transaction should succeed for order " + i);
        }

        executor.shutdown();
        assertTrue(executor.awaitTermination(5, TimeUnit.SECONDS), "Executor did not shut down in time.");
    }

    // Test optimistic locking by simulating multiple orders attempting to reserve the same inventory item.
    @Test
    public void testOptimisticLockingInInventory() throws InterruptedException {
        int numOrders = 10;
        ExecutorService executor = Executors.newFixedThreadPool(5);
        CountDownLatch latch = new CountDownLatch(numOrders);
        ConcurrentLinkedQueue<TransactionResult> resultsQueue = new ConcurrentLinkedQueue<>();

        for (int i = 0; i < numOrders; i++) {
            final String orderId = "order_optimistic_" + i;
            executor.submit(() -> {
                Order order = new Order(orderId, Order.Status.NEW);
                order.setInventoryItemId("item123"); // Simulate contention on the same inventory item.
                TransactionResult result = orchestrator.processOrder(order);
                resultsQueue.add(result);
                latch.countDown();
            });
        }

        latch.await(5, TimeUnit.SECONDS);
        executor.shutdown();
        int successCount = 0;
        int failedCount = 0;
        for (TransactionResult res : resultsQueue) {
            if (res.getStatus() == TransactionResult.Status.SUCCESS) {
                successCount++;
            } else {
                failedCount++;
            }
        }
        // Only one order should succeed in acquiring the inventory lock.
        assertEquals(1, successCount, "Only one order should successfully reserve the inventory item.");
        assertEquals(numOrders - 1, failedCount, "The remaining orders should fail due to optimistic locking.");
    }
}