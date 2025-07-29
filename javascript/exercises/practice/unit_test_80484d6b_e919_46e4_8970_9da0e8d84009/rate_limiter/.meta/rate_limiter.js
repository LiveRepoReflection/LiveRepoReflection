class RateLimiter {
  constructor(options) {
    if (!options || typeof options.limit !== 'number' || typeof options.windowMs !== 'number') {
      throw new Error("Invalid configuration: must provide limit and windowMs");
    }
    this.limit = options.limit;
    this.windowMs = options.windowMs;
    this.algorithm = options.algorithm || "fixed_window";
    // Using a Map to store per-user rate limiting data
    // For fixed_window: { windowStart: timestamp, count: number }
    // For token_bucket: { tokens: number, lastRefill: timestamp }
    this.users = new Map();
  }

  isAllowed(userId) {
    const now = Date.now();

    if (this.algorithm === "fixed_window") {
      let userData = this.users.get(userId);
      if (!userData) {
        userData = { windowStart: now, count: 1 };
        this.users.set(userId, userData);
        return true;
      }
      if (now - userData.windowStart >= this.windowMs) {
        // Reset for a new window
        userData.windowStart = now;
        userData.count = 1;
        this.users.set(userId, userData);
        return true;
      } else {
        if (userData.count < this.limit) {
          userData.count++;
          this.users.set(userId, userData);
          return true;
        } else {
          return false;
        }
      }
    } else if (this.algorithm === "token_bucket") {
      let userData = this.users.get(userId);
      if (!userData) {
        // Initialize new bucket at capacity
        userData = { tokens: this.limit, lastRefill: now };
      } else {
        // Calculate the number of tokens to replenish based on time elapsed
        const elapsed = now - userData.lastRefill;
        const refillRate = this.limit / this.windowMs; // tokens per millisecond
        userData.tokens = Math.min(this.limit, userData.tokens + elapsed * refillRate);
        userData.lastRefill = now;
      }
      if (userData.tokens >= 1) {
        // Allow request and consume a token
        userData.tokens -= 1;
        this.users.set(userId, userData);
        return true;
      } else {
        this.users.set(userId, userData);
        return false;
      }
    } else {
      throw new Error("Unsupported algorithm: " + this.algorithm);
    }
  }
}

module.exports = { RateLimiter };