import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class TransactionCoordinatorTest {

    private TransactionCoordinator coordinator;

    @BeforeEach
    public void setUp() {
        coordinator = new TransactionCoordinator(5000); // Timeout set to 5 seconds
    }

    @AfterEach
    public void tearDown() {
        coordinator.shutdown(); // Assuming there is a shutdown method for cleanup
    }

    @Test
    public void testBeginCommitAndRollback() {
        long tid = coordinator.begin();
        assertTrue(tid > 0, "Transaction ID should be positive.");
        // Commit without any locks as it's an empty transaction
        assertTrue(coordinator.commit(tid), "Empty transaction should commit successfully.");

        // Trying to rollback after commit should return false
        assertFalse(coordinator.rollback(tid), "Transaction already committed cannot be rolled back.");
    }

    @Test
    public void testLockAcquireAndRelease() throws InterruptedException {
        long tid = coordinator.begin();
        long resourceId = 100L;

        // Acquire lock for the transaction
        assertTrue(coordinator.acquireLock(tid, resourceId), "Lock acquisition should be successful");
        
        // Reentrant lock acquisition should succeed
        assertTrue(coordinator.acquireLock(tid, resourceId), "Reentrant lock acquisition should succeed");

        // Release the lock once, still holding one count for reentrant acquisition
        assertTrue(coordinator.releaseLock(tid, resourceId), "First lock release should be successful");

        // Releasing again should fully release the lock
        assertTrue(coordinator.releaseLock(tid, resourceId), "Second lock release should be successful");

        // Trying to release again should fail as it no longer holds the lock
        assertFalse(coordinator.releaseLock(tid, resourceId), "Releasing a non-held lock should return false");

        // Commit after releasing all locks
        assertTrue(coordinator.commit(tid), "Transaction commit should be successful");
    }

    @Test
    public void testDeadlockDetection() throws InterruptedException {
        // Create two transactions that will deadlock each other
        long tid1 = coordinator.begin();
        long tid2 = coordinator.begin();
        
        long resource1 = 1L;
        long resource2 = 2L;
        
        // T1 acquires resource1, T2 acquires resource2.
        assertTrue(coordinator.acquireLock(tid1, resource1), "T1 should acquire resource1");
        assertTrue(coordinator.acquireLock(tid2, resource2), "T2 should acquire resource2");
        
        // Using separate threads to simulate concurrent lock acquisition leading to deadlock
        ExecutorService executor = Executors.newFixedThreadPool(2);
        CountDownLatch latch = new CountDownLatch(2);
        
        executor.submit(() -> {
            try {
                // T1 tries to acquire resource2, will wait.
                coordinator.acquireLock(tid1, resource2);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            } finally {
                latch.countDown();
            }
        });
        
        executor.submit(() -> {
            try {
                // T2 tries to acquire resource1, will wait.
                coordinator.acquireLock(tid2, resource1);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            } finally {
                latch.countDown();
            }
        });
        
        // Wait enough time for deadlock detection to kick in
        assertTrue(latch.await(10, TimeUnit.SECONDS), "Both threads should complete due to deadlock resolution");
        executor.shutdownNow();

        // One of the transactions should have been aborted due to deadlock
        boolean t1Committed = coordinator.commit(tid1);
        boolean t2Committed = coordinator.commit(tid2);
        assertTrue((t1Committed ^ t2Committed), "Exactly one transaction should have been aborted to resolve deadlock");
    }

    @Test
    public void testLockTimeout() throws InterruptedException {
        // Create two transactions where one waits longer than timeout period
        long tid1 = coordinator.begin();
        long tid2 = coordinator.begin();
        long resourceId = 50L;
        
        // T1 acquires the resource first.
        assertTrue(coordinator.acquireLock(tid1, resourceId), "T1 should acquire lock initially");
        
        // In a separate thread, T2 will try to acquire the same lock.
        ExecutorService executor = Executors.newSingleThreadExecutor();
        CountDownLatch latch = new CountDownLatch(1);
        final boolean[] result = new boolean[1];
        
        executor.submit(() -> {
            try {
                result[0] = coordinator.acquireLock(tid2, resourceId);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            } finally {
                latch.countDown();
            }
        });
        
        // Wait longer than the configured timeout to trigger deadlock/timeout resolution.
        assertTrue(latch.await(7, TimeUnit.SECONDS), "Wait for T2 acquisition to timeout");
        executor.shutdownNow();

        // T2 should have timed out and been aborted or returned false.
        assertFalse(result[0], "T2 should not acquire the lock due to timeout");

        // Cleanup T1.
        assertTrue(coordinator.releaseLock(tid1, resourceId), "T1 releases the lock");
        assertTrue(coordinator.commit(tid1), "T1 commits successfully after releasing lock");
    }

    @Test
    public void testConcurrentTransactions() throws InterruptedException {
        int numTransactions = 100;
        ExecutorService executor = Executors.newFixedThreadPool(10);
        CountDownLatch latch = new CountDownLatch(numTransactions);

        for (int i = 0; i < numTransactions; i++) {
            executor.submit(() -> {
                long tid = coordinator.begin();
                long resource = (long) (Math.random() * 50);
                try {
                    // Try acquiring and releasing a lock
                    if (coordinator.acquireLock(tid, resource)) {
                        // Simulate some operation
                        Thread.sleep((long) (Math.random() * 100));
                        coordinator.releaseLock(tid, resource);
                    }
                    // Randomly commit or rollback
                    if (Math.random() < 0.8) {
                        coordinator.commit(tid);
                    } else {
                        coordinator.rollback(tid);
                    }
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                } finally {
                    latch.countDown();
                }
            });
        }

        assertTrue(latch.await(15, TimeUnit.SECONDS), "All concurrent transactions should complete in time");
        executor.shutdownNow();
    }
}