package distributed_tx;

import java.util.concurrent.ConcurrentHashMap;

public class OrderService {
    private static ConcurrentHashMap<String, Order> orderStore = new ConcurrentHashMap<>();

    public boolean createOrder(Order order) {
        Order prev = orderStore.putIfAbsent(order.getOrderId(), order);
        return prev == null;
    }
    
    public void deleteOrder(Order order) {
        orderStore.remove(order.getOrderId());
    }
}