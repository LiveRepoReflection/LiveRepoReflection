package distributed_tx;

import java.util.concurrent.ConcurrentHashMap;

public class InventoryService {
    private static ConcurrentHashMap<String, Boolean> inventoryLock = new ConcurrentHashMap<>();

    public boolean reserveItem(String itemId) {
        Boolean previous = inventoryLock.putIfAbsent(itemId, true);
        return previous == null;
    }
    
    public void releaseItem(String itemId) {
        inventoryLock.remove(itemId);
    }
}