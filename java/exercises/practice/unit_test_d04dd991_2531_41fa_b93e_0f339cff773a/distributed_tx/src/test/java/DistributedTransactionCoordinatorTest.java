import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import java.util.UUID;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

class DistributedTransactionCoordinatorTest {
    
    private DistributedTransactionCoordinator coordinator;
    
    @Mock
    private ResourceManager resourceManager1;
    
    @Mock
    private ResourceManager resourceManager2;
    
    @Mock
    private ResourceManager resourceManager3;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
        coordinator = new DistributedTransactionCoordinator();
    }

    @Test
    void testSuccessfulTransaction() {
        // Given
        when(resourceManager1.prepare(any(), any())).thenReturn(true);
        when(resourceManager2.prepare(any(), any())).thenReturn(true);
        
        UUID tid = coordinator.beginTransaction();
        coordinator.enlistResource(tid, resourceManager1, "operation1");
        coordinator.enlistResource(tid, resourceManager2, "operation2");

        // When
        boolean result = coordinator.commitTransaction(tid);

        // Then
        assertTrue(result);
        verify(resourceManager1).prepare(eq(tid), eq("operation1"));
        verify(resourceManager2).prepare(eq(tid), eq("operation2"));
        verify(resourceManager1).commit(tid);
        verify(resourceManager2).commit(tid);
    }

    @Test
    void testRollbackWhenPrepareFails() {
        // Given
        when(resourceManager1.prepare(any(), any())).thenReturn(true);
        when(resourceManager2.prepare(any(), any())).thenReturn(false);
        
        UUID tid = coordinator.beginTransaction();
        coordinator.enlistResource(tid, resourceManager1, "operation1");
        coordinator.enlistResource(tid, resourceManager2, "operation2");

        // When
        boolean result = coordinator.commitTransaction(tid);

        // Then
        assertFalse(result);
        verify(resourceManager1).rollback(tid);
        verify(resourceManager2).rollback(tid);
    }

    @Test
    void testExplicitRollback() {
        // Given
        UUID tid = coordinator.beginTransaction();
        coordinator.enlistResource(tid, resourceManager1, "operation1");
        coordinator.enlistResource(tid, resourceManager2, "operation2");

        // When
        coordinator.rollbackTransaction(tid);

        // Then
        verify(resourceManager1).rollback(tid);
        verify(resourceManager2).rollback(tid);
    }

    @Test
    void testConcurrentTransactions() throws InterruptedException {
        // Given
        int numThreads = 5;
        ExecutorService executor = Executors.newFixedThreadPool(numThreads);
        CountDownLatch latch = new CountDownLatch(numThreads);
        
        when(resourceManager1.prepare(any(), any())).thenReturn(true);
        when(resourceManager2.prepare(any(), any())).thenReturn(true);

        // When
        for (int i = 0; i < numThreads; i++) {
            executor.submit(() -> {
                try {
                    UUID tid = coordinator.beginTransaction();
                    coordinator.enlistResource(tid, resourceManager1, "operation1");
                    coordinator.enlistResource(tid, resourceManager2, "operation2");
                    coordinator.commitTransaction(tid);
                } finally {
                    latch.countDown();
                }
            });
        }

        // Then
        assertTrue(latch.await(5, TimeUnit.SECONDS));
        executor.shutdown();
    }

    @Test
    void testResourceManagerTimeout() {
        // Given
        when(resourceManager1.prepare(any(), any())).thenAnswer(invocation -> {
            Thread.sleep(2000); // Simulate slow response
            return true;
        });
        
        UUID tid = coordinator.beginTransaction();
        coordinator.enlistResource(tid, resourceManager1, "operation1");

        // When
        boolean result = coordinator.commitTransaction(tid);

        // Then
        assertFalse(result);
        verify(resourceManager1).rollback(tid);
    }

    @Test
    void testDeadlockDetection() throws InterruptedException {
        // Given
        CountDownLatch latch1 = new CountDownLatch(1);
        CountDownLatch latch2 = new CountDownLatch(1);
        
        when(resourceManager1.prepare(any(), any())).thenAnswer(invocation -> {
            latch1.countDown();
            latch2.await(1, TimeUnit.SECONDS);
            return true;
        });
        
        when(resourceManager2.prepare(any(), any())).thenAnswer(invocation -> {
            latch1.await(1, TimeUnit.SECONDS);
            return true;
        });

        // When
        UUID tid1 = coordinator.beginTransaction();
        UUID tid2 = coordinator.beginTransaction();
        
        coordinator.enlistResource(tid1, resourceManager1, "operation1");
        coordinator.enlistResource(tid1, resourceManager2, "operation2");
        
        coordinator.enlistResource(tid2, resourceManager2, "operation3");
        coordinator.enlistResource(tid2, resourceManager1, "operation4");

        ExecutorService executor = Executors.newFixedThreadPool(2);
        executor.submit(() -> coordinator.commitTransaction(tid1));
        executor.submit(() -> coordinator.commitTransaction(tid2));

        // Then
        executor.shutdown();
        assertTrue(executor.awaitTermination(5, TimeUnit.SECONDS));
        
        // Verify that at least one transaction was rolled back
        verify(resourceManager1, atLeastOnce()).rollback(any());
        verify(resourceManager2, atLeastOnce()).rollback(any());
    }

    @Test
    void testReadOnlyOptimization() {
        // Given
        UUID tid = coordinator.beginTransaction();
        coordinator.enlistResource(tid, resourceManager1, "READ_ONLY:select * from table");
        
        when(resourceManager1.prepare(any(), any())).thenReturn(true);

        // When
        boolean result = coordinator.commitTransaction(tid);

        // Then
        assertTrue(result);
        verify(resourceManager1, never()).commit(tid);
        verify(resourceManager1, never()).rollback(tid);
    }

    @Test
    void testMaximumResourceManagerLimit() {
        // Given
        UUID tid = coordinator.beginTransaction();
        
        // When/Then
        for (int i = 0; i < 10; i++) {
            assertTrue(coordinator.enlistResource(tid, mock(ResourceManager.class), "operation"));
        }
        
        assertThrows(IllegalStateException.class, () -> 
            coordinator.enlistResource(tid, mock(ResourceManager.class), "operation"));
    }
}