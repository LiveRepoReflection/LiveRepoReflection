package distributed_tx;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;
import org.junit.jupiter.api.Assertions;

import java.util.List;
import java.util.ArrayList;
import java.util.UUID;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * This unit test suite verifies the functionalities of the Distributed Transaction Coordinator (DTC)
 * which implements a Two-Phase Commit (2PC) protocol across simulated services.
 * It covers cases such as successful commits, rollbacks on failures, timeout handling, idempotency,
 * concurrency, and crash recovery.
 *
 * Note: It is assumed that the production code provides the following:
 * 1. An interface TransactionalService with methods:
 *      boolean prepare(String transactionId) throws Exception;
 *      void commit(String transactionId) throws Exception;
 *      void rollback(String transactionId) throws Exception;
 *
 * 2. A class DistributedTransactionCoordinator with:
 *      DistributedTransactionCoordinator(List<TransactionalService> services, long prepareTimeoutMillis)
 *      TransactionResult executeTransaction();
 *      void recoverPendingTransaction(String transactionId); // For crash recovery simulation
 *
 * 3. A class TransactionResult with:
 *      String getTransactionId();
 *      TransactionState getState(); // where TransactionState is an enum with COMMITTED and ABORTED.
 *
 * If the production code uses different method names or class names,
 * adjust the tests accordingly.
 */
public class DistributedTxCoordinatorTest {

    // Dummy implementation of TransactionalService for testing purposes.
    private static class DummyService implements TransactionalService {
        private final String name;
        private final boolean shouldPrepareSucceed;
        private final long prepareDelayMillis;
        private final boolean idempotent;
        private final AtomicInteger commitCount = new AtomicInteger(0);
        private final AtomicInteger rollbackCount = new AtomicInteger(0);
        // To simulate idempotency, we record if prepare has been executed.
        private final ConcurrentMap<String, Boolean> preparedTransactions = new ConcurrentHashMap<>();

        public DummyService(String name, boolean shouldPrepareSucceed, long prepareDelayMillis, boolean idempotent) {
            this.name = name;
            this.shouldPrepareSucceed = shouldPrepareSucceed;
            this.prepareDelayMillis = prepareDelayMillis;
            this.idempotent = idempotent;
        }

        @Override
        public boolean prepare(String transactionId) throws Exception {
            if (prepareDelayMillis > 0) {
                Thread.sleep(prepareDelayMillis);
            }
            if (idempotent) {
                // If already prepared, return the same decision.
                if (preparedTransactions.containsKey(transactionId)) {
                    return preparedTransactions.get(transactionId);
                }
            }
            preparedTransactions.put(transactionId, shouldPrepareSucceed);
            return shouldPrepareSucceed;
        }

        @Override
        public void commit(String transactionId) throws Exception {
            // Allow idempotent commit.
            if (idempotent) {
                if (commitCount.get() > 0) {
                    return;
                }
            }
            commitCount.incrementAndGet();
        }

        @Override
        public void rollback(String transactionId) throws Exception {
            // Allow idempotent rollback.
            if (idempotent) {
                if (rollbackCount.get() > 0) {
                    return;
                }
            }
            rollbackCount.incrementAndGet();
        }

        public int getCommitCount() {
            return commitCount.get();
        }

        public int getRollbackCount() {
            return rollbackCount.get();
        }

        public String getName() {
            return name;
        }
    }

    // Test 1: All services prepare successfully and commit.
    @Test
    public void testTransactionCommit() throws Exception {
        List<TransactionalService> services = new ArrayList<>();
        services.add(new DummyService("OrderService", true, 0, true));
        services.add(new DummyService("InventoryService", true, 0, true));
        services.add(new DummyService("PaymentService", true, 0, true));
        services.add(new DummyService("NotificationService", true, 0, true));

        DistributedTransactionCoordinator coordinator = new DistributedTransactionCoordinator(services, 5000);
        TransactionResult result = coordinator.executeTransaction();
        Assertions.assertEquals(TransactionState.COMMITTED, result.getState(), 
            "Transaction should commit when all services prepare successfully.");
    }

    // Test 2: One service fails during prepare leading to rollback.
    @Test
    public void testTransactionRollbackOnFailure() throws Exception {
        List<TransactionalService> services = new ArrayList<>();
        services.add(new DummyService("OrderService", true, 0, true));
        services.add(new DummyService("InventoryService", false, 0, true)); // This service fails.
        services.add(new DummyService("PaymentService", true, 0, true));
        services.add(new DummyService("NotificationService", true, 0, true));

        DistributedTransactionCoordinator coordinator = new DistributedTransactionCoordinator(services, 5000);
        TransactionResult result = coordinator.executeTransaction();
        Assertions.assertEquals(TransactionState.ABORTED, result.getState(), 
            "Transaction should abort when one service fails to prepare.");
    }

