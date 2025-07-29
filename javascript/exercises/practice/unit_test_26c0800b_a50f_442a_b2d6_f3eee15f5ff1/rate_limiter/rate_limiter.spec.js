const RateLimiter = require('./rate_limiter');

describe('RateLimiter', () => {
  let limiter;
  const userId = 'user1';
  const now = Date.now();

  beforeEach(() => {
    // Instantiate a new RateLimiter with a configuration of 3 requests per 1000ms window.
    limiter = new RateLimiter({ maxRequests: 3, windowMs: 1000 });
  });

  test('allows requests under the rate limit', () => {
    let result = limiter.check(userId, now);
    expect(result.allowRequest).toBe(true);
    expect(result.retryAfter).toBe(0);

    result = limiter.check(userId, now + 100);
    expect(result.allowRequest).toBe(true);
    expect(result.retryAfter).toBe(0);

    result = limiter.check(userId, now + 200);
    expect(result.allowRequest).toBe(true);
    expect(result.retryAfter).toBe(0);
  });

  test('rejects request when rate limit is exceeded', () => {
    // Consume the available quota.
    limiter.check(userId, now);
    limiter.check(userId, now + 10);
    limiter.check(userId, now + 20);

    // Fourth request within the same window should be rejected.
    const result = limiter.check(userId, now + 30);
    expect(result.allowRequest).toBe(false);
    expect(result.retryAfter).toBeGreaterThan(0);
  });

  test('resets the rate limiter after the window expires', () => {
    // Fill up the quota.
    limiter.check(userId, now);
    limiter.check(userId, now + 10);
    limiter.check(userId, now + 20);

    // Request within the same window is rejected.
    let resultBlocked = limiter.check(userId, now + 30);
    expect(resultBlocked.allowRequest).toBe(false);

    // After the window has expired, the request is allowed.
    const resultAfterReset = limiter.check(userId, now + 1000);
    expect(resultAfterReset.allowRequest).toBe(true);
    expect(resultAfterReset.retryAfter).toBe(0);
  });

  test('maintains separate buckets for different users', () => {
    // First requests for two different users.
    const resultUser1 = limiter.check('user1', now);
    const resultUser2 = limiter.check('user2', now);
    expect(resultUser1.allowRequest).toBe(true);
    expect(resultUser2.allowRequest).toBe(true);

    // Consume the quota for user1.
    limiter.check('user1', now + 10);
    limiter.check('user1', now + 20);
    // Fourth request for user1 should be rejected.
    const resultUser1Blocked = limiter.check('user1', now + 30);
    expect(resultUser1Blocked.allowRequest).toBe(false);
    // User2 should still be within limit.
    const resultUser2Again = limiter.check('user2', now + 30);
    expect(resultUser2Again.allowRequest).toBe(true);
  });

  test('handles concurrent requests correctly', async () => {
    const baseTime = now;
    // Simulate 5 concurrent requests from the same user.
    const promises = [];
    for (let i = 0; i < 5; i++) {
      promises.push(Promise.resolve(limiter.check(userId, baseTime + i * 5)));
    }
    const results = await Promise.all(promises);

    // Only the first 3 requests should be allowed.
    const allowedCount = results.filter(r => r.allowRequest).length;
    const rejectedCount = results.filter(r => !r.allowRequest).length;
    expect(allowedCount).toBe(3);
    expect(rejectedCount).toBe(2);
  });

  test('calculates retryAfter correctly for rate limited requests', () => {
    // Capture the starting time.
    const startTime = now;
    // Deplete the available quota.
    limiter.check(userId, startTime);
    limiter.check(userId, startTime + 50);
    limiter.check(userId, startTime + 100);
    
    // Next request should be rejected and return a positive retryAfter value.
    const blockedResult = limiter.check(userId, startTime + 150);
    expect(blockedResult.allowRequest).toBe(false);
    expect(typeof blockedResult.retryAfter).toBe('number');
    expect(blockedResult.retryAfter).toBeGreaterThan(0);

    // The retryAfter should not exceed the window length.
    expect(blockedResult.retryAfter).toBeLessThanOrEqual(1);
  });
});