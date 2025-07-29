import java.io.Serializable;

public class Operation implements Serializable {
    private final String type;
    private final int amount;

    public Operation(String type, int amount) {
        this.type = type;
        this.amount = amount;
    }

    public String getType() {
        return type;
    }

    public int getAmount() {
        return amount;
    }
}