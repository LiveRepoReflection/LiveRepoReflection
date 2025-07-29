package rate_limiter;

import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

public class RateLimiterImpl implements RateLimiter {
    private final int maxRequests;
    private final long timeWindowInMillis;
    private final ConcurrentHashMap<String, ClientRequestInfo> clientInfoMap;

    public RateLimiterImpl(int maxRequests, long timeWindowInMillis) {
        this.maxRequests = maxRequests;
        this.timeWindowInMillis = timeWindowInMillis;
        this.clientInfoMap = new ConcurrentHashMap<>();
    }

    @Override
    public boolean allowRequest(String clientId) {
        long currentTime = System.currentTimeMillis();
        ClientRequestInfo info = clientInfoMap.computeIfAbsent(clientId, k -> new ClientRequestInfo(currentTime, new AtomicInteger(0)));
        synchronized (info) {
            // Reset the counter if the time window has passed
            if (currentTime - info.startTime >= timeWindowInMillis) {
                info.startTime = currentTime;
                info.count.set(0);
            }

            if (info.count.get() < maxRequests) {
                info.count.incrementAndGet();
                return true;
            } else {
                return false;
            }
        }
    }

    private static class ClientRequestInfo {
        volatile long startTime;
        AtomicInteger count;

        ClientRequestInfo(long startTime, AtomicInteger count) {
            this.startTime = startTime;
            this.count = count;
        }
    }
}