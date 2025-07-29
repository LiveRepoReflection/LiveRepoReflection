import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;

public class DistributedRateLimiter {
    
    private static class ClientRecord {
        long windowStartSec;
        int count;
        int rateLimit;
        
        ClientRecord(int rateLimit, long windowStartSec) {
            this.rateLimit = rateLimit;
            this.windowStartSec = windowStartSec;
            this.count = 0;
        }
    }
    
    private final ConcurrentMap<String, ClientRecord> clientsMap = new ConcurrentHashMap<>();
    
    public void setRateLimit(String clientId, int rateLimit) {
        long nowSec = System.currentTimeMillis() / 1000;
        clientsMap.compute(clientId, (id, record) -> {
            if (record == null) {
                return new ClientRecord(rateLimit, nowSec);
            } else {
                synchronized(record) {
                    record.rateLimit = rateLimit;
                }
                return record;
            }
        });
    }
    
    public boolean shouldAllow(String clientId) {
        long nowSec = System.currentTimeMillis() / 1000;
        ClientRecord record = clientsMap.get(clientId);
        if (record == null) {
            // If no rate limit is configured for the client, do not allow any requests.
            return false;
        }
        synchronized(record) {
            if (nowSec > record.windowStartSec) {
                record.windowStartSec = nowSec;
                record.count = 0;
            }
            if (record.count < record.rateLimit) {
                record.count++;
                return true;
            } else {
                return false;
            }
        }
    }
}