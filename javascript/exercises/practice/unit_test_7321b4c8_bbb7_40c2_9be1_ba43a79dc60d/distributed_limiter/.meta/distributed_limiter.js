class DistributedRateLimiter {
  constructor() {
    // Map to store request timestamps for each user and endpoint.
    // Key: "userId::apiEndpoint", Value: Array of request timestamps.
    this.requestLog = new Map();
  }

  async isAllowed(userId, apiEndpoint, timestamp) {
    // Retrieve rate limit settings using the configuration service.
    // If getRateLimit is not defined, use the default of 60 requests per 60000ms.
    const rateConfig =
      typeof getRateLimit === 'function'
        ? getRateLimit(userId, apiEndpoint)
        : { limit: 60, window: 60000 };
    const { limit, window } = rateConfig;

    // Create a unique key for the combination of user and endpoint.
    const key = `${userId}::${apiEndpoint}`;

    // Retrieve the array of timestamps for this user and endpoint.
    let timestamps = this.requestLog.get(key);
    if (!timestamps) {
      timestamps = [];
    }

    // Remove timestamps that are older than the current window.
    const windowStart = timestamp - window;
    timestamps = timestamps.filter((time) => time > windowStart);

    // If the number of requests in the window is below the limit, allow the request.
    if (timestamps.length < limit) {
      timestamps.push(timestamp);
      this.requestLog.set(key, timestamps);
      return true;
    }

    // If the limit is reached, update the record and block the request.
    this.requestLog.set(key, timestamps);
    return false;
  }
}

module.exports = { DistributedRateLimiter };