    // Test 3: Timeout handling when a service delays its prepare response.
    @Test
    @Timeout(10)
    public void testTimeoutHandling() throws Exception {
        List<TransactionalService> services = new ArrayList<>();
        // This service will delay beyond the timeout period.
        services.add(new DummyService("OrderService", true, 6000, true));
        services.add(new DummyService("InventoryService", true, 0, true));
        services.add(new DummyService("PaymentService", true, 0, true));
        services.add(new DummyService("NotificationService", true, 0, true));

        DistributedTransactionCoordinator coordinator = new DistributedTransactionCoordinator(services, 5000);
        TransactionResult result = coordinator.executeTransaction();
        Assertions.assertEquals(TransactionState.ABORTED, result.getState(), 
            "Transaction should abort when a service does not respond within the timeout period.");
    }

    // Test 4: Idempotency - ensure that duplicate commit or rollback messages do not cause repeated operations.
    @Test
    public void testIdempotency() throws Exception {
        DummyService orderService = new DummyService("OrderService", true, 0, true);
        DummyService inventoryService = new DummyService("InventoryService", true, 0, true);
        DummyService paymentService = new DummyService("PaymentService", true, 0, true);
        DummyService notificationService = new DummyService("NotificationService", true, 0, true);

        List<TransactionalService> services = new ArrayList<>();
        services.add(orderService);
        services.add(inventoryService);
        services.add(paymentService);
        services.add(notificationService);

        DistributedTransactionCoordinator coordinator = new DistributedTransactionCoordinator(services, 5000);
        TransactionResult result = coordinator.executeTransaction();
        Assertions.assertEquals(TransactionState.COMMITTED, result.getState(),
            "Transaction should commit when all services prepare successfully.");

        // Trigger duplicate commit messages via recovery (simulate duplicate call on commit).
        coordinator.recoverPendingTransaction(result.getTransactionId());
        // The commit counts should remain 1 each due to idempotency.
        Assertions.assertEquals(1, orderService.getCommitCount(), "OrderService commit should be idempotent.");
        Assertions.assertEquals(1, inventoryService.getCommitCount(), "InventoryService commit should be idempotent.");
        Assertions.assertEquals(1, paymentService.getCommitCount(), "PaymentService commit should be idempotent.");
        Assertions.assertEquals(1, notificationService.getCommitCount(), "NotificationService commit should be idempotent.");
    }

    // Test 5: Concurrency test - running multiple transactions concurrently.
    @Test
    public void testConcurrency() throws Exception {
        int concurrentTransactions = 10;
        ExecutorService executor = Executors.newFixedThreadPool(concurrentTransactions);
        List<Future<TransactionResult>> futures = new ArrayList<>();

        for (int i = 0; i < concurrentTransactions; i++) {
            futures.add(executor.submit(() -> {
                List<TransactionalService> services = new ArrayList<>();
                services.add(new DummyService("OrderService", true, 0, true));
                services.add(new DummyService("InventoryService", true, 0, true));
                services.add(new DummyService("PaymentService", true, 0, true));
                services.add(new DummyService("NotificationService", true, 0, true));

                DistributedTransactionCoordinator coordinator = new DistributedTransactionCoordinator(services, 5000);
                return coordinator.executeTransaction();
            }));
        }

        int committedCount = 0;
        int abortedCount = 0;
        for (Future<TransactionResult> future : futures) {
            TransactionResult result = future.get(10, TimeUnit.SECONDS);
            if (result.getState() == TransactionState.COMMITTED) {
                committedCount++;
            } else {
                abortedCount++;
            }
        }
        // In this test, all transactions should commit.
        Assertions.assertEquals(concurrentTransactions, committedCount, 
            "All concurrent transactions should commit successfully.");
        executor.shutdown();
    }

    // Test 6: Crash recovery simulation - coordinator recovers a pending transaction after a crash.
    @Test
    public void testCrashRecovery() throws Exception {
        // Simulate a coordinator that crashes after prepare phase but before commit.
        List<TransactionalService> services = new ArrayList<>();
        DummyService orderService = new DummyService("OrderService", true, 0, true);
        DummyService inventoryService = new DummyService("InventoryService", true, 0, true);
        DummyService paymentService = new DummyService("PaymentService", true, 0, true);
        DummyService notificationService = new DummyService("NotificationService", true, 0, true);
        services.add(orderService);
        services.add(inventoryService);
        services.add(paymentService);
        services.add(notificationService);

        DistributedTransactionCoordinator coordinator = new DistributedTransactionCoordinator(services, 5000);
        // Start a transaction which gets stuck in the prepare phase.
        TransactionResult pendingResult = coordinator.executeTransaction();
        // Simulate a crash by not completing the commit phase.
        // Now, recover the transaction.
        coordinator.recoverPendingTransaction(pendingResult.getTransactionId());
        // After recovery, the transaction should be committed if all services had prepared successfully.
        // Verify that commit was executed only once per service.
        Assertions.assertEquals(1, orderService.getCommitCount(), "OrderService should commit once after recovery.");
        Assertions.assertEquals(1, inventoryService.getCommitCount(), "InventoryService should commit once after recovery.");
        Assertions.assertEquals(1, paymentService.getCommitCount(), "PaymentService should commit once after recovery.");
        Assertions.assertEquals(1, notificationService.getCommitCount(), "NotificationService should commit once after recovery.");
    }
}