import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import java.util.Iterator;
import java.util.List;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.Map;

public class DistributedLimiter {
    private final int limit;
    private final int timeWindowSeconds;
    private final String granularity;
    private final int tolerance;
    private final String evictionPolicy;
    private final int evictionDurationSeconds;
    private final int capacityThreshold = 1000;

    // For GLOBAL and HYBRID, use a shared static counter map.
    private static final ConcurrentMap<String, RateLimitData> globalCounters = new ConcurrentHashMap<>();

    // For SERVER mode, each instance uses its own counter map.
    private final ConcurrentMap<String, RateLimitData> localCounters;

    public DistributedLimiter(int limit, int timeWindowSeconds, String granularity, int tolerance, String evictionPolicy, int evictionDurationSeconds) {
        this.limit = limit;
        this.timeWindowSeconds = timeWindowSeconds;
        this.granularity = granularity;
        this.tolerance = tolerance;
        this.evictionPolicy = evictionPolicy;
        this.evictionDurationSeconds = evictionDurationSeconds;
        if (granularity.equals("SERVER")) {
            localCounters = new ConcurrentHashMap<>();
        } else {
            localCounters = null;
        }
    }

    public boolean allowRequest(String apiKey) {
        long now = System.currentTimeMillis();
        ConcurrentMap<String, RateLimitData> counters = (granularity.equals("SERVER") ? localCounters : globalCounters);

        // Evict expired entries from the counters map
        evictExpiredEntries(counters, now);

        RateLimitData data = counters.computeIfAbsent(apiKey, key -> new RateLimitData(now, 0, now));
        synchronized (data) {
            // Reset the counter if the current window has expired
            if (now - data.windowStartMillis >= timeWindowSeconds * 1000L) {
                data.windowStartMillis = now;
                data.count = 0;
            }
            data.lastAccessMillis = now;
            int currentCount = ++data.count;
            int effectiveLimit = limit;
            if (granularity.equals("HYBRID")) {
                // Calculate the extra allowed requests as per tolerance percentage
                effectiveLimit = limit + (int)Math.floor(limit * (tolerance / 100.0));
            }
            return currentCount <= effectiveLimit;
        }
    }

    private void evictExpiredEntries(ConcurrentMap<String, RateLimitData> counters, long now) {
        if (evictionPolicy.equals("TTL")) {
            // Remove entries that have not been accessed within evictionDurationSeconds
            for (Iterator<Map.Entry<String, RateLimitData>> it = counters.entrySet().iterator(); it.hasNext();) {
                Map.Entry<String, RateLimitData> entry = it.next();
                RateLimitData data = entry.getValue();
                synchronized (data) {
                    if (now - data.lastAccessMillis >= evictionDurationSeconds * 1000L) {
                        it.remove();
                    }
                }
            }
        } else if (evictionPolicy.equals("LRU")) {
            // If the map size exceeds capacity, remove a portion of the least recently used entries
            if (counters.size() > capacityThreshold) {
                List<Map.Entry<String, RateLimitData>> entries = new ArrayList<>(counters.entrySet());
                entries.sort(Comparator.comparingLong(e -> e.getValue().lastAccessMillis));
                int removeCount = entries.size() / 10; // Remove 10% of the entries
                for (int i = 0; i < removeCount; i++) {
                    counters.remove(entries.get(i).getKey());
                }
            }
        }
    }

    private static class RateLimitData {
        long windowStartMillis;
        int count;
        long lastAccessMillis;

        RateLimitData(long windowStartMillis, int count, long lastAccessMillis) {
            this.windowStartMillis = windowStartMillis;
            this.count = count;
            this.lastAccessMillis = lastAccessMillis;
        }
    }
}