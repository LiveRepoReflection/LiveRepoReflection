import java.util.concurrent.ConcurrentHashMap;

public class RateLimiter {

    private volatile int maxRequests;
    private volatile long windowMillis;
    private final ConcurrentHashMap<String, UserRecord> userRecords;

    public RateLimiter(int maxRequests, long windowMillis) {
        this.maxRequests = maxRequests;
        this.windowMillis = windowMillis;
        this.userRecords = new ConcurrentHashMap<>();
    }

    /**
     * Allows a request for the given user if it is within the rate limit.
     * @param user a unique identifier for a user (can be user ID, IP, etc.)
     * @return true if the request is allowed, false otherwise.
     */
    public boolean allowRequest(String user) {
        long now = System.currentTimeMillis();
        // Create or get the current record for the user.
        UserRecord record = userRecords.computeIfAbsent(user, k -> new UserRecord(now, 0));

        // Synchronize on the record to ensure that checking and updating is atomic for that user.
        synchronized (record) {
            // If the current window has expired. Reset the record.
            if (now - record.windowStart >= windowMillis) {
                record.windowStart = now;
                record.count = 1;
                return true;
            } else {
                // Within current window. If request count is under limit, increment.
                if (record.count < maxRequests) {
                    record.count++;
                    return true;
                } else {
                    return false;
                }
            }
        }
    }

    /**
     * Dynamically update the rate limit configuration.
     * @param newMaxRequests new maximum number of requests allowed in the specified window.
     * @param newWindowMillis new time window in milliseconds.
     */
    public void updateLimit(int newMaxRequests, long newWindowMillis) {
        this.maxRequests = newMaxRequests;
        this.windowMillis = newWindowMillis;
    }

    /**
     * Inner class to represent a user's request record.
     */
    private static class UserRecord {
        long windowStart;
        int count;

        UserRecord(long windowStart, int count) {
            this.windowStart = windowStart;
            this.count = count;
        }
    }
}