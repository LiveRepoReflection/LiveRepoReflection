class DistributedRateLimiter {
  /**
   * @param {object} options
   * @param {number} options.maxRequests The maximum number of requests allowed within the time window.
   * @param {number} options.timeWindowMs The length of the time window in milliseconds.
   * @param {object} options.cacheClient An object representing the distributed cache client (e.g., a Redis client).
   *   It should have get, set, incrementAndGet, and decrementAndGet methods.
   * @param {number} [options.fallbackMaxRequests] Optional: The maximum number of requests allowed in the fallback mechanism.
   * @param {number} [options.fallbackTimeWindowMs] Optional: The length of the fallback time window in milliseconds.
   */
  constructor(options) {
    this.maxRequests = options.maxRequests;
    this.timeWindowMs = options.timeWindowMs;
    this.cacheClient = options.cacheClient;

    // Set fallback values; if not provided, choose reasonable defaults.
    this.fallbackMaxRequests =
      options.fallbackMaxRequests !== undefined
        ? options.fallbackMaxRequests
        : Math.floor(this.maxRequests / 2);
    this.fallbackTimeWindowMs =
      options.fallbackTimeWindowMs !== undefined
        ? options.fallbackTimeWindowMs
        : this.timeWindowMs;

    // Local in-memory store for fallback mechanism.
    // It stores records per clientId: { count: number, resetTime: number }
    this.fallbackMap = new Map();
  }

  /**
   * Checks if a client is allowed to make a request.
   * @param {string} clientId The unique identifier of the client.
   * @returns {Promise<boolean>} A promise that resolves to true if the client is allowed, false otherwise.
   */
  async isAllowed(clientId) {
    const key = `rate:${clientId}`;
    try {
      // Use the distributed cache's atomic increment.
      const count = await this.cacheClient.incrementAndGet(key, this.timeWindowMs);
      if (count > this.maxRequests) {
        return false;
      }
      return true;
    } catch (err) {
      // Fallback mechanism using local in-memory store if cache is unavailable.
      const now = Date.now();
      let record = this.fallbackMap.get(clientId);
      if (!record || now > record.resetTime) {
        // Initialize or reset the record for this client.
        record = {
          count: 1,
          resetTime: now + this.fallbackTimeWindowMs,
        };
        this.fallbackMap.set(clientId, record);
        return true;
      } else {
        record.count += 1;
        this.fallbackMap.set(clientId, record);
        if (record.count > this.fallbackMaxRequests) {
          return false;
        }
        return true;
      }
    }
  }
}

module.exports = { DistributedRateLimiter };