const DistributedRateLimiter = require('../distributed_limiter');

describe('DistributedRateLimiter', () => {
  let rateLimiter;

  beforeEach(() => {
    rateLimiter = new DistributedRateLimiter();
  });

  test('allows requests under the configured limit', () => {
    rateLimiter.configureRateLimit('user1', { limit: 3, windowMs: 1000 });
    expect(rateLimiter.isAllowed('user1')).toBe(true);
    expect(rateLimiter.isAllowed('user1')).toBe(true);
    expect(rateLimiter.isAllowed('user1')).toBe(true);
  });

  test('blocks requests over the configured limit', () => {
    rateLimiter.configureRateLimit('user2', { limit: 2, windowMs: 1000 });
    expect(rateLimiter.isAllowed('user2')).toBe(true);
    expect(rateLimiter.isAllowed('user2')).toBe(true);
    expect(rateLimiter.isAllowed('user2')).toBe(false);
  });

  test('resets the rate limit after the time window expires', (done) => {
    rateLimiter.configureRateLimit('user3', { limit: 1, windowMs: 500 });
    expect(rateLimiter.isAllowed('user3')).toBe(true);
    expect(rateLimiter.isAllowed('user3')).toBe(false);
    setTimeout(() => {
      // After the window expires, the rate limiter should allow a new request
      expect(rateLimiter.isAllowed('user3')).toBe(true);
      done();
    }, 600);
  });

  test('handles multiple clients independently', () => {
    rateLimiter.configureRateLimit('clientA', { limit: 2, windowMs: 1000 });
    rateLimiter.configureRateLimit('clientB', { limit: 3, windowMs: 1000 });
    expect(rateLimiter.isAllowed('clientA')).toBe(true);
    expect(rateLimiter.isAllowed('clientB')).toBe(true);
    expect(rateLimiter.isAllowed('clientA')).toBe(true);
    expect(rateLimiter.isAllowed('clientA')).toBe(false);
    expect(rateLimiter.isAllowed('clientB')).toBe(true);
    expect(rateLimiter.isAllowed('clientB')).toBe(true);
    expect(rateLimiter.isAllowed('clientB')).toBe(false);
  });

  test('evicts inactive clients from the datastore', (done) => {
    // Here we assume that the implementation supports an eviction mechanism.
    // For testing purposes, we simulate a configuration that includes an evictionTime parameter.
    rateLimiter.configureRateLimit('user4', { limit: 1, windowMs: 500, evictionTime: 200 });
    expect(rateLimiter.isAllowed('user4')).toBe(true);
    // Wait long enough to trigger eviction beyond the windowMs and evictionTime.
    setTimeout(() => {
      // After eviction, the internal record for user4 should be removed, and a new request should be allowed.
      expect(rateLimiter.isAllowed('user4')).toBe(true);
      done();
    }, 800);
  });

  test('performs under high throughput conditions', () => {
    rateLimiter.configureRateLimit('user5', { limit: 1000, windowMs: 1000 });
    let allowedCount = 0;
    for (let i = 0; i < 1500; i++) {
      if (rateLimiter.isAllowed('user5')) allowedCount++;
    }
    expect(allowedCount).toBe(1000);
  });

  test('ensures atomicity under concurrent requests simulation', (done) => {
    rateLimiter.configureRateLimit('user6', { limit: 10, windowMs: 1000 });
    const requestPromises = [];
    const results = [];

    for (let i = 0; i < 20; i++) {
      requestPromises.push(
        new Promise(resolve => {
          // Simulate small random delays for concurrent requests.
          setTimeout(() => {
            const allowed = rateLimiter.isAllowed('user6');
            results.push(allowed);
            resolve();
          }, Math.floor(Math.random() * 10));
        })
      );
    }

    Promise.all(requestPromises).then(() => {
      const allowedRequests = results.filter(r => r === true).length;
      // Only 10 requests should be allowed within the window.
      expect(allowedRequests).toBe(10);
      done();
    });
  });
});