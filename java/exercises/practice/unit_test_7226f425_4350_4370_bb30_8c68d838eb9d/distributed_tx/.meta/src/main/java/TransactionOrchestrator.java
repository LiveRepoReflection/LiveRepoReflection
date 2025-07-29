package distributed_tx;

import java.util.concurrent.ConcurrentHashMap;

public class TransactionOrchestrator {
    private InventoryService inventoryService;
    private PaymentService paymentService;
    private ShippingService shippingService;
    private OrderService orderService;
    private static ConcurrentHashMap<String, Boolean> processedOrders = new ConcurrentHashMap<>();

    public TransactionOrchestrator() {
        this.inventoryService = new InventoryService();
        this.paymentService = new PaymentService();
        this.shippingService = new ShippingService();
        this.orderService = new OrderService();
    }

    public TransactionResult processOrder(Order order) {
        if (processedOrders.containsKey(order.getOrderId())) {
            TransactionResult.Status status = order.getStatus() == Order.Status.COMPLETED ? TransactionResult.Status.SUCCESS : TransactionResult.Status.FAILED;
            return new TransactionResult(status);
        }
        
        processedOrders.put(order.getOrderId(), true);
        order.incrementProcessingCount();
        order.setStatus(Order.Status.PROCESSING);
        boolean inventoryReserved = false;
        boolean paymentProcessed = false;
        boolean shippingScheduled = false;
        boolean orderCreated = false;
        
        try {
            if (order.getInventoryItemId() != null) {
                inventoryReserved = inventoryService.reserveItem(order.getInventoryItemId());
                if (!inventoryReserved) {
                    throw new Exception("Inventory reservation failed due to optimistic locking.");
                }
            }
            
            paymentProcessed = paymentService.processPayment(order);
            if (!paymentProcessed) {
                throw new Exception("Payment processing failed.");
            }
            
            shippingScheduled = shippingService.scheduleShipping(order);
            if (!shippingScheduled) {
                throw new Exception("Shipping scheduling failed.");
            }
            
            orderCreated = orderService.createOrder(order);
            if (!orderCreated) {
                throw new Exception("Order creation failed.");
            }
            
            order.setStatus(Order.Status.COMPLETED);
            return new TransactionResult(TransactionResult.Status.SUCCESS);
        } catch (Exception ex) {
            if (orderCreated) {
                orderService.deleteOrder(order);
            }
            if (shippingScheduled) {
                shippingService.cancelShipping(order);
            }
            if (paymentProcessed) {
                paymentService.refundPayment(order);
            }
            if (inventoryReserved && order.getInventoryItemId() != null) {
                inventoryService.releaseItem(order.getInventoryItemId());
            }
            order.setCompensationExecuted(true);
            order.setStatus(Order.Status.FAILED);
            return new TransactionResult(TransactionResult.Status.FAILED);
        }
    }
}