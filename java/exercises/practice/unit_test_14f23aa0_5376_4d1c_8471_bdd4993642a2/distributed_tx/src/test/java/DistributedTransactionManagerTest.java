import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class DistributedTransactionManagerTest {
    private DistributedTransactionManager dtm;
    private MockInventoryService inventoryService;
    private MockOrderService orderService;

    @BeforeEach
    void setUp() {
        dtm = new DistributedTransactionManager();
        inventoryService = new MockInventoryService();
        orderService = new MockOrderService();
        dtm.registerService("inventoryService", inventoryService);
        dtm.registerService("orderService", orderService);
    }

    @Test
    void testSuccessfulTransaction() {
        String transactionId = dtm.beginTransaction();
        
        Map<String, Object> inventoryData = new HashMap<>();
        inventoryData.put("productId", "prod1");
        inventoryData.put("quantity", 5);
        
        Map<String, Object> orderData = new HashMap<>();
        orderData.put("userId", "user1");
        orderData.put("productId", "prod1");
        orderData.put("quantity", 5);
        
        Map<String, Map<String, Object>> transactionData = Map.of(
            "inventoryService", inventoryData,
            "orderService", orderData
        );
        
        boolean result = dtm.commitTransaction(transactionId, transactionData);
        assertTrue(result);
        assertTrue(inventoryService.isCommitted(transactionId));
        assertTrue(orderService.isCommitted(transactionId));
    }

    @Test
    void testInventoryServiceFailure() {
        inventoryService.setShouldFailPrepare(true);
        
        String transactionId = dtm.beginTransaction();
        
        Map<String, Object> inventoryData = new HashMap<>();
        inventoryData.put("productId", "prod1");
        inventoryData.put("quantity", 5);
        
        Map<String, Object> orderData = new HashMap<>();
        orderData.put("userId", "user1");
        orderData.put("productId", "prod1");
        orderData.put("quantity", 5);
        
        Map<String, Map<String, Object>> transactionData = Map.of(
            "inventoryService", inventoryData,
            "orderService", orderData
        );
        
        boolean result = dtm.commitTransaction(transactionId, transactionData);
        assertFalse(result);
        assertTrue(inventoryService.isRolledBack(transactionId));
        assertTrue(orderService.isRolledBack(transactionId));
    }

    @Test
    void testOrderServiceFailure() {
        orderService.setShouldFailPrepare(true);
        
        String transactionId = dtm.beginTransaction();
        
        Map<String, Object> inventoryData = new HashMap<>();
        inventoryData.put("productId", "prod1");
        inventoryData.put("quantity", 5);
        
        Map<String, Object> orderData = new HashMap<>();
        orderData.put("userId", "user1");
        orderData.put("productId", "prod1");
        orderData.put("quantity", 5);
        
        Map<String, Map<String, Object>> transactionData = Map.of(
            "inventoryService", inventoryData,
            "orderService", orderData
        );
        
        boolean result = dtm.commitTransaction(transactionId, transactionData);
        assertFalse(result);
        assertTrue(inventoryService.isRolledBack(transactionId));
        assertTrue(orderService.isRolledBack(transactionId));
    }

    @Test
    void testConcurrentTransactions() throws InterruptedException {
        int numThreads = 10;
        ExecutorService executor = Executors.newFixedThreadPool(numThreads);
        CountDownLatch latch = new CountDownLatch(numThreads);
        
        for (int i = 0; i < numThreads; i++) {
            final int threadNum = i;
            executor.execute(() -> {
                try {
                    String transactionId = dtm.beginTransaction();
                    
                    Map<String, Object> inventoryData = new HashMap<>();
                    inventoryData.put("productId", "prod" + threadNum);
                    inventoryData.put("quantity", threadNum + 1);
                    
                    Map<String, Object> orderData = new HashMap<>();
                    orderData.put("userId", "user" + threadNum);
                    orderData.put("productId", "prod" + threadNum);
                    orderData.put("quantity", threadNum + 1);
                    
                    Map<String, Map<String, Object>> transactionData = Map.of(
                        "inventoryService", inventoryData,
                        "orderService", orderData
                    );
                    
                    boolean result = dtm.commitTransaction(transactionId, transactionData);
                    assertTrue(result);
                } finally {
                    latch.countDown();
                }
            });
        }
        
        latch.await(5, TimeUnit.SECONDS);
        executor.shutdown();
        
        assertEquals(numThreads, inventoryService.getCommittedCount());
        assertEquals(numThreads, orderService.getCommittedCount());
    }

    @Test
    void testIdempotentOperations() {
        String transactionId = dtm.beginTransaction();
        
        Map<String, Object> inventoryData = new HashMap<>();
        inventoryData.put("productId", "prod1");
        inventoryData.put("quantity", 5);
        
        Map<String, Object> orderData = new HashMap<>();
        orderData.put("userId", "user1");
        orderData.put("productId", "prod1");
        orderData.put("quantity", 5);
        
        Map<String, Map<String, Object>> transactionData = Map.of(
            "inventoryService", inventoryData,
            "orderService", orderData
        );
        
        // First commit attempt
        boolean result1 = dtm.commitTransaction(transactionId, transactionData);
        assertTrue(result1);
        
        // Second commit attempt with same transaction ID
        boolean result2 = dtm.commitTransaction(transactionId, transactionData);
        assertTrue(result2);
        
        // Verify services were only committed once
        assertEquals(1, inventoryService.getCommitCount(transactionId));
        assertEquals(1, orderService.getCommitCount(transactionId));
    }

    @Test
    void testTimeoutHandling() {
        inventoryService.setDelay(2000); // 2 second delay
        dtm.setPrepareTimeout(1000); // 1 second timeout
        
        String transactionId = dtm.beginTransaction();
        
        Map<String, Object> inventoryData = new HashMap<>();
        inventoryData.put("productId", "prod1");
        inventoryData.put("quantity", 5);
        
        Map<String, Object> orderData = new HashMap<>();
        orderData.put("userId", "user1");
        orderData.put("productId", "prod1");
        orderData.put("quantity", 5);
        
        Map<String, Map<String, Object>> transactionData = Map.of(
            "inventoryService", inventoryData,
            "orderService", orderData
        );
        
        boolean result = dtm.commitTransaction(transactionId, transactionData);
        assertFalse(result);
        assertTrue(inventoryService.isRolledBack(transactionId));
        assertTrue(orderService.isRolledBack(transactionId));
    }
}

