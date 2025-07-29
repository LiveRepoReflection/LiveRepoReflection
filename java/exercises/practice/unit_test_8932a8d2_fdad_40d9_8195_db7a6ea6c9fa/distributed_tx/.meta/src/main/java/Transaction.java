package distributed_tx;

public class Transaction {
    private final String source;
    private final String destination;
    private final int amount;
    private final String id;

    public Transaction(String source, String destination, int amount) {
        this.source = source;
        this.destination = destination;
        this.amount = amount;
        this.id = source + "_" + destination + "_" + amount;
    }

    public String getSource() {
        return source;
    }

    public String getDestination() {
        return destination;
    }

    public int getAmount() {
        return amount;
    }

    public String getId() {
        return id;
    }
}