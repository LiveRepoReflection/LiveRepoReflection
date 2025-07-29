import java.util.HashMap;
import java.util.Map;

public class TransactionContext {
    private final String transactionId;
    private final Map<String, Object> serviceData = new HashMap<>();

    public TransactionContext(String transactionId) {
        this.transactionId = transactionId;
    }

    public String getTransactionId() {
        return transactionId;
    }

    public void addServiceData(String serviceName, Object data) {
        serviceData.put(serviceName, data);
    }

    public Object getServiceData(String serviceName) {
        return serviceData.get(serviceName);
    }
}