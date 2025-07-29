class RateLimiter {
  constructor(options) {
    if (!options || typeof options !== 'object') {
      throw new Error('Options must be provided');
    }
    const { limit, interval } = options;
    if (typeof limit !== 'number' || limit <= 0) {
      throw new Error('Invalid limit configuration');
    }
    if (typeof interval !== 'number' || interval <= 0) {
      throw new Error('Invalid interval configuration');
    }
    this.limit = limit;
    this.interval = interval;
    // Map to hold the rate limiting buckets per key.
    // Each bucket keeps track of the count and the window start time.
    this.buckets = new Map();
  }

  tryRequest(key) {
    if (!key) {
      throw new Error('Key is required');
    }
    const now = Date.now();
    if (!this.buckets.has(key)) {
      this.buckets.set(key, { count: 0, startTime: now });
    }
    const bucket = this.buckets.get(key);
    // Reset the bucket if the current window has expired.
    if (now - bucket.startTime >= this.interval) {
      bucket.count = 0;
      bucket.startTime = now;
    }
    // Allow the request if under the limit.
    if (bucket.count < this.limit) {
      bucket.count += 1;
      return true;
    }
    return false;
  }

  getResetTime(key) {
    if (!key) {
      throw new Error('Key is required');
    }
    const now = Date.now();
    if (!this.buckets.has(key)) {
      return 0;
    }
    const bucket = this.buckets.get(key);
    const elapsed = now - bucket.startTime;
    const remaining = this.interval - elapsed;
    return remaining > 0 ? remaining : 0;
  }
}

module.exports = RateLimiter;