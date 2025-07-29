public class RateLimitConfiguration {
    private final int limit;
    private final long timeWindowMillis;

    public RateLimitConfiguration(int limit, long timeWindowMillis) {
        this.limit = limit;
        this.timeWindowMillis = timeWindowMillis;
    }

    public int getLimit() {
        return limit;
    }

    public long getTimeWindowMillis() {
        return timeWindowMillis;
    }
}