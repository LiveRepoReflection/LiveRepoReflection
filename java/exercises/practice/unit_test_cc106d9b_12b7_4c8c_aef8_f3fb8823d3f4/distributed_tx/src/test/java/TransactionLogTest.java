import org.junit.jupiter.api.Test;
import static org.assertj.core.api.Assertions.*;

public class TransactionLogTest {

    @Test
    void testLogEntryCreation() {
        TransactionLog log = new TransactionLog("TX1", TransactionState.PREPARED);
        
        assertThat(log.getTransactionId()).isEqualTo("TX1");
        assertThat(log.getState()).isEqualTo(TransactionState.PREPARED);
        assertThat(log.getTimestamp()).isNotNull();
    }

    @Test
    void testLogPersistence() {
        TransactionLog log = new TransactionLog("TX1", TransactionState.COMMITTED);
        log.persist();
        
        TransactionLog loadedLog = TransactionLog.load("TX1");
        
        assertThat(loadedLog).isNotNull();
        assertThat(loadedLog.getTransactionId()).isEqualTo("TX1");
        assertThat(loadedLog.getState()).isEqualTo(TransactionState.COMMITTED);
    }

    @Test
    void testLogStateTransitions() {
        TransactionLog log = new TransactionLog("TX1", TransactionState.PREPARED);
        
        log.updateState(TransactionState.COMMITTED);
        
        assertThat(log.getState()).isEqualTo(TransactionState.COMMITTED);
    }
}