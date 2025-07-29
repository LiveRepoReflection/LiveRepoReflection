# Multi-Tenant Rate Limiter

This package implements a distributed rate limiter service that operates in a multi-tenant environment. Each tenant has its own independent rate limits, and the rate limiter is designed to be highly available, scalable, and efficient.

## Implementation Details

The solution uses a sliding window algorithm to ensure accurate rate limiting with the following features:

1. **High Concurrency Support**: Thread-safe implementation with locks to handle concurrent requests.
2. **Scalability**: The design can be extended to distribute state across multiple instances (currently uses a mock storage).
3. **Persistence**: Rate limit data persists across restarts (simulated with an in-memory store).
4. **Atomicity**: Request counting is atomic to prevent race conditions.
5. **Accuracy**: The sliding window approach provides better accuracy than simple fixed windows.
6. **Efficiency**: Optimized for both memory and CPU usage with an LRU cache.
7. **Time Window Management**: Tracks and resets request counts for each tenant accurately.
8. **Edge Cases**: Handles various edge cases including invalid inputs.
9. **Low Latency**: Designed for minimal latency per Allow call.
10. **LRU Cache**: Implements an LRU cache to minimize external data access.

## Design Considerations

The implementation uses a sliding window algorithm but could be extended to support:

- **Token Bucket**: Better for handling bursts of traffic.
- **Leaky Bucket**: Good for ensuring constant outflow rate.
- **Fixed Window Counter**: Simpler but less accurate at window boundaries.
- **Sliding Window Log**: Most accurate but higher memory usage.

In a real distributed environment, you would replace the mock storage with Redis or another distributed key-value store, and implement proper distributed locking.

## Usage
