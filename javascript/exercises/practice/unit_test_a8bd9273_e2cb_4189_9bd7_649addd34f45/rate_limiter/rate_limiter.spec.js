const RateLimiter = require('./rate_limiter');

describe('RateLimiter', () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  test('should allow requests under the configured limit for a given key', () => {
    const limiter = new RateLimiter({ limit: 3, interval: 1000 });
    const key = 'user1';

    expect(limiter.tryRequest(key)).toBe(true);
    expect(limiter.tryRequest(key)).toBe(true);
    expect(limiter.tryRequest(key)).toBe(true);
    // Fourth request should be rejected.
    expect(limiter.tryRequest(key)).toBe(false);
  });

  test('should reset the counter after the interval expires for a given key', () => {
    const limiter = new RateLimiter({ limit: 2, interval: 1000 });
    const key = 'user2';

    expect(limiter.tryRequest(key)).toBe(true);
    expect(limiter.tryRequest(key)).toBe(true);
    expect(limiter.tryRequest(key)).toBe(false);

    // Fast-forward time beyond the interval
    jest.advanceTimersByTime(1000);

    // After interval reset, requests should be allowed again.
    expect(limiter.tryRequest(key)).toBe(true);
    expect(limiter.tryRequest(key)).toBe(true);
    expect(limiter.tryRequest(key)).toBe(false);
  });

  test('should maintain separate counters for different keys', () => {
    const limiter = new RateLimiter({ limit: 2, interval: 1000 });
    const key1 = 'userA';
    const key2 = 'userB';

    expect(limiter.tryRequest(key1)).toBe(true);
    expect(limiter.tryRequest(key1)).toBe(true);
    expect(limiter.tryRequest(key1)).toBe(false);

    // Requests for key2 should not be affected by key1's usage.
    expect(limiter.tryRequest(key2)).toBe(true);
    expect(limiter.tryRequest(key2)).toBe(true);
    expect(limiter.tryRequest(key2)).toBe(false);
  });

  test('should correctly handle concurrent requests for the same key', async () => {
    const limiter = new RateLimiter({ limit: 5, interval: 1000 });
    const key = 'concurrentUser';
    const requestCount = 10;
    const results = await Promise.all(
      Array.from({ length: requestCount }, () => Promise.resolve(limiter.tryRequest(key)))
    );
    // Only first 5 should be true.
    const allowed = results.filter(result => result === true).length;
    expect(allowed).toBe(5);
    const blocked = results.filter(result => result === false).length;
    expect(blocked).toBe(5);
  });

  test('should return the remaining time until reset if available', () => {
    const limiter = new RateLimiter({ limit: 3, interval: 2000 });
    const key = 'timerTest';

    // Make one request
    expect(limiter.tryRequest(key)).toBe(true);
    const resetTime1 = limiter.getResetTime(key);
    expect(typeof resetTime1).toBe('number');
    expect(resetTime1).toBeGreaterThan(0);

    // Advance time by 1000 ms and check the remaining time
    jest.advanceTimersByTime(1000);
    const resetTime2 = limiter.getResetTime(key);
    expect(resetTime2).toBeGreaterThan(0);
    expect(resetTime2).toBeLessThan(resetTime1);

    // Advance time to expiration and verify reset time is 0 or negative
    jest.advanceTimersByTime(1000);
    const resetTime3 = limiter.getResetTime(key);
    expect(resetTime3).toBeLessThanOrEqual(0);
  });

  test('should handle rapid consecutive requests and renew rate window correctly', () => {
    const limiter = new RateLimiter({ limit: 2, interval: 500 });
    const key = 'rapidUser';

    // Send two requests immediately.
    expect(limiter.tryRequest(key)).toBe(true);
    expect(limiter.tryRequest(key)).toBe(true);

    // Next request should be blocked.
    expect(limiter.tryRequest(key)).toBe(false);

    // After 250ms, still should be blocked.
    jest.advanceTimersByTime(250);
    expect(limiter.tryRequest(key)).toBe(false);

    // After the remaining 250ms, rate limiter should have reset.
    jest.advanceTimersByTime(250);
    expect(limiter.tryRequest(key)).toBe(true);
    expect(limiter.tryRequest(key)).toBe(true);
    expect(limiter.tryRequest(key)).toBe(false);
  });

  test('should throw an error for invalid configurations', () => {
    // Negative limit
    expect(() => new RateLimiter({ limit: -1, interval: 1000 })).toThrow();
    // Zero interval
    expect(() => new RateLimiter({ limit: 5, interval: 0 })).toThrow();
  });

  test('should operate correctly under prolonged usage and multiple intervals', () => {
    const limiter = new RateLimiter({ limit: 4, interval: 1000 });
    const key = 'longTermUser';

    // Simulate usage over multiple intervals.
    for (let i = 0; i < 3; i++) {
      // Use all available requests in the current interval.
      expect(limiter.tryRequest(key)).toBe(true);
      expect(limiter.tryRequest(key)).toBe(true);
      expect(limiter.tryRequest(key)).toBe(true);
      expect(limiter.tryRequest(key)).toBe(true);
      expect(limiter.tryRequest(key)).toBe(false);

      // Advance time to reset.
      jest.advanceTimersByTime(1000);
    }
  });
});