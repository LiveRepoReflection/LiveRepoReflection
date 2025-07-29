public class Operation {
    public String serverID;
    public String accountID;
    public String operationType; // "Deposit" or "Withdraw"
    public int amount;

    public Operation(String serverID, String accountID, String operationType, int amount) {
        this.serverID = serverID;
        this.accountID = accountID;
        this.operationType = operationType;
        this.amount = amount;
    }
}