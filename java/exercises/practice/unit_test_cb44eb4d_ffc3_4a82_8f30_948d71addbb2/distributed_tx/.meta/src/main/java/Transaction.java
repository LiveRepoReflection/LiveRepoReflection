package distributed_tx;

import java.util.List;
import java.util.Set;

public interface Transaction {
    String transactionId();
    List<Operation> operations();
    Set<BankServer> participatingServers();
}