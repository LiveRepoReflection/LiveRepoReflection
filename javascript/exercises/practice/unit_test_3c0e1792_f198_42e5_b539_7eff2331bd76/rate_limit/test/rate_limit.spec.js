const { RateLimiter } = require('../rate_limit');

describe('RateLimiter', () => {
  beforeEach(() => {
    // Reset timers and any shared state if needed.
    jest.useRealTimers();
  });

  test('should allow requests under the limit for a single key', async () => {
    // Create a limiter with limit 3 requests per 1000ms window.
    const limiter = new RateLimiter({ limit: 3, window: 1000 });
    const key = 'user1';

    // First 3 requests should be allowed.
    expect(await limiter.consume(key)).toBe(true);
    expect(await limiter.consume(key)).toBe(true);
    expect(await limiter.consume(key)).toBe(true);
    
    // Fourth request should be rejected.
    expect(await limiter.consume(key)).toBe(false);
  });

  test('should enforce rate limits independently for different keys', async () => {
    const limiter = new RateLimiter({ limit: 2, window: 1000 });
    const key1 = 'user1';
    const key2 = 'user2';

    // For key1, limit of 2 should be reached.
    expect(await limiter.consume(key1)).toBe(true);
    expect(await limiter.consume(key1)).toBe(true);
    expect(await limiter.consume(key1)).toBe(false);

    // For key2, it should still allow two requests.
    expect(await limiter.consume(key2)).toBe(true);
    expect(await limiter.consume(key2)).toBe(true);
    expect(await limiter.consume(key2)).toBe(false);
  });

  test('should reset the count after the sliding window has passed', async () => {
    jest.useFakeTimers();
    const limiter = new RateLimiter({ limit: 2, window: 1000 });
    const key = 'user1';

    // Consume up to the limit.
    expect(await limiter.consume(key)).toBe(true);
    expect(await limiter.consume(key)).toBe(true);
    expect(await limiter.consume(key)).toBe(false);

    // Advance time by a little over the window.
    jest.advanceTimersByTime(1001);

    // The sliding window should now allow new requests.
    expect(await limiter.consume(key)).toBe(true);
    expect(await limiter.consume(key)).toBe(true);
    expect(await limiter.consume(key)).toBe(false);

    jest.useRealTimers();
  });

  test('should share state across distributed instances with a shared store', async () => {
    // Create a simple in-memory shared store object.
    const sharedStore = {};
    const config = { limit: 3, window: 1000 };

    // Two RateLimiter instances sharing the same store.
    const limiter1 = new RateLimiter(config, sharedStore);
    const limiter2 = new RateLimiter(config, sharedStore);
    const key = 'distributedUser';

    // Use limiter1 for first two requests.
    expect(await limiter1.consume(key)).toBe(true);
    expect(await limiter1.consume(key)).toBe(true);

    // Use limiter2 for the next request.
    expect(await limiter2.consume(key)).toBe(true);

    // Further requests from either instance should be rejected.
    expect(await limiter1.consume(key)).toBe(false);
    expect(await limiter2.consume(key)).toBe(false);
  });

  test('should handle concurrent requests correctly without exceeding the limit', async () => {
    const limiter = new RateLimiter({ limit: 5, window: 1000 });
    const key = 'concurrentUser';

    // Create an array of 10 concurrent requests.
    const requests = Array.from({ length: 10 }).map(() => limiter.consume(key));
    const results = await Promise.all(requests);

    // Count how many requests were allowed.
    const allowedCount = results.filter(result => result === true).length;
    expect(allowedCount).toBe(5);

    // The rest should be rejected.
    const rejectedCount = results.filter(result => result === false).length;
    expect(rejectedCount).toBe(5);
  });

  test('should throw error for invalid configuration such as negative window', () => {
    expect(() => {
      new RateLimiter({ limit: 3, window: -100 });
    }).toThrow();
  });

  test('should throw error when an invalid key is provided', async () => {
    const limiter = new RateLimiter({ limit: 3, window: 1000 });
    // Assuming that providing a non-string key should trigger an error.
    await expect(limiter.consume(null)).rejects.toThrow();
    await expect(limiter.consume(123)).rejects.toThrow();
  });
});