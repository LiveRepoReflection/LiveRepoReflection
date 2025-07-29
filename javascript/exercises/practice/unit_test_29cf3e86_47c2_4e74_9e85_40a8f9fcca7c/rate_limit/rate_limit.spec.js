const { rateLimit } = require('./rate_limit');

describe('rateLimit Function', () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  test('allows actions under the limit', () => {
    const userId = 'user1';
    const action = 'login';
    const limit = 3;
    const timeWindow = 10; // in seconds

    expect(rateLimit(userId, action, limit, timeWindow)).toBe(true);
    expect(rateLimit(userId, action, limit, timeWindow)).toBe(true);
    expect(rateLimit(userId, action, limit, timeWindow)).toBe(true);
  });

  test('blocks actions after exceeding the limit', () => {
    const userId = 'user2';
    const action = 'comment';
    const limit = 2;
    const timeWindow = 5; // in seconds

    expect(rateLimit(userId, action, limit, timeWindow)).toBe(true);
    expect(rateLimit(userId, action, limit, timeWindow)).toBe(true);
    expect(rateLimit(userId, action, limit, timeWindow)).toBe(false);
    expect(rateLimit(userId, action, limit, timeWindow)).toBe(false);
  });

  test('resets action count after time window expires', () => {
    const userId = 'user3';
    const action = 'post';
    const limit = 2;
    const timeWindow = 3; // in seconds

    expect(rateLimit(userId, action, limit, timeWindow)).toBe(true);
    expect(rateLimit(userId, action, limit, timeWindow)).toBe(true);
    expect(rateLimit(userId, action, limit, timeWindow)).toBe(false);

    // Advance time past the time window (in milliseconds)
    jest.advanceTimersByTime((timeWindow + 1) * 1000);

    // After the time window, the count should be reset.
    expect(rateLimit(userId, action, limit, timeWindow)).toBe(true);
  });

  test('handles different actions independently', () => {
    const userId = 'user4';
    const actionLogin = 'login';
    const actionComment = 'comment';
    const limit = 1;
    const timeWindow = 10;

    expect(rateLimit(userId, actionLogin, limit, timeWindow)).toBe(true);
    expect(rateLimit(userId, actionLogin, limit, timeWindow)).toBe(false);

    // Different action should be independent.
    expect(rateLimit(userId, actionComment, limit, timeWindow)).toBe(true);
    expect(rateLimit(userId, actionComment, limit, timeWindow)).toBe(false);
  });

  test('handles different users independently', () => {
    const action = 'share';
    const limit = 2;
    const timeWindow = 10;

    // User A calls
    expect(rateLimit('userA', action, limit, timeWindow)).toBe(true);
    expect(rateLimit('userA', action, limit, timeWindow)).toBe(true);
    expect(rateLimit('userA', action, limit, timeWindow)).toBe(false);

    // User B calls
    expect(rateLimit('userB', action, limit, timeWindow)).toBe(true);
    expect(rateLimit('userB', action, limit, timeWindow)).toBe(true);
    expect(rateLimit('userB', action, limit, timeWindow)).toBe(false);
  });

  test('returns false for empty userId', () => {
    const action = 'view';
    const limit = 1;
    const timeWindow = 10;

    expect(rateLimit('', action, limit, timeWindow)).toBe(false);
    expect(rateLimit(null, action, limit, timeWindow)).toBe(false);
    expect(rateLimit(undefined, action, limit, timeWindow)).toBe(false);
  });

  test('returns false for empty action name', () => {
    const userId = 'user5';
    const limit = 1;
    const timeWindow = 10;

    expect(rateLimit(userId, '', limit, timeWindow)).toBe(false);
    expect(rateLimit(userId, null, limit, timeWindow)).toBe(false);
    expect(rateLimit(userId, undefined, limit, timeWindow)).toBe(false);
  });

  test('handles very short time windows', () => {
    const userId = 'user6';
    const action = 'click';
    const limit = 1;
    const timeWindow = 1; // in seconds

    expect(rateLimit(userId, action, limit, timeWindow)).toBe(true);
    expect(rateLimit(userId, action, limit, timeWindow)).toBe(false);

    // Advance half a second; still within time window.
    jest.advanceTimersByTime(500);
    expect(rateLimit(userId, action, limit, timeWindow)).toBe(false);

    // Advance beyond the time window to allow a reset.
    jest.advanceTimersByTime(600);
    expect(rateLimit(userId, action, limit, timeWindow)).toBe(true);
  });

  test('rapid consecutive calls should enforce limit correctly', () => {
    const userId = 'user7';
    const action = 'download';
    const limit = 5;
    const timeWindow = 10;

    const results = [];
    for (let i = 0; i < 10; i++) {
      results.push(rateLimit(userId, action, limit, timeWindow));
    }
    const allowedCount = results.filter(result => result === true).length;
    expect(allowedCount).toBe(limit);
  });
});