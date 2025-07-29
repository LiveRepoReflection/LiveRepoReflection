const { describe, test, expect, beforeEach } = require('@jest/globals');
const { DistributedRateLimiter } = require('./distributed_limiter');

describe('DistributedRateLimiter', () => {
  let rateLimiter;

  beforeEach(() => {
    // Mock the getRateLimit function to return different limits based on the userId and apiEndpoint.
    global.getRateLimit = jest.fn().mockImplementation((userId, apiEndpoint) => {
      if (apiEndpoint === '/users') {
        if (userId === 'userA') return { limit: 5, window: 1000 }; // 5 requests per second
        if (userId === 'userB') return { limit: 2, window: 1000 }; // 2 requests per second
      }
      // Default rate limit for other endpoints
      return { limit: 3, window: 1000 }; // 3 requests per second
    });
    rateLimiter = new DistributedRateLimiter();
  });

  test('allows a request when below the rate limit', async () => {
    const userId = 'userA';
    const apiEndpoint = '/users';
    const timestamp = Date.now();
    const allowed = await rateLimiter.isAllowed(userId, apiEndpoint, timestamp);
    expect(allowed).toBe(true);
  });

  test('blocks a request when the rate limit is exceeded for userB', async () => {
    const userId = 'userB';
    const apiEndpoint = '/users';
    const timestamp = Date.now();

    // For userB, the limit is 2 per second.
    const allowed1 = await rateLimiter.isAllowed(userId, apiEndpoint, timestamp);
    const allowed2 = await rateLimiter.isAllowed(userId, apiEndpoint, timestamp);
    const allowed3 = await rateLimiter.isAllowed(userId, apiEndpoint, timestamp);

    expect(allowed1).toBe(true);
    expect(allowed2).toBe(true);
    expect(allowed3).toBe(false);
  });

  test('resets the request count after the time window expires', async () => {
    const userId = 'userA';
    const apiEndpoint = '/users';
    const baseTimestamp = Date.now();

    // Exhaust the limit for userA on /users (limit is 5 per second).
    const results = [];
    for (let i = 0; i < 5; i++) {
      results.push(await rateLimiter.isAllowed(userId, apiEndpoint, baseTimestamp));
    }
    expect(results).toEqual([true, true, true, true, true]);

    // This request should be blocked within the same window.
    const blockedRequest = await rateLimiter.isAllowed(userId, apiEndpoint, baseTimestamp);
    expect(blockedRequest).toBe(false);

    // After the time window has passed, a new request should be allowed.
    const newTimestamp = baseTimestamp + 1001;
    const allowedAfterWindow = await rateLimiter.isAllowed(userId, apiEndpoint, newTimestamp);
    expect(allowedAfterWindow).toBe(true);
  });

  test('maintains independent rate limits for separate endpoints', async () => {
    const userId = 'userA';
    const endpointUsers = '/users';      // limit of 5 per second for userA
    const endpointProducts = '/products'; // default limit of 3 per second
    const timestamp = Date.now();

    // Exhaust rate limit for /users endpoint.
    for (let i = 0; i < 5; i++) {
      const allowed = await rateLimiter.isAllowed(userId, endpointUsers, timestamp);
      expect(allowed).toBe(true);
    }
    const blockedUsers = await rateLimiter.isAllowed(userId, endpointUsers, timestamp);
    expect(blockedUsers).toBe(false);

    // Exhaust rate limit for /products endpoint.
    for (let i = 0; i < 3; i++) {
      const allowed = await rateLimiter.isAllowed(userId, endpointProducts, timestamp);
      expect(allowed).toBe(true);
    }
    const blockedProducts = await rateLimiter.isAllowed(userId, endpointProducts, timestamp);
    expect(blockedProducts).toBe(false);
  });

  test('handles independent rate limits for multiple users', async () => {
    const apiEndpoint = '/users';
    const timestamp = Date.now();
    const userA = 'userA'; // limit: 5 per second
    const userB = 'userB'; // limit: 2 per second

    // Send requests for userA.
    for (let i = 0; i < 5; i++) {
      const allowed = await rateLimiter.isAllowed(userA, apiEndpoint, timestamp);
      expect(allowed).toBe(true);
    }
    const blockedUserA = await rateLimiter.isAllowed(userA, apiEndpoint, timestamp);
    expect(blockedUserA).toBe(false);

    // Send requests for userB.
    for (let i = 0; i < 2; i++) {
      const allowed = await rateLimiter.isAllowed(userB, apiEndpoint, timestamp);
      expect(allowed).toBe(true);
    }
    const blockedUserB = await rateLimiter.isAllowed(userB, apiEndpoint, timestamp);
    expect(blockedUserB).toBe(false);
  });

  test('handles concurrent requests correctly', async () => {
    const userId = 'concurrentUser';
    const apiEndpoint = '/concurrent';
    // For this test, override the getRateLimit to set a limit of 3 per second.
    global.getRateLimit.mockImplementation(() => ({ limit: 3, window: 1000 }));
    const timestamp = Date.now();
    const promises = [];

    // Simulate 10 concurrent requests.
    for (let i = 0; i < 10; i++) {
      promises.push(rateLimiter.isAllowed(userId, apiEndpoint, timestamp));
    }
    const results = await Promise.all(promises);
    const allowedCount = results.filter(result => result === true).length;
    const blockedCount = results.filter(result => result === false).length;

    expect(allowedCount).toBe(3);
    expect(blockedCount).toBe(7);
  });
});