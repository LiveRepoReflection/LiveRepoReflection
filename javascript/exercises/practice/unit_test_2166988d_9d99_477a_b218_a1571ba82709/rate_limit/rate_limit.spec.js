const RateLimiter = require('./rate_limit');

class FakeRedis {
  constructor() {
    this.store = new Map();
  }

  // Simulate the Redis EVAL command for a sliding window rate limiter.
  // Expected args:
  // ARGV[0]: current timestamp in ms (as string)
  // ARGV[1]: window size in ms (as string)
  // ARGV[2]: limit (as string)
  async eval(script, keys, args) {
    const key = keys[0];
    const current = parseInt(args[0], 10);
    const windowSize = parseInt(args[1], 10);
    const limit = parseInt(args[2], 10);

    // Initialize sorted set if it doesn't exist
    if (!this.store.has(key)) {
      this.store.set(key, []);
    }
    let timestamps = this.store.get(key);
    // Remove expired timestamps (simulate ZREMRANGEBYSCORE key, "-inf", current-window)
    timestamps = timestamps.filter(ts => ts > current - windowSize);
    // Count the remaining requests (simulate ZCARD)
    const count = timestamps.length;

    if (count < limit) {
      // Add the current timestamp (simulate ZADD)
      timestamps.push(current);
      // Sort timestamps so that further removals work correctly
      timestamps.sort((a, b) => a - b);
      this.store.set(key, timestamps);
      // Simulate EXPIRE by ignoring since cleanup is done on every call.
      return 1;
    } else {
      return 0;
    }
  }
}

// A variant of FakeRedis that simulates a failure on eval.
class FailingFakeRedis {
  async eval(script, keys, args) {
    throw new Error('Redis error');
  }
}

describe('RateLimiter', () => {
  let redisClient;
  let rateLimiter;

  const userId = 'user123';

  beforeEach(() => {
    redisClient = new FakeRedis();
    // Create a RateLimiter with a limit of 3 requests per 1000 ms.
    rateLimiter = new RateLimiter({
      limit: 3,
      window: 1000,
      redisClient
    });
  });

  test('allows requests under the limit', async () => {
    // First three requests should be allowed.
    const result1 = await rateLimiter.isAllowed(userId);
    expect(result1).toBe(true);

    const result2 = await rateLimiter.isAllowed(userId);
    expect(result2).toBe(true);

    const result3 = await rateLimiter.isAllowed(userId);
    expect(result3).toBe(true);
  });

  test('blocks requests over the limit', async () => {
    // Use a fixed timestamp to simulate requests in the same window.
    const now = Date.now();
    // Monkey-patch Date.now to control the timing within this test.
    const realDateNow = Date.now;
    Date.now = () => now;

    // First three requests allowed.
    expect(await rateLimiter.isAllowed(userId)).toBe(true);
    expect(await rateLimiter.isAllowed(userId)).toBe(true);
    expect(await rateLimiter.isAllowed(userId)).toBe(true);
    // Fourth request should be blocked.
    expect(await rateLimiter.isAllowed(userId)).toBe(false);

    // Restore Date.now.
    Date.now = realDateNow;
  });

  test('allows new requests after the window expires', async () => {
    // Use a separate window value for precise control.
    const customLimit = 2;
    const customWindow = 200; // 200ms window
    rateLimiter = new RateLimiter({
      limit: customLimit,
      window: customWindow,
      redisClient
    });

    // First two requests allowed.
    expect(await rateLimiter.isAllowed(userId)).toBe(true);
    expect(await rateLimiter.isAllowed(userId)).toBe(true);
    // Third request blocked.
    expect(await rateLimiter.isAllowed(userId)).toBe(false);

    // Wait for window to expire.
    await new Promise(resolve => setTimeout(resolve, customWindow + 50));

    // New request should now be allowed.
    expect(await rateLimiter.isAllowed(userId)).toBe(true);
  });

  test('handles concurrent requests correctly', async () => {
    // Set a limit of 3 requests per window.
    rateLimiter = new RateLimiter({
      limit: 3,
      window: 1000,
      redisClient
    });
    // Fire off 5 concurrent requests.
    const promises = [];
    for (let i = 0; i < 5; i++) {
      promises.push(rateLimiter.isAllowed(userId));
    }
    const results = await Promise.all(promises);
    // Count how many requests were allowed.
    const allowedCount = results.filter(r => r === true).length;
    expect(allowedCount).toBe(3);
  });

  test('gracefully handles redis errors', async () => {
    // Use the failing redis client to simulate an error.
    const failingRedis = new FailingFakeRedis();
    rateLimiter = new RateLimiter({
      limit: 3,
      window: 1000,
      redisClient: failingRedis
    });
    await expect(rateLimiter.isAllowed(userId)).rejects.toThrow('Redis error');
  });
});