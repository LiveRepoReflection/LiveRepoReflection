import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;
import org.mockito.Mockito;

import java.util.UUID;
import java.util.concurrent.TimeUnit;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class TransactionCoordinatorTest {

    private TransactionCoordinator coordinator;
    private MockMicroservice[] mockServices;
    private static final int NUM_SERVICES = 5;

    @BeforeEach
    void setUp() {
        // Create real coordinator with mocked services
        mockServices = new MockMicroservice[NUM_SERVICES];
        for (int i = 0; i < NUM_SERVICES; i++) {
            mockServices[i] = Mockito.mock(MockMicroservice.class);
        }
        
        coordinator = new TransactionCoordinator(NUM_SERVICES) {
            @Override
            protected MockMicroservice[] createMicroservices(int numServices) {
                return mockServices;
            }
        };
    }

    @Test
    void beginShouldReturnUniqueTransactionIds() {
        UUID tx1 = coordinator.begin();
        UUID tx2 = coordinator.begin();
        
        assertNotNull(tx1);
        assertNotNull(tx2);
        assertNotEquals(tx1, tx2);
    }

    @Test
    void registerShouldThrowExceptionForInvalidTransactionId() {
        UUID invalidTxId = UUID.randomUUID(); // Not registered with begin()
        
        Exception exception = assertThrows(IllegalArgumentException.class, () -> {
            coordinator.register(invalidTxId, 0, "Test data");
        });
        
        assertTrue(exception.getMessage().contains("Transaction not found"));
    }

    @Test
    void registerShouldThrowExceptionForInvalidServiceId() {
        UUID txId = coordinator.begin();
        
        Exception exception = assertThrows(IllegalArgumentException.class, () -> {
            coordinator.register(txId, NUM_SERVICES + 1, "Test data");
        });
        
        assertTrue(exception.getMessage().contains("Invalid service ID"));
    }

    @Test
    void registerShouldAcceptValidParameters() {
        UUID txId = coordinator.begin();
        
        // This should not throw any exceptions
        coordinator.register(txId, 0, "Test data");
        coordinator.register(txId, NUM_SERVICES - 1, "More test data");
    }

    @Test
    void commitShouldExecuteAllRegisteredOperations() {
        UUID txId = coordinator.begin();
        String data1 = "Operation data 1";
        String data2 = "Operation data 2";
        
        coordinator.register(txId, 0, data1);
        coordinator.register(txId, 1, data2);
        
        boolean result = coordinator.commit(txId);
        
        assertTrue(result);
        verify(mockServices[0], times(1)).executeTransaction(txId, data1);
        verify(mockServices[1], times(1)).executeTransaction(txId, data2);
    }

    @Test
    void commitShouldReturnFalseAndRollbackOnFailure() {
        UUID txId = coordinator.begin();
        
        coordinator.register(txId, 0, "Data 1");
        coordinator.register(txId, 1, "Data 2");
        
        // Make service 1 fail during execution
        doThrow(new RuntimeException("Simulated failure"))
            .when(mockServices[1]).executeTransaction(eq(txId), anyString());
        
        boolean result = coordinator.commit(txId);
        
        assertFalse(result);
        // Verify rollback was called on both services
        verify(mockServices[0], times(1)).rollbackTransaction(txId);
        verify(mockServices[1], times(1)).rollbackTransaction(txId);
    }

    @Test
    @Timeout(value = 1, unit = TimeUnit.SECONDS)
    void commitShouldExecuteServicesConcurrently() {
        UUID txId = coordinator.begin();
        
        // Register multiple services
        for (int i = 0; i < NUM_SERVICES; i++) {
            coordinator.register(txId, i, "Data " + i);
            
            // Make each service take 200ms to execute
            doAnswer(invocation -> {
                Thread.sleep(200);
                return null;
            }).when(mockServices[i]).executeTransaction(eq(txId), anyString());
        }
        
        // If services execute sequentially, this would take 5*200ms = 1000ms
        // With concurrency, it should take ~200ms
        long startTime = System.currentTimeMillis();
        coordinator.commit(txId);
        long duration = System.currentTimeMillis() - startTime;
        
        // Should take less than 500ms if executed concurrently
        assertTrue(duration < 500, "Execution took " + duration + "ms, should be concurrent");
        
        // Verify all services were called
        for (int i = 0; i < NUM_SERVICES; i++) {
            verify(mockServices[i], times(1)).executeTransaction(eq(txId), anyString());
        }
    }

    @Test
    @Timeout(value = 1, unit = TimeUnit.SECONDS)
    void rollbackShouldExecuteServicesConcurrently() {
        UUID txId = coordinator.begin();
        
        // Register multiple services
        for (int i = 0; i < NUM_SERVICES; i++) {
            coordinator.register(txId, i, "Data " + i);
            
            // Make each service take 200ms to rollback
            doAnswer(invocation -> {
                Thread.sleep(200);
                return null;
            }).when(mockServices[i]).rollbackTransaction(eq(txId));
        }
        
        // If services rollback sequentially, this would take 5*200ms = 1000ms
        // With concurrency, it should take ~200ms
        long startTime = System.currentTimeMillis();
        coordinator.rollback(txId);
        long duration = System.currentTimeMillis() - startTime;
        
        // Should take less than 500ms if executed concurrently
        assertTrue(duration < 500, "Rollback took " + duration + "ms, should be concurrent");
        
        // Verify all services were called
        for (int i = 0; i < NUM_SERVICES; i++) {
            verify(mockServices[i], times(1)).rollbackTransaction(txId);
        }
    }

    @Test
    void rollbackShouldThrowExceptionForInvalidTransactionId() {
        UUID invalidTxId = UUID.randomUUID(); // Not registered with begin()
        
        Exception exception = assertThrows(IllegalArgumentException.class, () -> {
            coordinator.rollback(invalidTxId);
        });
        
        assertTrue(exception.getMessage().contains("Transaction not found"));
    }

    @Test
    void commitShouldThrowExceptionForInvalidTransactionId() {
        UUID invalidTxId = UUID.randomUUID(); // Not registered with begin()
        
        Exception exception = assertThrows(IllegalArgumentException.class, () -> {
            coordinator.commit(invalidTxId);
        });
        
        assertTrue(exception.getMessage().contains("Transaction not found"));
    }

    @Test
    void commitShouldHandleEmptyTransactionList() {
        UUID txId = coordinator.begin();
        // Don't register any services
        
        boolean result = coordinator.commit(txId);
        
        assertTrue(result, "Empty transaction list should commit successfully");
    }
    
    @Test
    void commitShouldHandleExceptionsInRollback() {
        UUID txId = coordinator.begin();
        
        coordinator.register(txId, 0, "Data 0");
        coordinator.register(txId, 1, "Data 1");
        
        // Make service 1 fail during execution
        doThrow(new RuntimeException("Execution failure"))
            .when(mockServices[1]).executeTransaction(eq(txId), anyString());
            
        // Make service 0 fail during rollback
        doThrow(new RuntimeException("Rollback failure"))
            .when(mockServices[0]).rollbackTransaction(eq(txId));
        
        boolean result = coordinator.commit(txId);
        
        assertFalse(result);
        // Verify rollback was attempted on both services
        verify(mockServices[0], times(1)).rollbackTransaction(txId);
        verify(mockServices[1], times(1)).rollbackTransaction(txId);
    }
    
    @Test
    void rollbackShouldHandleExceptions() {
        UUID txId = coordinator.begin();
        
        coordinator.register(txId, 0, "Data 0");
        coordinator.register(txId, 1, "Data 1");
        
        // Make service 0 fail during rollback
        doThrow(new RuntimeException("Rollback failure"))
            .when(mockServices[0]).rollbackTransaction(eq(txId));
        
        // Should not throw exception
        coordinator.rollback(txId);
        
        // Verify rollback was attempted on both services
        verify(mockServices[0], times(1)).rollbackTransaction(txId);
        verify(mockServices[1], times(1)).rollbackTransaction(txId);
    }
}