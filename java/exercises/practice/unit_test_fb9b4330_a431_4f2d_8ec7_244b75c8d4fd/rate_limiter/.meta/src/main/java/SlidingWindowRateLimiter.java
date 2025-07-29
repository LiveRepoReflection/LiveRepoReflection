import java.time.Instant;
import java.util.Map;
import java.util.NavigableMap;
import java.util.TreeMap;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

/**
 * A more sophisticated implementation using the sliding window algorithm.
 * This implementation tracks the exact timestamps of requests and gives
 * a more accurate rate limiting.
 */
public class SlidingWindowRateLimiter implements DistributedRateLimiter {
    private final Map<String, ClientState> clientStates;
    
    public SlidingWindowRateLimiter() {
        this.clientStates = new ConcurrentHashMap<>();
    }
    
    @Override
    public boolean isAllowed(String clientId, int maxRequests, int timeWindowInSeconds) {
        if (clientId == null || clientId.isEmpty()) {
            throw new IllegalArgumentException("Client ID cannot be null or empty");
        }
        if (maxRequests <= 0) {
            throw new IllegalArgumentException("Max requests must be greater than zero");
        }
        if (timeWindowInSeconds <= 0) {
            throw new IllegalArgumentException("Time window must be greater than zero");
        }
        
        ClientState state = clientStates.computeIfAbsent(clientId, k -> new ClientState());
        return state.isAllowed(maxRequests, timeWindowInSeconds);
    }
    
    @Override
    public void close() {
        // No resources to clean up
    }
    
    private static class ClientState {
        private final NavigableMap<Long, Integer> requestCounts; // timestamp -> count
        private final Lock lock;
        
        public ClientState() {
            this.requestCounts = new TreeMap<>();
            this.lock = new ReentrantLock();
        }
        
        public boolean isAllowed(int maxRequests, int timeWindowInSeconds) {
            lock.lock();
            try {
                long currentTime = Instant.now().getEpochSecond();
                long cutoffTime = currentTime - timeWindowInSeconds;
                
                // Remove expired entries
                requestCounts.headMap(cutoffTime, false).clear();
                
                // Count total requests in the time window
                int totalRequests = requestCounts.values().stream().mapToInt(Integer::intValue).sum();
                
                if (totalRequests >= maxRequests) {
                    return false;
                }
                
                // Record this request
                requestCounts.merge(currentTime, 1, Integer::sum);
                return true;
            } finally {
                lock.unlock();
            }
        }
    }
}