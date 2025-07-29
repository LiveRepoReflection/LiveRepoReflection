import java.util.concurrent.ConcurrentHashMap;
import java.util.Map;

public class OrderService implements TransactionParticipant {
    private final Map<String, Order> preparedOrders = new ConcurrentHashMap<>();
    private final Map<String, Order> confirmedOrders = new ConcurrentHashMap<>();

    @Override
    public boolean prepare(String txId) {
        if (preparedOrders.containsKey(txId) || confirmedOrders.containsKey(txId)) {
            return true;
        }
        preparedOrders.put(txId, new Order(txId));
        return true;
    }

    @Override
    public boolean commit(String txId) {
        Order order = preparedOrders.remove(txId);
        if (order != null) {
            confirmedOrders.put(txId, order);
            return true;
        }
        return confirmedOrders.containsKey(txId);
    }

    @Override
    public boolean rollback(String txId) {
        preparedOrders.remove(txId);
        return true;
    }

    private static class Order {
        private final String txId;

        public Order(String txId) {
            this.txId = txId;
        }
    }
}