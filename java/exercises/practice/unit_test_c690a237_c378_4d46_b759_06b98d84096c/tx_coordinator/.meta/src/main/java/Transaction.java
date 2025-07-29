import java.io.Serializable;
import java.util.List;
import java.util.Map;

public class Transaction implements Serializable {
    private final String id;
    private final Map<BankServer, List<Operation>> bankOperations;

    public Transaction(String id, Map<BankServer, List<Operation>> bankOperations) {
        this.id = id;
        this.bankOperations = bankOperations;
    }

    public String getId() {
        return id;
    }

    public List<Operation> getOperations(BankServer bank) {
        return bankOperations.get(bank);
    }
}