import java.io.Serializable;
import java.util.Objects;

/**
 * Represents a rate limiting rule that specifies the maximum number
 * of requests allowed for a specific target within a time window.
 */
public class RateLimitRule implements Serializable {
    private static final long serialVersionUID = 1L;
    
    private final String id;
    private final String target;
    private final int limit;
    private final int window;
    
    /**
     * Constructs a new RateLimitRule.
     *
     * @param id The unique identifier for the rule.
     * @param target The target (user ID, service ID, or "*" for wildcard) this rule applies to.
     * @param limit The maximum number of requests allowed in the time window.
     * @param window The time window in seconds.
     */
    public RateLimitRule(String id, String target, int limit, int window) {
        this.id = id;
        this.target = target;
        this.limit = limit;
        this.window = window;
    }
    
    /**
     * Gets the unique identifier of this rule.
     *
     * @return The rule ID.
     */
    public String getId() {
        return id;
    }
    
    /**
     * Gets the target of this rule.
     *
     * @return The target identifier or "*" for wildcard.
     */
    public String getTarget() {
        return target;
    }
    
    /**
     * Gets the maximum number of requests allowed in the time window.
     *
     * @return The request limit.
     */
    public int getLimit() {
        return limit;
    }
    
    /**
     * Gets the time window in seconds.
     *
     * @return The time window.
     */
    public int getWindow() {
        return window;
    }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        RateLimitRule that = (RateLimitRule) o;
        return limit == that.limit &&
               window == that.window &&
               Objects.equals(id, that.id) &&
               Objects.equals(target, that.target);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(id, target, limit, window);
    }
    
    @Override
    public String toString() {
        return "RateLimitRule{" +
               "id='" + id + '\'' +
               ", target='" + target + '\'' +
               ", limit=" + limit +
               ", window=" + window +
               '}';
    }
}