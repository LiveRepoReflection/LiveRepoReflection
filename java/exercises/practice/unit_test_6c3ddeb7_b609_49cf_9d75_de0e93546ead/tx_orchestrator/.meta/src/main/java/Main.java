import java.util.Arrays;
import java.util.List;

public class Main {
    public static void main(String[] args) {
        TxOrchestrator orchestrator = new TxOrchestrator();
        
        List<Operation> transaction = Arrays.asList(
            new Operation("inventory", "item_id:123,quantity:2", "item_id:123,quantity:2"),
            new Operation("payment", "amount:20", "amount:20"),
            new Operation("shipping", "address:123Main", "address:123Main")
        );
        
        boolean result = orchestrator.executeTransaction(transaction);
        System.out.println("Transaction result: " + result);
    }
}