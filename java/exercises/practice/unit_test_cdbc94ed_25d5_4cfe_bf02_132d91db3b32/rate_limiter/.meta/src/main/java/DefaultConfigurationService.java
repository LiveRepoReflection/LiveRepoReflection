import java.util.Map;
import java.util.HashMap;

public class DefaultConfigurationService implements ConfigurationService {
    private final Map<String, RateLimitConfiguration> configMap = new HashMap<>();

    public DefaultConfigurationService() {
        // Pre-configured rate limits for demonstration.
        // For instance, client1 is allowed 5 requests per 2000ms.
        configMap.put("client1", new RateLimitConfiguration(5, 2000));
        // Another client example: client3 is allowed 10 requests per 1000ms.
        configMap.put("client3", new RateLimitConfiguration(10, 1000));
    }

    @Override
    public RateLimitConfiguration getConfiguration(String clientId) {
        return configMap.get(clientId);
    }

    public void setConfiguration(String clientId, RateLimitConfiguration configuration) {
        configMap.put(clientId, configuration);
    }
}