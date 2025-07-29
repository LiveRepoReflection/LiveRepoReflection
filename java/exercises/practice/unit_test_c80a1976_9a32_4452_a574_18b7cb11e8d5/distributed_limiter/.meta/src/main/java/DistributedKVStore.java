public interface DistributedKVStore {
    long increment(String key, long delta, long windowMs);
}