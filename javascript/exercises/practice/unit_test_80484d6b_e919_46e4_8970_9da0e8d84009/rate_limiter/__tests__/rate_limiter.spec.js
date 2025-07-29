const { RateLimiter } = require('../rate_limiter');

describe("RateLimiter", () => {
  beforeEach(() => {
    // For tests, we assume the RateLimiter constructor accepts an options object with:
    // - limit: maximum number of requests allowed in the specified window.
    // - windowMs: time window in milliseconds.
    // - algorithm (optional): 'fixed_window' (default) or 'token_bucket'
    // For simplicity, our tests will use a limit of 3 requests per 1000ms.
    // The tests below depend on a clean state for each test case.
    // Note: The actual RateLimiter implementation is not provided here.
  });

  describe("Fixed Window Algorithm", () => {
    let limiter;
    beforeEach(() => {
      limiter = new RateLimiter({ limit: 3, windowMs: 1000, algorithm: 'fixed_window' });
      jest.useFakeTimers();
    });

    afterEach(() => {
      jest.useRealTimers();
    });

    test("allows requests under the limit", () => {
      const userId = "user1";
      expect(limiter.isAllowed(userId)).toBe(true);
      expect(limiter.isAllowed(userId)).toBe(true);
      expect(limiter.isAllowed(userId)).toBe(true);
    });

    test("blocks requests when limit is exceeded", () => {
      const userId = "user1";
      limiter.isAllowed(userId); // 1st request
      limiter.isAllowed(userId); // 2nd request
      limiter.isAllowed(userId); // 3rd request
      expect(limiter.isAllowed(userId)).toBe(false); // 4th request should be blocked
    });

    test("resets the counter after the window elapses", () => {
      const userId = "user1";
      limiter.isAllowed(userId); // 1st
      limiter.isAllowed(userId); // 2nd
      limiter.isAllowed(userId); // 3rd
      expect(limiter.isAllowed(userId)).toBe(false);
      // Advance the time past the window period
      jest.advanceTimersByTime(1000);
      expect(limiter.isAllowed(userId)).toBe(true);
      expect(limiter.isAllowed(userId)).toBe(true);
    });

    test("handles multiple users independently", () => {
      const user1 = "user1";
      const user2 = "user2";
      // User1 makes two requests
      expect(limiter.isAllowed(user1)).toBe(true);
      expect(limiter.isAllowed(user1)).toBe(true);
      // User2 makes three requests
      expect(limiter.isAllowed(user2)).toBe(true);
      expect(limiter.isAllowed(user2)).toBe(true);
      expect(limiter.isAllowed(user2)).toBe(true);
      // Further request for user2 should be blocked while user1 still has room
      expect(limiter.isAllowed(user2)).toBe(false);
      // User1 should still be allowed one more request
      expect(limiter.isAllowed(user1)).toBe(true);
      expect(limiter.isAllowed(user1)).toBe(false);
    });
  });

  describe("Token Bucket Algorithm", () => {
    let tokenLimiter;
    beforeEach(() => {
      tokenLimiter = new RateLimiter({ limit: 3, windowMs: 1000, algorithm: 'token_bucket' });
      jest.useFakeTimers();
    });

    afterEach(() => {
      jest.useRealTimers();
    });

    test("allows initial burst up to the limit", () => {
      const userId = "user1";
      expect(tokenLimiter.isAllowed(userId)).toBe(true);
      expect(tokenLimiter.isAllowed(userId)).toBe(true);
      expect(tokenLimiter.isAllowed(userId)).toBe(true);
      expect(tokenLimiter.isAllowed(userId)).toBe(false);
    });

    test("replenishes tokens gradually over time", () => {
      const userId = "user1";
      // Exhaust tokens
      tokenLimiter.isAllowed(userId);
      tokenLimiter.isAllowed(userId);
      tokenLimiter.isAllowed(userId);
      expect(tokenLimiter.isAllowed(userId)).toBe(false);
      // Advance half the window time, expecting partial token replenishment.
      jest.advanceTimersByTime(500);
      // Depending on the token bucket's refill implementation (continuous refill),
      // approximately 50% of the tokens should be replenished.
      // For our test, we assume that after 500ms one token becomes available.
      expect(tokenLimiter.isAllowed(userId)).toBe(true);
      // Subsequent call should be blocked if only one token was refilled.
      expect(tokenLimiter.isAllowed(userId)).toBe(false);
      // Advance another 500ms to complete the window.
      jest.advanceTimersByTime(500);
      // Now, up to 2 tokens may have been refilled.
      expect(tokenLimiter.isAllowed(userId)).toBe(true);
      expect(tokenLimiter.isAllowed(userId)).toBe(true);
      expect(tokenLimiter.isAllowed(userId)).toBe(false);
    });

    test("handles multiple users with token bucket correctly", () => {
      const userA = "userA";
      const userB = "userB";
      // UserA uses all tokens
      expect(tokenLimiter.isAllowed(userA)).toBe(true);
      expect(tokenLimiter.isAllowed(userA)).toBe(true);
      expect(tokenLimiter.isAllowed(userA)).toBe(true);
      expect(tokenLimiter.isAllowed(userA)).toBe(false);
      // UserB should be unaffected
      expect(tokenLimiter.isAllowed(userB)).toBe(true);
      expect(tokenLimiter.isAllowed(userB)).toBe(true);
      expect(tokenLimiter.isAllowed(userB)).toBe(true);
      expect(tokenLimiter.isAllowed(userB)).toBe(false);
      // Advance time and verify that tokens are replenished independently
      jest.advanceTimersByTime(1000);
      expect(tokenLimiter.isAllowed(userA)).toBe(true);
      expect(tokenLimiter.isAllowed(userB)).toBe(true);
    });
  });
});