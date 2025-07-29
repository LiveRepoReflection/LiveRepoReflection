const { DistributedRateLimiter } = require('../distributed_rate_limiter');

// A fake cache client that simulates a working distributed cache.
class FakeCacheClient {
  constructor() {
    this.store = new Map();
    this.timeouts = new Map();
  }

  async get(key) {
    const record = this.store.get(key);
    if (!record) return null;
    const { value, expiry } = record;
    if (expiry && Date.now() > expiry) {
      this.store.delete(key);
      return null;
    }
    return value;
  }

  async set(key, value, expiryMs) {
    const expiry = expiryMs ? Date.now() + expiryMs : null;
    this.store.set(key, { value, expiry });
  }

  async incrementAndGet(key, expiryMs) {
    let record = this.store.get(key);
    let current = 0;
    if (record) {
      const { value, expiry } = record;
      if (expiry && Date.now() > expiry) {
        current = 0;
      } else {
        current = value;
      }
    }
    current += 1;
    const newExpiry = expiryMs ? Date.now() + expiryMs : null;
    this.store.set(key, { value: current, expiry: newExpiry });
    return current;
  }

  async decrementAndGet(key) {
    let record = this.store.get(key);
    let current = 0;
    if (record) {
      const { value, expiry } = record;
      if (expiry && Date.now() > expiry) {
        current = 0;
      } else {
        current = value;
      }
    }
    current -= 1;
    this.store.set(key, { value: current, expiry: null });
    return current;
  }
}

// A failing cache client that always throws an error.
class FailingCacheClient {
  async get(key) {
    throw new Error('Cache not available');
  }
  async set(key, value, expiryMs) {
    throw new Error('Cache not available');
  }
  async incrementAndGet(key, expiryMs) {
    throw new Error('Cache not available');
  }
  async decrementAndGet(key) {
    throw new Error('Cache not available');
  }
}

describe('DistributedRateLimiter with working cache', () => {
  // Use a short time window for tests.
  const maxRequests = 3;
  const timeWindowMs = 1000;
  let rateLimiter;
  let cacheClient;

  beforeEach(() => {
    cacheClient = new FakeCacheClient();
    rateLimiter = new DistributedRateLimiter({ maxRequests, timeWindowMs, cacheClient });
  });

  test('allows requests under the limit', async () => {
    const clientId = 'client1';
    const res1 = await rateLimiter.isAllowed(clientId);
    const res2 = await rateLimiter.isAllowed(clientId);
    expect(res1).toBe(true);
    expect(res2).toBe(true);
  });

  test('rejects requests exceeding the limit', async () => {
    const clientId = 'client2';
    // First maxRequests calls should be allowed
    for (let i = 0; i < maxRequests; i++) {
      const allowed = await rateLimiter.isAllowed(clientId);
      expect(allowed).toBe(true);
    }
    // Next call should return false
    const allowed = await rateLimiter.isAllowed(clientId);
    expect(allowed).toBe(false);
  });

  test('resets counter after time window', async () => {
    jest.useFakeTimers();
    const clientId = 'client3';
    // Use maxRequests calls, then simulate time passing.
    for (let i = 0; i < maxRequests; i++) {
      const allowed = await rateLimiter.isAllowed(clientId);
      expect(allowed).toBe(true);
    }
    const allowedAfterLimit = await rateLimiter.isAllowed(clientId);
    expect(allowedAfterLimit).toBe(false);

    // Fast-forward time past the window
    jest.advanceTimersByTime(timeWindowMs + 10);
    // Await a promise resolution cycle to let any timers complete.
    await Promise.resolve();

    // The counter should be reset.
    const allowedAfterReset = await rateLimiter.isAllowed(clientId);
    expect(allowedAfterReset).toBe(true);
    jest.useRealTimers();
  });
});

describe('DistributedRateLimiter with failing cache (fallback mechanism)', () => {
  // The fallback max requests and time window.
  const fallbackMaxRequests = 2;
  const fallbackTimeWindowMs = 1000;
  let rateLimiter;
  let cacheClient;

  beforeEach(() => {
    cacheClient = new FailingCacheClient();
    rateLimiter = new DistributedRateLimiter({
      maxRequests: 10, // normal limit which will be ignored
      timeWindowMs: 1000,
      cacheClient,
      fallbackMaxRequests,
      fallbackTimeWindowMs
    });
  });

  test('allows requests under the fallback limit', async () => {
    const clientId = 'clientFallback1';
    const res1 = await rateLimiter.isAllowed(clientId);
    const res2 = await rateLimiter.isAllowed(clientId);
    expect(res1).toBe(true);
    expect(res2).toBe(true);
  });

  test('rejects requests exceeding the fallback limit', async () => {
    const clientId = 'clientFallback2';
    for (let i = 0; i < fallbackMaxRequests; i++) {
      const allowed = await rateLimiter.isAllowed(clientId);
      expect(allowed).toBe(true);
    }
    const notAllowed = await rateLimiter.isAllowed(clientId);
    expect(notAllowed).toBe(false);
  });

  test('fallback resets counter after fallback time window', async () => {
    jest.useFakeTimers();
    const clientId = 'clientFallback3';
    for (let i = 0; i < fallbackMaxRequests; i++) {
      const allowed = await rateLimiter.isAllowed(clientId);
      expect(allowed).toBe(true);
    }
    const disallowed = await rateLimiter.isAllowed(clientId);
    expect(disallowed).toBe(false);

    // Advance fallback timer
    jest.advanceTimersByTime(fallbackTimeWindowMs + 10);
    await Promise.resolve();

    const allowedAfterReset = await rateLimiter.isAllowed(clientId);
    expect(allowedAfterReset).toBe(true);
    jest.useRealTimers();
  });
});

describe('DistributedRateLimiter multiple clients', () => {
  const maxRequests = 5;
  const timeWindowMs = 2000;
  let rateLimiter;
  let cacheClient;

  beforeEach(() => {
    cacheClient = new FakeCacheClient();
    rateLimiter = new DistributedRateLimiter({ maxRequests, timeWindowMs, cacheClient });
  });

  test('separates limits per client', async () => {
    const clientA = 'clientA';
    const clientB = 'clientB';
    // For clientA, exhaust the limit.
    for (let i = 0; i < maxRequests; i++) {
      const allowed = await rateLimiter.isAllowed(clientA);
      expect(allowed).toBe(true);
    }
    const allowedA = await rateLimiter.isAllowed(clientA);
    expect(allowedA).toBe(false);

    // ClientB should still be allowed.
    for (let i = 0; i < maxRequests; i++) {
      const allowed = await rateLimiter.isAllowed(clientB);
      expect(allowed).toBe(true);
    }
    const allowedB = await rateLimiter.isAllowed(clientB);
    expect(allowedB).toBe(false);
  });
});