const { isAllowed, configureUserLimit } = require('../rate_limiter');

// In-memory simulation for atomicIncrement and key-value storage
let fakeStore;

beforeEach(() => {
  fakeStore = new Map();

  // Reset and initialize fake time
  let currentTime = 1000;
  global.getTimeInSeconds = jest.fn(() => currentTime);

  // Expose a helper to advance time in tests
  global.advanceTime = (seconds) => {
    currentTime += seconds;
  };

  // Simulated atomicIncrement: key format: "rl:{userId}:{timeWindowStart}"
  // Each key holds an object with { count, expiryTime }
  global.atomicIncrement = (key, expiryInSeconds) => {
    const now = global.getTimeInSeconds();
    if (!fakeStore.has(key)) {
      fakeStore.set(key, { count: 1, expiryTime: now + expiryInSeconds });
      return 1;
    }
    const record = fakeStore.get(key);
    // If key expired, reset the counter
    if (now >= record.expiryTime) {
      const newRecord = { count: 1, expiryTime: now + expiryInSeconds };
      fakeStore.set(key, newRecord);
      return 1;
    } else {
      record.count += 1;
      fakeStore.set(key, record);
      return record.count;
    }
  };

  // Clear any user-specific configuration if stored globally.
  // Assume the rate limiter implementation uses a global config store named "userLimits"
  global.userLimits = new Map();
});

describe('Distributed Rate Limiter', () => {
  test('should allow requests under the configured limit for a user', () => {
    // Configure the user "user1" with limit 3 requests per 60 seconds.
    configureUserLimit('user1', 3, 60);

    // First 3 requests should be allowed.
    expect(isAllowed('user1')).toBe(true);
    expect(isAllowed('user1')).toBe(true);
    expect(isAllowed('user1')).toBe(true);
    // Fourth request should exceed limit and be blocked.
    expect(isAllowed('user1')).toBe(false);
  });

  test('should maintain separate counters for different users', () => {
    // Configure two users with the same limit.
    configureUserLimit('userA', 2, 60);
    configureUserLimit('userB', 2, 60);

    // UserA makes 2 requests.
    expect(isAllowed('userA')).toBe(true);
    expect(isAllowed('userA')).toBe(true);
    // Third request for UserA is blocked.
    expect(isAllowed('userA')).toBe(false);

    // UserB should still have full quota.
    expect(isAllowed('userB')).toBe(true);
    expect(isAllowed('userB')).toBe(true);
    expect(isAllowed('userB')).toBe(false);
  });

  test('should reset the counter after the time window expires', () => {
    // Configure the user "user2" with a limit of 2 requests per 30 seconds.
    configureUserLimit('user2', 2, 30);

    // Use up the limit.
    expect(isAllowed('user2')).toBe(true);
    expect(isAllowed('user2')).toBe(true);
    expect(isAllowed('user2')).toBe(false);

    // Advance time beyond the window.
    global.advanceTime(31);

    // The counter should reset. New request should be allowed.
    expect(isAllowed('user2')).toBe(true);
  });

  test('should correctly handle the edge of expiration and reset the counter', () => {
    // Configure user with limit of 1 per 10 seconds.
    configureUserLimit('edgeUser', 1, 10);

    // First request allowed.
    expect(isAllowed('edgeUser')).toBe(true);
    // Immediate second request is blocked.
    expect(isAllowed('edgeUser')).toBe(false);

    // Advance time exactly to the expiry time.
    global.advanceTime(10);
    // Counter should reset exactly at expiry.
    expect(isAllowed('edgeUser')).toBe(true);
  });

  test('should handle multiple rapid requests within a small time window', () => {
    // Configure with limit of 5 requests per 5 seconds.
    configureUserLimit('rapidUser', 5, 5);

    // Make 5 rapid requests.
    for (let i = 0; i < 5; i++) {
      expect(isAllowed('rapidUser')).toBe(true);
    }
    // 6th rapid request should be blocked.
    expect(isAllowed('rapidUser')).toBe(false);

    // Advance time 6 seconds and counter resets.
    global.advanceTime(6);
    expect(isAllowed('rapidUser')).toBe(true);
  });
});