import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.assertj.core.api.Assertions.assertThat;

@ExtendWith(MockitoExtension.class)
public class TransactionParticipantTest {

    @Test
    void orderServiceOperations() {
        // Given
        OrderService orderService = new OrderService();
        String txId = "test-tx-1";

        // When & Then
        assertThat(orderService.prepare(txId)).isTrue();
        assertThat(orderService.commit(txId)).isTrue();
    }

    @Test
    void paymentServiceOperations() {
        // Given
        PaymentService paymentService = new PaymentService();
        String txId = "test-tx-2";

        // When & Then
        assertThat(paymentService.prepare(txId)).isTrue();
        assertThat(paymentService.commit(txId)).isTrue();
    }

    @Test
    void inventoryServiceOperations() {
        // Given
        InventoryService inventoryService = new InventoryService();
        String txId = "test-tx-3";

        // When & Then
        assertThat(inventoryService.prepare(txId)).isTrue();
        assertThat(inventoryService.commit(txId)).isTrue();
    }

    @Test
    void participantRollback() {
        // Given
        OrderService orderService = new OrderService();
        String txId = "test-tx-4";

        // When
        orderService.prepare(txId);
        boolean rollbackResult = orderService.rollback(txId);

        // Then
        assertThat(rollbackResult).isTrue();
    }
}