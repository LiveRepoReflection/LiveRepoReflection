public class DistributedRateLimiterException extends Exception {
    public DistributedRateLimiterException(String message) {
        super(message);
    }
    
    public DistributedRateLimiterException(String message, Throwable cause) {
        super(message, cause);
    }
}