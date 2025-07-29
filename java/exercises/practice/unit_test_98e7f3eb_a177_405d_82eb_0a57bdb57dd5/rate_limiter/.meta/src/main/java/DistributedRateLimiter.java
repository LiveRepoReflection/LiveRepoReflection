import java.util.LinkedList;
import java.util.concurrent.ConcurrentHashMap;

public class DistributedRateLimiter {

    private static class RequestRecord {
        private final LinkedList<Long> timestamps = new LinkedList<>();

        public synchronized boolean allowRequest(int limit, long windowMillis, long currentTimeMillis) {
            // Remove timestamps that are outside the current time window
            while (!timestamps.isEmpty() && (currentTimeMillis - timestamps.peekFirst()) >= windowMillis) {
                timestamps.pollFirst();
            }
            if (timestamps.size() < limit) {
                timestamps.addLast(currentTimeMillis);
                return true;
            }
            return false;
        }
    }

    // The key is a combination of userId and resourceId.
    private final ConcurrentHashMap<String, RequestRecord> records = new ConcurrentHashMap<>();

    public boolean allowRequest(String userId, String resourceId, int limit, int timeWindowSeconds) {
        if (limit <= 0) {
            throw new IllegalArgumentException("Limit must be greater than 0");
        }
        if (timeWindowSeconds <= 0) {
            throw new IllegalArgumentException("Time window must be greater than 0 seconds");
        }
        if (userId == null || resourceId == null) {
            throw new IllegalArgumentException("User ID and Resource ID must not be null");
        }

        long currentTimeMillis = System.currentTimeMillis();
        long windowMillis = timeWindowSeconds * 1000L;
        String key = userId + ":" + resourceId;

        RequestRecord record = records.computeIfAbsent(key, k -> new RequestRecord());
        return record.allowRequest(limit, windowMillis, currentTimeMillis);
    }
}