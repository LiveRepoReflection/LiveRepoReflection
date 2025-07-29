const { RateLimiter } = require('../rate_limiter');

describe('Distributed Rate Limiter', () => {
  beforeEach(() => {
    // Reset the rate limiter state.
    // Assume RateLimiter has a static reset method for testing purposes.
    if (typeof RateLimiter.reset === 'function') {
      RateLimiter.reset();
    }
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  test('should allow requests under the limit and block when exceeding the limit', () => {
    const clientId = 'client1';
    const action = 'download';
    const limit = 3;
    const timeWindow = 1000; // milliseconds

    const rateLimiter = new RateLimiter();

    // First three requests should be allowed.
    expect(rateLimiter.isAllowed(clientId, action, limit, timeWindow)).toBe(true);
    expect(rateLimiter.isAllowed(clientId, action, limit, timeWindow)).toBe(true);
    expect(rateLimiter.isAllowed(clientId, action, limit, timeWindow)).toBe(true);
    // Fourth request should be blocked.
    expect(rateLimiter.isAllowed(clientId, action, limit, timeWindow)).toBe(false);
  });

  test('should reset count after time window expires', () => {
    const clientId = 'client2';
    const action = 'create_post';
    const limit = 2;
    const timeWindow = 2000; // milliseconds

    const rateLimiter = new RateLimiter();

    // Use up the limit.
    expect(rateLimiter.isAllowed(clientId, action, limit, timeWindow)).toBe(true);
    expect(rateLimiter.isAllowed(clientId, action, limit, timeWindow)).toBe(true);
    expect(rateLimiter.isAllowed(clientId, action, limit, timeWindow)).toBe(false);

    // Fast-forward time beyond the time window.
    jest.advanceTimersByTime(timeWindow + 100);
    // After time expiry, should allow again.
    expect(rateLimiter.isAllowed(clientId, action, limit, timeWindow)).toBe(true);
  });

  test('should maintain separate counts for different clients', () => {
    const action = 'download';
    const limit = 2;
    const timeWindow = 3000; // milliseconds

    const rateLimiter = new RateLimiter();

    // For client A.
    expect(rateLimiter.isAllowed('clientA', action, limit, timeWindow)).toBe(true);
    expect(rateLimiter.isAllowed('clientA', action, limit, timeWindow)).toBe(true);
    expect(rateLimiter.isAllowed('clientA', action, limit, timeWindow)).toBe(false);

    // For client B, should be independent.
    expect(rateLimiter.isAllowed('clientB', action, limit, timeWindow)).toBe(true);
    expect(rateLimiter.isAllowed('clientB', action, limit, timeWindow)).toBe(true);
    expect(rateLimiter.isAllowed('clientB', action, limit, timeWindow)).toBe(false);
  });

  test('should maintain separate counts for different actions for the same client', () => {
    const clientId = 'client3';
    const limit = 2;
    const timeWindow = 4000; // milliseconds

    const rateLimiter = new RateLimiter();

    // Action download.
    expect(rateLimiter.isAllowed(clientId, 'download', limit, timeWindow)).toBe(true);
    expect(rateLimiter.isAllowed(clientId, 'download', limit, timeWindow)).toBe(true);
    expect(rateLimiter.isAllowed(clientId, 'download', limit, timeWindow)).toBe(false);

    // Action upload should start fresh.
    expect(rateLimiter.isAllowed(clientId, 'upload', limit, timeWindow)).toBe(true);
    expect(rateLimiter.isAllowed(clientId, 'upload', limit, timeWindow)).toBe(true);
    expect(rateLimiter.isAllowed(clientId, 'upload', limit, timeWindow)).toBe(false);
  });

  test('should handle invalid input parameters gracefully', () => {
    const rateLimiter = new RateLimiter();
    const validLimit = 3;
    const validTimeWindow = 1000;

    // Invalid clientId.
    expect(() => {
      rateLimiter.isAllowed(null, 'action', validLimit, validTimeWindow);
    }).toThrow();

    // Invalid action.
    expect(() => {
      rateLimiter.isAllowed('client_invalid', undefined, validLimit, validTimeWindow);
    }).toThrow();

    // Invalid limit.
    expect(() => {
      rateLimiter.isAllowed('client_invalid', 'action', -1, validTimeWindow);
    }).toThrow();

    // Invalid timeWindow.
    expect(() => {
      rateLimiter.isAllowed('client_invalid', 'action', validLimit, 0);
    }).toThrow();
  });

  test('should reflect distributed behavior across multiple RateLimiter instances', () => {
    const clientId = 'client_multi';
    const action = 'sync_action';
    const limit = 5;
    const timeWindow = 5000; // milliseconds

    // Assume multiple instances share the same external state.
    const rateLimiter1 = new RateLimiter();
    const rateLimiter2 = new RateLimiter();

    // Use first instance to make three requests.
    expect(rateLimiter1.isAllowed(clientId, action, limit, timeWindow)).toBe(true);
    expect(rateLimiter1.isAllowed(clientId, action, limit, timeWindow)).toBe(true);
    expect(rateLimiter1.isAllowed(clientId, action, limit, timeWindow)).toBe(true);

    // Use second instance to make two requests.
    expect(rateLimiter2.isAllowed(clientId, action, limit, timeWindow)).toBe(true);
    expect(rateLimiter2.isAllowed(clientId, action, limit, timeWindow)).toBe(true);

    // Further requests using either instance should be blocked.
    expect(rateLimiter1.isAllowed(clientId, action, limit, timeWindow)).toBe(false);
    expect(rateLimiter2.isAllowed(clientId, action, limit, timeWindow)).toBe(false);
  });

  test('should allow a small burst over the limit if using a leaky bucket or token bucket approach (if applicable)', () => {
    const clientId = 'client_burst';
    const action = 'burst_test';
    const limit = 4;
    const timeWindow = 3000; // milliseconds

    const rateLimiter = new RateLimiter();

    // Simulate a burst where tokens might accumulate.
    // Since implementation details may vary, we test that initial calls are allowed.
    const results = [];
    for (let i = 0; i < 6; i++) {
      results.push(rateLimiter.isAllowed(clientId, action, limit, timeWindow));
    }
    // At least the first 4 calls must be allowed.
    expect(results.slice(0, 4).every(val => val === true)).toBe(true);
    // Depending on the algorithm, subsequent calls should be false.
    expect(results.slice(4).every(val => val === false)).toBe(true);
  });
});