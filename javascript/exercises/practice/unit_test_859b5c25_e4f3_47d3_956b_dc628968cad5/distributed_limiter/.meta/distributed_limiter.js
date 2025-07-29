class DistributedRateLimiter {
  constructor() {
    this.clients = new Map();
  }

  configureRateLimit(clientId, rateLimitConfig) {
    // rateLimitConfig: { limit, windowMs, evictionTime (optional) }
    if (!this.clients.has(clientId)) {
      this.clients.set(clientId, {
        config: rateLimitConfig,
        timestamps: []
      });
    } else {
      const clientData = this.clients.get(clientId);
      clientData.config = rateLimitConfig;
    }
  }

  isAllowed(clientId) {
    const now = Date.now();
    if (!this.clients.has(clientId)) {
      // If the client hasn't been configured, return false.
      return false;
    }
    const clientData = this.clients.get(clientId);
    const { limit, windowMs, evictionTime } = clientData.config;
    let timestamps = clientData.timestamps;

    // Remove expired timestamps (older than the window)
    let validTimestamps = timestamps.filter(ts => ts > now - windowMs);

    // If evictionTime is provided and there are no valid timestamps,
    // we can clear the old timestamps to free up memory.
    if (validTimestamps.length === 0 && timestamps.length > 0 && evictionTime !== undefined) {
      const mostRecentTimestamp = Math.max(...timestamps);
      if (now - mostRecentTimestamp >= windowMs + evictionTime) {
        validTimestamps = [];
      }
    }

    if (validTimestamps.length < limit) {
      validTimestamps.push(now);
      clientData.timestamps = validTimestamps;
      return true;
    } else {
      clientData.timestamps = validTimestamps;
      return false;
    }
  }
}

module.exports = DistributedRateLimiter;