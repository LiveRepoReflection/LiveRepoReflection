import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

import java.util.UUID;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;

import static org.junit.jupiter.api.Assertions.*;

class DistributedTxManagerTest {
    private DistributedTxManager dtm;
    
    @BeforeEach
    void setUp() {
        dtm = new DistributedTxManager();
    }

    @Test
    void testSuccessfulTransaction() {
        String txId = dtm.startTransaction();
        String serviceId1 = "service1";
        String serviceId2 = "service2";

        // Register two services that will both succeed
        dtm.registerService(serviceId1, 
            () -> CompletableFuture.completedFuture(true),
            () -> CompletableFuture.completedFuture(true));
        
        dtm.registerService(serviceId2,
            () -> CompletableFuture.completedFuture(true),
            () -> CompletableFuture.completedFuture(true));

        dtm.enlistParticipant(txId, serviceId1);
        dtm.enlistParticipant(txId, serviceId2);

        assertTrue(dtm.commitTransaction(txId));
        assertEquals(TransactionStatus.COMMITTED, dtm.getTransactionStatus(txId));
    }

    @Test
    void testRollbackWhenOneServiceFails() {
        String txId = dtm.startTransaction();
        String serviceId1 = "service1";
        String serviceId2 = "service2";

        // First service succeeds, second fails
        dtm.registerService(serviceId1,
            () -> CompletableFuture.completedFuture(true),
            () -> CompletableFuture.completedFuture(true));
        
        dtm.registerService(serviceId2,
            () -> CompletableFuture.completedFuture(false),
            () -> CompletableFuture.completedFuture(true));

        dtm.enlistParticipant(txId, serviceId1);
        dtm.enlistParticipant(txId, serviceId2);

        assertFalse(dtm.commitTransaction(txId));
        assertEquals(TransactionStatus.ROLLED_BACK, dtm.getTransactionStatus(txId));
    }

    @Test
    @Timeout(6)
    void testTimeoutDuringCommit() {
        String txId = dtm.startTransaction();
        String serviceId = "slowService";

        // Register a service that will timeout
        dtm.registerService(serviceId,
            () -> CompletableFuture.supplyAsync(() -> {
                try {
                    Thread.sleep(10000); // Longer than timeout
                    return true;
                } catch (InterruptedException e) {
                    return false;
                }
            }),
            () -> CompletableFuture.completedFuture(true));

        dtm.enlistParticipant(txId, serviceId);

        assertFalse(dtm.commitTransaction(txId));
        assertEquals(TransactionStatus.ROLLED_BACK, dtm.getTransactionStatus(txId));
    }

    @Test
    void testConcurrentTransactions() throws InterruptedException {
        int numTransactions = 100;
        CountDownLatch latch = new CountDownLatch(numTransactions);
        AtomicInteger successCount = new AtomicInteger(0);
        
        // Register some services
        for (int i = 0; i < 5; i++) {
            String serviceId = "service" + i;
            dtm.registerService(serviceId,
                () -> CompletableFuture.completedFuture(true),
                () -> CompletableFuture.completedFuture(true));
        }

        // Start multiple transactions concurrently
        ExecutorService executor = Executors.newFixedThreadPool(10);
        for (int i = 0; i < numTransactions; i++) {
            executor.submit(() -> {
                try {
                    String txId = dtm.startTransaction();
                    dtm.enlistParticipant(txId, "service0");
                    dtm.enlistParticipant(txId, "service1");
                    if (dtm.commitTransaction(txId)) {
                        successCount.incrementAndGet();
                    }
                } finally {
                    latch.countDown();
                }
            });
        }

        latch.await(10, TimeUnit.SECONDS);
        executor.shutdown();
        assertEquals(numTransactions, successCount.get());
    }

    @Test
    void testIdempotencyOfCallbacks() {
        String txId = dtm.startTransaction();
        String serviceId = "service";
        AtomicInteger commitCount = new AtomicInteger(0);
        AtomicInteger rollbackCount = new AtomicInteger(0);

        // Register service with counting callbacks
        dtm.registerService(serviceId,
            () -> {
                commitCount.incrementAndGet();
                return CompletableFuture.completedFuture(true);
            },
            () -> {
                rollbackCount.incrementAndGet();
                return CompletableFuture.completedFuture(true);
            });

        dtm.enlistParticipant(txId, serviceId);

        // Call commit multiple times
        assertTrue(dtm.commitTransaction(txId));
        assertFalse(dtm.commitTransaction(txId)); // Should fail as already committed
        assertFalse(dtm.commitTransaction(txId)); // Should fail as already committed

        assertEquals(1, commitCount.get()); // Should only be called once
        assertEquals(0, rollbackCount.get()); // Should never be called
    }

    @Test
    void testServiceFailureDuringRollback() {
        String txId = dtm.startTransaction();
        String serviceId1 = "service1";
        String serviceId2 = "service2";
        AtomicBoolean service2RollbackCalled = new AtomicBoolean(false);

        // First service fails commit
        dtm.registerService(serviceId1,
            () -> CompletableFuture.completedFuture(false),
            () -> CompletableFuture.failedFuture(new RuntimeException("Rollback failed")));

        // Second service succeeds commit but fails rollback
        dtm.registerService(serviceId2,
            () -> CompletableFuture.completedFuture(true),
            () -> {
                service2RollbackCalled.set(true);
                return CompletableFuture.completedFuture(true);
            });

        dtm.enlistParticipant(txId, serviceId1);
        dtm.enlistParticipant(txId, serviceId2);

        assertFalse(dtm.commitTransaction(txId));
        assertEquals(TransactionStatus.ROLLED_BACK, dtm.getTransactionStatus(txId));
        assertTrue(service2RollbackCalled.get()); // Ensure second service was rolled back
    }
}