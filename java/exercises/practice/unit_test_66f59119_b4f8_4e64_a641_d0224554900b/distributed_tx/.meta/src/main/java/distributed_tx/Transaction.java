package distributed_tx;

public class Transaction {
    private String id;
    private int amount;
    private String debitAccount;
    private String creditAccount;

    public Transaction(String id, int amount, String debitAccount, String creditAccount) {
        this.id = id;
        this.amount = amount;
        this.debitAccount = debitAccount;
        this.creditAccount = creditAccount;
    }

    public String getId() {
        return id;
    }

    public int getAmount() {
        return amount;
    }

    public String getDebitAccount() {
        return debitAccount;
    }

    public String getCreditAccount() {
        return creditAccount;
    }
}