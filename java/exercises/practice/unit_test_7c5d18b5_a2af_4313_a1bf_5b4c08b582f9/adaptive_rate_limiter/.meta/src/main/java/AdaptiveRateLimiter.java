import java.util.concurrent.ConcurrentHashMap;
import java.util.Map;
import java.lang.Math;

public class AdaptiveRateLimiter {
    private volatile double throttleFactor = 1.0;
    private final Object lock = new Object();
    private final Map<String, Integer> clientCounts = new ConcurrentHashMap<>();
    private final Map<String, Integer> globalCounts = new ConcurrentHashMap<>();

    // Default client-specific limit
    private final int DEFAULT_CLIENT_LIMIT = 5;

    // Global limits per endpoint
    private final Map<String, Integer> globalLimits = new ConcurrentHashMap<>();

    public AdaptiveRateLimiter() {
        // Configure endpoints with global limits
        globalLimits.put("/global", 10);
        globalLimits.put("/concurrent", 15);
    }

    public boolean allowRequest(String endpoint, String clientId) {
        synchronized(lock) {
            // Compute effective client-specific limit based on adaptive throttle factor
            int effectiveClientLimit = (int)Math.ceil(DEFAULT_CLIENT_LIMIT * throttleFactor);
            String clientKey = endpoint + ":" + clientId;
            int currentClientCount = clientCounts.getOrDefault(clientKey, 0);
            if(currentClientCount >= effectiveClientLimit) {
                return false;
            }

            // Check for global rate limit if configured for the endpoint
            if(globalLimits.containsKey(endpoint)) {
                int configuredGlobalLimit = globalLimits.get(endpoint);
                int effectiveGlobalLimit = (int)Math.ceil(configuredGlobalLimit * throttleFactor);
                int currentGlobalCount = globalCounts.getOrDefault(endpoint, 0);
                if(currentGlobalCount >= effectiveGlobalLimit) {
                    return false;
                }
                // Increment global counter for the endpoint
                globalCounts.put(endpoint, currentGlobalCount + 1);
            }

            // Increment client-specific counter
            clientCounts.put(clientKey, currentClientCount + 1);
            return true;
        }
    }

    // updateBackendStatus simulates backend performance updates and adapts rate limits accordingly.
    // responseTime: backend response time in milliseconds.
    // errorRate: fraction representing the error rate.
    public void updateBackendStatus(int responseTime, double errorRate) {
        synchronized(lock) {
            if(responseTime >= 500 || errorRate > 0.2) {
                throttleFactor = 0.6;
            } else {
                throttleFactor = 1.0;
            }
            // Clear counters to simulate a new time window.
            clientCounts.clear();
            globalCounts.clear();
        }
    }
}