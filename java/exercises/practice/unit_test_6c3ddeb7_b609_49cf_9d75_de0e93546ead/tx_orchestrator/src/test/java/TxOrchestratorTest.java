import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Disabled;
import static org.junit.jupiter.api.Assertions.*;
import java.util.List;
import java.util.Arrays;

public class TxOrchestratorTest {
    private TxOrchestrator orchestrator;

    @BeforeEach
    public void setUp() {
        orchestrator = new TxOrchestrator();
    }

    @Test
    public void testSingleTransactionSuccess() {
        List<Operation> operations = Arrays.asList(
            new Operation("inventory", "item_id:123,quantity:2", "item_id:123,quantity:2"),
            new Operation("payment", "amount:20", "amount:20")
        );
        assertTrue(orchestrator.executeTransaction(operations));
    }

    @Disabled("Remove to run test")
    @Test
    public void testSingleTransactionFailure() {
        List<Operation> operations = Arrays.asList(
            new Operation("inventory", "item_id:123,quantity:2", "item_id:123,quantity:2"),
            new Operation("payment", "amount:20,fail:true", "amount:20") // Simulate failure
        );
        assertFalse(orchestrator.executeTransaction(operations));
    }

    @Disabled("Remove to run test")
    @Test
    public void testConcurrentTransactions() throws InterruptedException {
        List<Operation> tx1 = Arrays.asList(
            new Operation("inventory", "item_id:1,quantity:1", "item_id:1,quantity:1"),
            new Operation("payment", "amount:10", "amount:10")
        );

        List<Operation> tx2 = Arrays.asList(
            new Operation("inventory", "item_id:2,quantity:2", "item_id:2,quantity:2"),
            new Operation("payment", "amount:20", "amount:20")
        );

        Thread thread1 = new Thread(() -> assertTrue(orchestrator.executeTransaction(tx1)));
        Thread thread2 = new Thread(() -> assertTrue(orchestrator.executeTransaction(tx2)));

        thread1.start();
        thread2.start();
        thread1.join();
        thread2.join();
    }

    @Disabled("Remove to run test")
    @Test
    public void testDeadlockPrevention() {
        List<Operation> tx1 = Arrays.asList(
            new Operation("inventory", "item_id:1,quantity:1", "item_id:1,quantity:1"),
            new Operation("payment", "amount:10", "amount:10")
        );

        List<Operation> tx2 = Arrays.asList(
            new Operation("payment", "amount:20", "amount:20"),
            new Operation("inventory", "item_id:2,quantity:2", "item_id:2,quantity:2")
        );

        Thread thread1 = new Thread(() -> assertTrue(orchestrator.executeTransaction(tx1)));
        Thread thread2 = new Thread(() -> assertTrue(orchestrator.executeTransaction(tx2)));

        thread1.start();
        thread2.start();
        try {
            thread1.join();
            thread2.join();
        } catch (InterruptedException e) {
            fail("Deadlock occurred");
        }
    }

    @Disabled("Remove to run test")
    @Test
    public void testPartialRollback() {
        List<Operation> operations = Arrays.asList(
            new Operation("inventory", "item_id:123,quantity:2", "item_id:123,quantity:2"),
            new Operation("payment", "amount:20", "amount:20"),
            new Operation("shipping", "address:123Main,fail:true", "address:123Main") // Simulate failure
        );
        assertFalse(orchestrator.executeTransaction(operations));
    }

    @Disabled("Remove to run test")
    @Test
    public void testLargeTransaction() {
        List<Operation> operations = Arrays.asList(
            new Operation("inventory", "item_id:1,quantity:1", "item_id:1,quantity:1"),
            new Operation("inventory", "item_id:2,quantity:2", "item_id:2,quantity:2"),
            new Operation("payment", "amount:10", "amount:10"),
            new Operation("payment", "amount:20", "amount:20"),
            new Operation("shipping", "address:123Main", "address:123Main"),
            new Operation("notification", "email:user@test.com", "email:user@test.com")
        );
        assertTrue(orchestrator.executeTransaction(operations));
    }
}