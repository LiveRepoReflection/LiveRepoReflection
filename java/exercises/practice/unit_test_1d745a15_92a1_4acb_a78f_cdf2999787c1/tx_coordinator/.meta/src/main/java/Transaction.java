import java.util.List;

public class Transaction {
    public String transactionID;
    public List<Operation> operations;

    public Transaction(String transactionID, List<Operation> operations) {
        this.transactionID = transactionID;
        this.operations = operations;
    }
}