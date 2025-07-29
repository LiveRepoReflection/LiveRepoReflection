const { rateLimit, configure } = require('../rate_limit');

beforeEach(() => {
  // Set a short window for testing
  if (typeof configure === 'function') {
    configure({
      timeWindow: 1000,       // 1 second window
      capacity: 100,          // maximum allowed cost per window
      replenishRate: 0.1,     // replenishes 0.1 units per ms => 100 units per second
      redisHost: 'localhost',
      redisPort: 6379
    });
  }
});

describe('Basic Functionality', () => {
  test('allows requests within capacity', async () => {
    const userId = 'user1';
    // Issue 10 requests of cost 10 each; sufficient to exactly match capacity (100)
    for (let i = 0; i < 10; i++) {
      const allowed = await rateLimit(userId, 10);
      expect(allowed).toBe(true);
    }
  });

  test('blocks a request that exceeds capacity', async () => {
    const userId = 'user2';
    // Use almost full allowance
    for (let i = 0; i < 9; i++) {
      const allowed = await rateLimit(userId, 10);
      expect(allowed).toBe(true);
    }
    // At this point, 90 units have been consumed.
    // A request costing 15 should exceed the capacity of 100.
    const allowed = await rateLimit(userId, 15);
    expect(allowed).toBe(false);
  });
});

describe('Replenishment Behavior', () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });
  afterEach(() => {
    jest.useRealTimers();
  });

  test('replenishes allowance after timeWindow', async () => {
    const userId = 'user3';
    // Use full allowance with one request
    const firstCall = await rateLimit(userId, 100);
    expect(firstCall).toBe(true);
    // Next call, no allowance should be available
    const secondCall = await rateLimit(userId, 10);
    expect(secondCall).toBe(false);

    // Advance time by 500 ms, partially refilling allowance (should refill 50 units).
    jest.advanceTimersByTime(500);
    // A request costing 50 should now be allowed.
    const thirdCall = await rateLimit(userId, 50);
    expect(thirdCall).toBe(true);

    // Immediately following a high cost request, a small additional request might be blocked.
    const fourthCall = await rateLimit(userId, 1);
    expect(fourthCall).toBe(false);

    // Advance time to fully replenish and ensure request is allowed.
    jest.advanceTimersByTime(500);
    const fifthCall = await rateLimit(userId, 10);
    expect(fifthCall).toBe(true);
  });
});

describe('Edge Cases and Input Validation', () => {
  test('throws error for null userId', async () => {
    await expect(rateLimit(null, 10)).rejects.toThrow();
  });

  test('throws error for undefined userId', async () => {
    await expect(rateLimit(undefined, 10)).rejects.toThrow();
  });

  test('throws error for empty userId', async () => {
    await expect(rateLimit('', 10)).rejects.toThrow();
  });

  test('throws error for non-positive requestCost (zero)', async () => {
    await expect(rateLimit('user4', 0)).rejects.toThrow();
  });

  test('throws error for non-positive requestCost (negative)', async () => {
    await expect(rateLimit('user4', -5)).rejects.toThrow();
  });
});

describe('Concurrent Requests', () => {
  test('handles concurrent requests correctly', async () => {
    const userId = 'user_concurrent';
    // Prepare an array of promises simulating concurrent requests.
    // Each request costs 10 units. The maximum allowed cost is 100.
    const requests = [];
    for (let i = 0; i < 15; i++) {
      requests.push(rateLimit(userId, 10));
    }
    const results = await Promise.all(requests);
    // Only 10 of these requests should be allowed; the rest should be blocked.
    const allowedCount = results.filter(result => result === true).length;
    expect(allowedCount).toBe(10);
  });
});

describe('Graceful Handling of Redis Errors', () => {
  test('handles redis errors gracefully by using fallback mechanism', async () => {
    const userId = 'user_error';
    // If the module provides a way to simulate redis error, use it. This test assumes that when a redis error occurs,
    // the fallback is to allow the request.
    if (typeof rateLimit.simulateRedisError === 'function') {
      // Trigger redis error simulation.
      rateLimit.simulateRedisError(true);
      const result = await rateLimit(userId, 10);
      expect(result).toBe(true);
      // Reset the error simulation.
      rateLimit.simulateRedisError(false);
    } else {
      // If simulateRedisError is not available, simply ensure that the function does not throw an unhandled error.
      await expect(rateLimit(userId, 10)).resolves.toBeDefined();
    }
  });
});