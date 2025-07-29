package distributed_tx;

public class Operation {
    private final String type; // "debit" or "credit"
    private final String account;
    private final int amount;

    public Operation(String type, String account, int amount) {
        this.type = type;
        this.account = account;
        this.amount = amount;
    }

    public String getType() {
        return type;
    }

    public String getAccount() {
        return account;
    }

    public int getAmount() {
        return amount;
    }
}