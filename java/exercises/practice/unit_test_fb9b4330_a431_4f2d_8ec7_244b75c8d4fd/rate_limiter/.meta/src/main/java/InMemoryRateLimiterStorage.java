import java.time.Instant;
import java.util.Map;
import java.util.Queue;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class InMemoryRateLimiterStorage implements RateLimiterStorage {
    // Map of client ID -> map of time window -> request timestamps
    private final Map<String, Map<Integer, Queue<Long>>> requestTimestamps;
    // Lock for each client to prevent race conditions
    private final Map<String, Lock> clientLocks;
    private final ScheduledExecutorService cleanupExecutor;
    
    public InMemoryRateLimiterStorage() {
        this.requestTimestamps = new ConcurrentHashMap<>();
        this.clientLocks = new ConcurrentHashMap<>();
        this.cleanupExecutor = Executors.newSingleThreadScheduledExecutor();
        
        // Schedule periodic cleanup of expired timestamps
        this.cleanupExecutor.scheduleAtFixedRate(
            this::cleanupExpiredTimestamps, 
            60, // initial delay
            60, // period
            TimeUnit.SECONDS
        );
    }
    
    @Override
    public boolean incrementAndCheckLimit(String clientId, int maxRequests, int timeWindowInSeconds) 
            throws DistributedRateLimiterException {
        if (clientId == null || clientId.isEmpty()) {
            throw new DistributedRateLimiterException("Client ID cannot be null or empty");
        }
        if (maxRequests <= 0) {
            throw new DistributedRateLimiterException("Max requests must be greater than zero");
        }
        if (timeWindowInSeconds <= 0) {
            throw new DistributedRateLimiterException("Time window must be greater than zero");
        }
        
        // Get or create lock for this client
        Lock lock = clientLocks.computeIfAbsent(clientId, k -> new ReentrantLock());
        
        lock.lock();
        try {
            // Get or create the map for this client
            Map<Integer, Queue<Long>> clientWindows = requestTimestamps.computeIfAbsent(clientId, k -> new ConcurrentHashMap<>());
            
            // Get or create the queue for this time window
            Queue<Long> timestamps = clientWindows.computeIfAbsent(timeWindowInSeconds, k -> new ConcurrentLinkedQueue<>());
            
            long currentTime = Instant.now().getEpochSecond();
            long cutoffTime = currentTime - timeWindowInSeconds;
            
            // Remove expired timestamps
            while (!timestamps.isEmpty() && timestamps.peek() <= cutoffTime) {
                timestamps.poll();
            }
            
            // Check if we're at the limit
            if (timestamps.size() >= maxRequests) {
                return false;
            }
            
            // Add the current timestamp
            timestamps.add(currentTime);
            return true;
        } finally {
            lock.unlock();
        }
    }
    
    private void cleanupExpiredTimestamps() {
        long currentTime = Instant.now().getEpochSecond();
        
        for (Map.Entry<String, Map<Integer, Queue<Long>>> clientEntry : requestTimestamps.entrySet()) {
            String clientId = clientEntry.getKey();
            Map<Integer, Queue<Long>> clientWindows = clientEntry.getValue();
            
            Lock lock = clientLocks.get(clientId);
            if (lock != null) {
                lock.lock();
                try {
                    for (Map.Entry<Integer, Queue<Long>> windowEntry : clientWindows.entrySet()) {
                        int timeWindow = windowEntry.getKey();
                        Queue<Long> timestamps = windowEntry.getValue();
                        
                        long cutoffTime = currentTime - timeWindow;
                        
                        // Remove expired timestamps
                        while (!timestamps.isEmpty() && timestamps.peek() <= cutoffTime) {
                            timestamps.poll();
                        }
                        
                        // If all timestamps are removed, remove the queue
                        if (timestamps.isEmpty()) {
                            clientWindows.remove(timeWindow);
                        }
                    }
                    
                    // If all windows are removed, remove the client
                    if (clientWindows.isEmpty()) {
                        requestTimestamps.remove(clientId);
                        clientLocks.remove(clientId);
                    }
                } finally {
                    lock.unlock();
                }
            }
        }
    }
    
    @Override
    public void close() {
        cleanupExecutor.shutdown();
        try {
            if (!cleanupExecutor.awaitTermination(5, TimeUnit.SECONDS)) {
                cleanupExecutor.shutdownNow();
            }
        } catch (InterruptedException e) {
            cleanupExecutor.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }
}