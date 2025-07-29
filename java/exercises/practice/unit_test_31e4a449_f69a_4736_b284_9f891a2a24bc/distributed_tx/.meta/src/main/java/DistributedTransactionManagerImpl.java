import java.util.UUID;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;
import java.util.logging.Level;
import java.util.logging.Logger;

public class DistributedTransactionManagerImpl implements DistributedTransactionManager {
    private static final Logger LOGGER = Logger.getLogger(DistributedTransactionManagerImpl.class.getName());
    private static final int MAX_RETRIES = 3;
    private static final long RETRY_DELAY_MS = 500;
    
    private final InventoryService inventoryService;
    private final OrderService orderService;
    private final Lock transactionLock = new ReentrantLock();
    
    public DistributedTransactionManagerImpl(InventoryService inventoryService, OrderService orderService) {
        this.inventoryService = inventoryService;
        this.orderService = orderService;
    }
    
    @Override
    public boolean executeTransaction(String itemId, int quantity, String customerId, String orderId) {
        String transactionId = generateTransactionId();
        LOGGER.info("Starting transaction: " + transactionId + " for order: " + orderId);
        
        try {
            transactionLock.lock();
            
            // PREPARE PHASE
            if (!prepareInventoryService(itemId, quantity, transactionId)) {
                LOGGER.warning("Inventory prepare phase failed for transaction: " + transactionId);
                return false;
            }
            
            OrderDetails orderDetails = new OrderDetails(itemId, quantity, customerId, orderId);
            if (!prepareOrderService(orderDetails, transactionId)) {
                LOGGER.warning("Order prepare phase failed for transaction: " + transactionId);
                compensateInventoryService(itemId, quantity, transactionId);
                return false;
            }
            
            // COMMIT PHASE
            // In a real implementation, we would explicitly commit both services here
            // For this simplified example, we assume the prepare phase performs the actual operation
            
            LOGGER.info("Transaction completed successfully: " + transactionId);
            return true;
            
        } finally {
            transactionLock.unlock();
        }
    }
    
    private boolean prepareInventoryService(String itemId, int quantity, String transactionId) {
        int attempts = 0;
        while (attempts < MAX_RETRIES) {
            try {
                boolean result = inventoryService.decrementStock(itemId, quantity, transactionId);
                if (result) {
                    return true;
                } else {
                    LOGGER.warning("Failed to decrement stock, business logic failure. Transaction: " + transactionId);
                    return false;
                }
            } catch (ServiceUnavailableException e) {
                attempts++;
                if (attempts >= MAX_RETRIES) {
                    LOGGER.severe("Maximum retry attempts reached for inventory service. Transaction: " + transactionId);
                    return false;
                }
                LOGGER.warning("Inventory service temporarily unavailable. Retry attempt " + attempts + " for transaction: " + transactionId);
                sleep(RETRY_DELAY_MS);
            }
        }
        return false;
    }
    
    private boolean prepareOrderService(OrderDetails orderDetails, String transactionId) {
        int attempts = 0;
        while (attempts < MAX_RETRIES) {
            try {
                boolean result = orderService.createOrder(orderDetails, transactionId);
                if (result) {
                    return true;
                } else {
                    LOGGER.warning("Failed to create order, business logic failure. Transaction: " + transactionId);
                    return false;
                }
            } catch (ServiceUnavailableException e) {
                attempts++;
                if (attempts >= MAX_RETRIES) {
                    LOGGER.severe("Maximum retry attempts reached for order service. Transaction: " + transactionId);
                    return false;
                }
                LOGGER.warning("Order service temporarily unavailable. Retry attempt " + attempts + " for transaction: " + transactionId);
                sleep(RETRY_DELAY_MS);
            }
        }
        return false;
    }
    
    private void compensateInventoryService(String itemId, int quantity, String transactionId) {
        int attempts = 0;
        boolean compensationSuccessful = false;
        
        while (!compensationSuccessful && attempts < MAX_RETRIES) {
            try {
                inventoryService.compensateDecrementStock(itemId, quantity, transactionId);
                compensationSuccessful = true;
                LOGGER.info("Successfully compensated inventory service for transaction: " + transactionId);
            } catch (ServiceUnavailableException e) {
                attempts++;
                LOGGER.warning("Failed to compensate inventory service. Retry attempt " + attempts + " for transaction: " + transactionId);
                sleep(RETRY_DELAY_MS);
            }
        }
        
        if (!compensationSuccessful) {
            // In a real system, this would trigger a manual intervention or be logged in a compensation queue
            LOGGER.severe("Failed to compensate inventory service after " + MAX_RETRIES + " attempts. " +
                         "Manual intervention required for transaction: " + transactionId);
        }
    }
    
    private void compensateOrderService(String orderId, String transactionId) {
        int attempts = 0;
        boolean compensationSuccessful = false;
        
        while (!compensationSuccessful && attempts < MAX_RETRIES) {
            try {
                orderService.compensateCreateOrder(orderId, transactionId);
                compensationSuccessful = true;
                LOGGER.info("Successfully compensated order service for transaction: " + transactionId);
            } catch (ServiceUnavailableException e) {
                attempts++;
                LOGGER.warning("Failed to compensate order service. Retry attempt " + attempts + " for transaction: " + transactionId);
                sleep(RETRY_DELAY_MS);
            }
        }
        
        if (!compensationSuccessful) {
            // In a real system, this would trigger a manual intervention or be logged in a compensation queue
            LOGGER.severe("Failed to compensate order service after " + MAX_RETRIES + " attempts. " +
                         "Manual intervention required for transaction: " + transactionId);
        }
    }
    
    private String generateTransactionId() {
        return UUID.randomUUID().toString();
    }
    
    private void sleep(long milliseconds) {
        try {
            Thread.sleep(milliseconds);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}