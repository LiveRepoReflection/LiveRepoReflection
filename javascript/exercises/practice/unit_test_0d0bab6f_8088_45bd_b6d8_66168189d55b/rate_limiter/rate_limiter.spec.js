const { allowRequest, resetRateLimiter, configureRateLimiter } = require('./rate_limiter');

describe('Rate Limiter Unit Tests', () => {
  // Before each test, we reset the rate limiter state.
  beforeEach(() => {
    // Reset the internal state (this function must be implemented in the solution)
    resetRateLimiter();
    // Configure with a known state: bucket capacity 3, refill rate = 1 token per 1000ms.
    configureRateLimiter({
      bucketCapacity: 3,
      refillInterval: 1000, // milliseconds per token refill
      // other configuration parameters, if any, can go here
    });
  });

  test('should allow requests until capacity is exhausted', () => {
    const userId = 'user1';
    const endpoint = '/api/test';

    // First three requests should be allowed.
    expect(allowRequest(userId, endpoint)).toBe(true);
    expect(allowRequest(userId, endpoint)).toBe(true);
    expect(allowRequest(userId, endpoint)).toBe(true);
    // Fourth request should be rejected.
    expect(allowRequest(userId, endpoint)).toBe(false);
  });

  test('should maintain separate buckets per endpoint for the same user', () => {
    const userId = 'user2';
    const endpointA = '/api/testA';
    const endpointB = '/api/testB';

    // Exhaust endpointA
    expect(allowRequest(userId, endpointA)).toBe(true);
    expect(allowRequest(userId, endpointA)).toBe(true);
    expect(allowRequest(userId, endpointA)).toBe(true);
    expect(allowRequest(userId, endpointA)).toBe(false);

    // EndpointB should have its own bucket and be full.
    expect(allowRequest(userId, endpointB)).toBe(true);
    expect(allowRequest(userId, endpointB)).toBe(true);
    expect(allowRequest(userId, endpointB)).toBe(true);
    expect(allowRequest(userId, endpointB)).toBe(false);
  });

  test('should maintain separate buckets per user for the same endpoint', () => {
    const endpoint = '/api/common';
    const userA = 'userA';
    const userB = 'userB';

    // Exhaust userA's bucket.
    expect(allowRequest(userA, endpoint)).toBe(true);
    expect(allowRequest(userA, endpoint)).toBe(true);
    expect(allowRequest(userA, endpoint)).toBe(true);
    expect(allowRequest(userA, endpoint)).toBe(false);

    // UserB should have a separate bucket.
    expect(allowRequest(userB, endpoint)).toBe(true);
    expect(allowRequest(userB, endpoint)).toBe(true);
    expect(allowRequest(userB, endpoint)).toBe(true);
    expect(allowRequest(userB, endpoint)).toBe(false);
  });

  test('should refill tokens after the refill interval', () => {
    jest.useFakeTimers();

    const userId = 'user3';
    const endpoint = '/api/refill';

    // Use all tokens.
    expect(allowRequest(userId, endpoint)).toBe(true);
    expect(allowRequest(userId, endpoint)).toBe(true);
    expect(allowRequest(userId, endpoint)).toBe(true);
    expect(allowRequest(userId, endpoint)).toBe(false);

    // Advance time by 1000ms to refill one token.
    jest.advanceTimersByTime(1000);
    // Allow one request after refill.
    expect(allowRequest(userId, endpoint)).toBe(true);
    // Immediately after, token should be exhausted again.
    expect(allowRequest(userId, endpoint)).toBe(false);

    // Advance time by 3000ms to refill all tokens.
    jest.advanceTimersByTime(3000);
    // Should be allowed full capacity.
    expect(allowRequest(userId, endpoint)).toBe(true);
    expect(allowRequest(userId, endpoint)).toBe(true);
    expect(allowRequest(userId, endpoint)).toBe(true);
    expect(allowRequest(userId, endpoint)).toBe(false);

    jest.useRealTimers();
  });

  test('should handle invalid inputs gracefully', () => {
    // Invalid user IDs and endpoints.
    expect(() => allowRequest('', '/api/test')).toThrow();
    expect(() => allowRequest(null, '/api/test')).toThrow();
    expect(() => allowRequest('user_invalid', '')).toThrow();
    expect(() => allowRequest('user_invalid', null)).toThrow();
  });

  test('should handle concurrent requests correctly', async () => {
    const userId = 'userConcurrent';
    const endpoint = '/api/concurrent';
    const requestCount = 10; // More than capacity
    const results = [];

    // Create concurrent requests.
    await Promise.all(
      Array.from({ length: requestCount }).map(async () => {
        results.push(allowRequest(userId, endpoint));
      })
    );

    // There should be exactly capacity number of true responses.
    const allowedCount = results.filter(v => v === true).length;
    expect(allowedCount).toBe(3);
  });
});