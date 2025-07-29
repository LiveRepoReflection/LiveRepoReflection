import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
public class DistributedTransactionManagerTest {

    @Mock
    private InventoryService inventoryService;

    @Mock
    private OrderService orderService;

    private DistributedTransactionManager transactionManager;

    private static final String ITEM_ID = "item-1";
    private static final int QUANTITY = 5;
    private static final String CUSTOMER_ID = "customer-1";
    private static final String ORDER_ID = "order-1";

    @BeforeEach
    void setUp() {
        transactionManager = new DistributedTransactionManagerImpl(inventoryService, orderService);
    }

    @Test
    void successfulTransaction() throws ServiceUnavailableException {
        // Prepare phase successful
        when(inventoryService.decrementStock(eq(ITEM_ID), eq(QUANTITY), any())).thenReturn(true);
        when(orderService.createOrder(any(), any())).thenReturn(true);

        boolean result = transactionManager.executeTransaction(ITEM_ID, QUANTITY, CUSTOMER_ID, ORDER_ID);

        assertThat(result).isTrue();
        verify(inventoryService).decrementStock(eq(ITEM_ID), eq(QUANTITY), any());
        verify(orderService).createOrder(any(), any());
    }

    @Test
    void failedTransactionDueToInventoryServiceFailure() throws ServiceUnavailableException {
        // Prepare phase fails in inventory service
        when(inventoryService.decrementStock(eq(ITEM_ID), eq(QUANTITY), any())).thenReturn(false);

        boolean result = transactionManager.executeTransaction(ITEM_ID, QUANTITY, CUSTOMER_ID, ORDER_ID);

        assertThat(result).isFalse();
        verify(inventoryService).decrementStock(eq(ITEM_ID), eq(QUANTITY), any());
        verify(orderService, never()).createOrder(any(), any());
    }

    @Test
    void failedTransactionDueToOrderServiceFailure() throws ServiceUnavailableException {
        // Prepare phase fails in order service
        when(inventoryService.decrementStock(eq(ITEM_ID), eq(QUANTITY), any())).thenReturn(true);
        when(orderService.createOrder(any(), any())).thenReturn(false);

        boolean result = transactionManager.executeTransaction(ITEM_ID, QUANTITY, CUSTOMER_ID, ORDER_ID);

        assertThat(result).isFalse();
        verify(inventoryService).decrementStock(eq(ITEM_ID), eq(QUANTITY), any());
        verify(orderService).createOrder(any(), any());
        verify(inventoryService).compensateDecrementStock(eq(ITEM_ID), eq(QUANTITY), any());
    }

    @Test
    void temporaryInventoryServiceUnavailability() throws ServiceUnavailableException {
        // Simulate temporary unavailability then success
        when(inventoryService.decrementStock(eq(ITEM_ID), eq(QUANTITY), any()))
            .thenThrow(new ServiceUnavailableException())
            .thenReturn(true);
        when(orderService.createOrder(any(), any())).thenReturn(true);

        boolean result = transactionManager.executeTransaction(ITEM_ID, QUANTITY, CUSTOMER_ID, ORDER_ID);

        assertThat(result).isTrue();
        verify(inventoryService, times(2)).decrementStock(eq(ITEM_ID), eq(QUANTITY), any());
        verify(orderService).createOrder(any(), any());
    }

    @Test
    void persistentInventoryServiceUnavailability() throws ServiceUnavailableException {
        // Simulate persistent unavailability (exceeding retry limit)
        when(inventoryService.decrementStock(eq(ITEM_ID), eq(QUANTITY), any()))
            .thenThrow(new ServiceUnavailableException());

        boolean result = transactionManager.executeTransaction(ITEM_ID, QUANTITY, CUSTOMER_ID, ORDER_ID);

        assertThat(result).isFalse();
        // The exact number of retries depends on implementation
        verify(inventoryService, times(3)).decrementStock(eq(ITEM_ID), eq(QUANTITY), any());
        verify(orderService, never()).createOrder(any(), any());
    }

    @Test
    void rollbackFailureDuringCompensation() throws ServiceUnavailableException {
        // Prepare phase successful for inventory, fails for order
        when(inventoryService.decrementStock(eq(ITEM_ID), eq(QUANTITY), any())).thenReturn(true);
        when(orderService.createOrder(any(), any())).thenReturn(false);
        
        // Compensation fails initially then succeeds
        doThrow(new ServiceUnavailableException())
            .doNothing()
            .when(inventoryService).compensateDecrementStock(eq(ITEM_ID), eq(QUANTITY), any());

        boolean result = transactionManager.executeTransaction(ITEM_ID, QUANTITY, CUSTOMER_ID, ORDER_ID);

        assertThat(result).isFalse();
        verify(inventoryService).decrementStock(eq(ITEM_ID), eq(QUANTITY), any());
        verify(orderService).createOrder(any(), any());
        verify(inventoryService, times(2)).compensateDecrementStock(eq(ITEM_ID), eq(QUANTITY), any());
    }

    @Test
    void concurrentTransactionHandling() throws ServiceUnavailableException {
        // First attempt fails due to optimistic locking (simulate concurrent modification)
        when(inventoryService.decrementStock(eq(ITEM_ID), eq(QUANTITY), any()))
            .thenReturn(true);
        when(orderService.createOrder(any(), any()))
            .thenReturn(false) // First attempt fails due to optimistic locking
            .thenReturn(true); // Second attempt succeeds
            
        // First transaction attempt
        boolean firstResult = transactionManager.executeTransaction(ITEM_ID, QUANTITY, CUSTOMER_ID, ORDER_ID);
        assertThat(firstResult).isFalse();
        
        // Verify compensation was called
        verify(inventoryService).compensateDecrementStock(eq(ITEM_ID), eq(QUANTITY), any());
        
        // Reset mocks for second attempt
        verify(inventoryService).decrementStock(eq(ITEM_ID), eq(QUANTITY), any());
        verify(orderService).createOrder(any(), any());
        
        // Second transaction attempt
        boolean secondResult = transactionManager.executeTransaction(ITEM_ID, QUANTITY, CUSTOMER_ID, ORDER_ID);
        assertThat(secondResult).isTrue();
    }

    @Test
    void idempotencyInPreparePhase() throws ServiceUnavailableException {
        // Simulate idempotent behavior even though service is not guaranteed to be idempotent
        when(inventoryService.decrementStock(eq(ITEM_ID), eq(QUANTITY), any())).thenReturn(true);
        when(orderService.createOrder(any(), any())).thenReturn(true);

        // Execute same transaction twice
        boolean firstResult = transactionManager.executeTransaction(ITEM_ID, QUANTITY, CUSTOMER_ID, ORDER_ID);
        boolean secondResult = transactionManager.executeTransaction(ITEM_ID, QUANTITY, CUSTOMER_ID, ORDER_ID);

        assertThat(firstResult).isTrue();
        assertThat(secondResult).isTrue();
        
        // Each transaction should generate a unique transaction ID
        verify(inventoryService, times(2)).decrementStock(eq(ITEM_ID), eq(QUANTITY), any());
        verify(orderService, times(2)).createOrder(any(), any());
    }
}