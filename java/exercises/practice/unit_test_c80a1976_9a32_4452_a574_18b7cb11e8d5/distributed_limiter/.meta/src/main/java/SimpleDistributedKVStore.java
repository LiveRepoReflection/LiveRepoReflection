import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;

public class SimpleDistributedKVStore implements DistributedKVStore {

    private static class ValueWithExpiry {
        long value;
        long expiryTime;

        ValueWithExpiry(long value, long expiryTime) {
            this.value = value;
            this.expiryTime = expiryTime;
        }
    }

    private final ConcurrentMap<String, ValueWithExpiry> store = new ConcurrentHashMap<>();

    @Override
    public long increment(String key, long delta, long windowMs) {
        long now = System.currentTimeMillis();
        return store.compute(key, (k, oldVal) -> {
            if (oldVal == null || oldVal.expiryTime <= now) {
                return new ValueWithExpiry(delta, now + windowMs);
            } else {
                oldVal.value += delta;
                return oldVal;
            }
        }).value;
    }
}