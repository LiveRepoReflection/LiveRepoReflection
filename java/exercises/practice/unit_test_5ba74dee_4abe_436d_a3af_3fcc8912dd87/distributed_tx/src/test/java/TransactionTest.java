import org.junit.jupiter.api.Test;
import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

class TransactionTest {

    @Test
    void testTransactionCreation() {
        Transaction transaction = new Transaction("tx1");
        assertThat(transaction.getId()).isEqualTo("tx1");
        assertThat(transaction.getOperations()).isEmpty();
    }

    @Test
    void testAddOperation() {
        Transaction transaction = new Transaction("tx1");
        transaction.addOperation("service1", "operation1");
        transaction.addOperation("service2", "operation2");

        assertThat(transaction.getOperations()).hasSize(2);
        assertThat(transaction.getOperations()).containsKeys("service1", "service2");
    }

    @Test
    void testNullId() {
        assertThatThrownBy(() -> new Transaction(null))
            .isInstanceOf(IllegalArgumentException.class)
            .hasMessageContaining("Transaction ID cannot be null");
    }

    @Test
    void testEmptyId() {
        assertThatThrownBy(() -> new Transaction(""))
            .isInstanceOf(IllegalArgumentException.class)
            .hasMessageContaining("Transaction ID cannot be empty");
    }

    @Test
    void testNullServiceId() {
        Transaction transaction = new Transaction("tx1");
        assertThatThrownBy(() -> transaction.addOperation(null, "operation1"))
            .isInstanceOf(IllegalArgumentException.class)
            .hasMessageContaining("Service ID cannot be null");
    }

    @Test
    void testNullOperation() {
        Transaction transaction = new Transaction("tx1");
        assertThatThrownBy(() -> transaction.addOperation("service1", null))
            .isInstanceOf(IllegalArgumentException.class)
            .hasMessageContaining("Operation cannot be null");
    }
}