class MockInventoryService implements ParticipantService {
    private boolean shouldFailPrepare = false;
    private int delay = 0;
    private final Map<String, Boolean> committedTransactions = new HashMap<>();
    private final Map<String, Boolean> rolledBackTransactions = new HashMap<>();
    private final Map<String, Integer> commitCounts = new HashMap<>();

    @Override
    public boolean prepare(String transactionId, Map<String, Object> data) {
        if (delay > 0) {
            try {
                Thread.sleep(delay);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
        return !shouldFailPrepare;
    }

    @Override
    public boolean commit(String transactionId) {
        committedTransactions.put(transactionId, true);
        commitCounts.merge(transactionId, 1, Integer::sum);
        return true;
    }

    @Override
    public boolean rollback(String transactionId) {
        rolledBackTransactions.put(transactionId, true);
        return true;
    }

    public void setShouldFailPrepare(boolean shouldFailPrepare) {
        this.shouldFailPrepare = shouldFailPrepare;
    }

    public void setDelay(int delay) {
        this.delay = delay;
    }

    public boolean isCommitted(String transactionId) {
        return committedTransactions.getOrDefault(transactionId, false);
    }

    public boolean isRolledBack(String transactionId) {
        return rolledBackTransactions.getOrDefault(transactionId, false);
    }

    public int getCommittedCount() {
        return committedTransactions.size();
    }

    public int getCommitCount(String transactionId) {
        return commitCounts.getOrDefault(transactionId, 0);
    }
}

class MockOrderService implements ParticipantService {
    private boolean shouldFailPrepare = false;
    private final Map<String, Boolean> committedTransactions = new HashMap<>();
    private final Map<String, Boolean> rolledBackTransactions = new HashMap<>();
    private final Map<String, Integer> commitCounts = new HashMap<>();

    @Override
    public boolean prepare(String transactionId, Map<String, Object> data) {
        return !shouldFailPrepare;
    }

    @Override
    public boolean commit(String transactionId) {
        committedTransactions.put(transactionId, true);
        commitCounts.merge(transactionId, 1, Integer::sum);
        return true;
    }

    @Override
    public boolean rollback(String transactionId) {
        rolledBackTransactions.put(transactionId, true);
        return true;
    }

    public void setShouldFailPrepare(boolean shouldFailPrepare) {
        this.shouldFailPrepare = shouldFailPrepare;
    }

    public boolean isCommitted(String transactionId) {
        return committedTransactions.getOrDefault(transactionId, false);
    }

    public boolean isRolledBack(String transactionId) {
        return rolledBackTransactions.getOrDefault(transactionId, false);
    }

    public int getCommittedCount() {
        return committedTransactions.size();
    }

    public int getCommitCount(String transactionId) {
        return commitCounts.getOrDefault(transactionId, 0);
    }
}