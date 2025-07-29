import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.UUID;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
public class TransactionManagerTest {

    @Mock private OrderService orderService;
    @Mock private PaymentService paymentService;
    @Mock private InventoryService inventoryService;
    
    private TransactionManager transactionManager;
    private ExecutorService executorService;

    @BeforeEach
    void setUp() {
        transactionManager = new TransactionManager();
        executorService = Executors.newFixedThreadPool(10);
    }

    @Test
    void successfulTransaction() throws Exception {
        // Given
        String txId = UUID.randomUUID().toString();
        when(inventoryService.prepare(txId)).thenReturn(true);
        when(paymentService.prepare(txId)).thenReturn(true);
        when(orderService.prepare(txId)).thenReturn(true);

        // When
        boolean result = transactionManager.executeTransaction(txId, 
            orderService, paymentService, inventoryService);

        // Then
        assertThat(result).isTrue();
        verify(inventoryService).commit(txId);
        verify(paymentService).commit(txId);
        verify(orderService).commit(txId);
    }

    @Test
    void failedTransactionDueToInventory() throws Exception {
        // Given
        String txId = UUID.randomUUID().toString();
        when(inventoryService.prepare(txId)).thenReturn(false);
        when(paymentService.prepare(txId)).thenReturn(true);
        when(orderService.prepare(txId)).thenReturn(true);

        // When
        boolean result = transactionManager.executeTransaction(txId,
            orderService, paymentService, inventoryService);

        // Then
        assertThat(result).isFalse();
        verify(inventoryService).rollback(txId);
        verify(paymentService).rollback(txId);
        verify(orderService).rollback(txId);
    }

    @Test
    void concurrentTransactions() throws Exception {
        // Given
        int numTransactions = 10;
        CompletableFuture<Boolean>[] futures = new CompletableFuture[numTransactions];
        
        for (int i = 0; i < numTransactions; i++) {
            String txId = UUID.randomUUID().toString();
            when(inventoryService.prepare(txId)).thenReturn(true);
            when(paymentService.prepare(txId)).thenReturn(true);
            when(orderService.prepare(txId)).thenReturn(true);

            final String finalTxId = txId;
            futures[i] = CompletableFuture.supplyAsync(() ->
                transactionManager.executeTransaction(finalTxId,
                    orderService, paymentService, inventoryService),
                executorService);
        }

        // When
        CompletableFuture.allOf(futures).get(5, TimeUnit.SECONDS);

        // Then
        for (CompletableFuture<Boolean> future : futures) {
            assertThat(future.get()).isTrue();
        }
    }

    @Test
    void recoveryAfterCoordinatorFailure() throws Exception {
        // Given
        String txId = UUID.randomUUID().toString();
        transactionManager.logTransactionStart(txId);

        // Simulate coordinator failure
        TransactionManager newTransactionManager = new TransactionManager();

        // When
        boolean recovered = newTransactionManager.recoverTransaction(txId);

        // Then
        assertThat(recovered).isTrue();
        assertThat(newTransactionManager.getTransactionState(txId))
            .isEqualTo(TransactionState.ROLLED_BACK);
    }

    @Test
    void idempotencyTest() throws Exception {
        // Given
        String txId = UUID.randomUUID().toString();
        when(inventoryService.prepare(txId)).thenReturn(true);
        when(paymentService.prepare(txId)).thenReturn(true);
        when(orderService.prepare(txId)).thenReturn(true);

        // When
        boolean firstAttempt = transactionManager.executeTransaction(txId,
            orderService, paymentService, inventoryService);
        boolean secondAttempt = transactionManager.executeTransaction(txId,
            orderService, paymentService, inventoryService);

        // Then
        assertThat(firstAttempt).isTrue();
        assertThat(secondAttempt).isTrue();
        verify(inventoryService, times(1)).prepare(txId);
        verify(paymentService, times(1)).prepare(txId);
        verify(orderService, times(1)).prepare(txId);
    }
}