class RateLimiter {
  constructor() {
    // No instance-specific state; using a shared static store to simulate a distributed datastore.
  }

  static get distributedStore() {
    if (!RateLimiter._store) {
      RateLimiter._store = new Map();
    }
    return RateLimiter._store;
  }

  static reset() {
    RateLimiter._store = new Map();
  }

  isAllowed(clientId, action, limit, timeWindow) {
    if (clientId === null || clientId === undefined) {
      throw new Error("Invalid clientId");
    }
    if (action === null || action === undefined) {
      throw new Error("Invalid action");
    }
    if (!Number.isInteger(limit) || limit <= 0) {
      throw new Error("Invalid limit");
    }
    if (!Number.isInteger(timeWindow) || timeWindow <= 0) {
      throw new Error("Invalid timeWindow");
    }
    
    const key = `${clientId}:${action}`;
    const currentTime = Date.now();
    const windowStart = currentTime - timeWindow;
    const store = RateLimiter.distributedStore;
    
    let timestamps = store.get(key);
    if (!timestamps) {
      timestamps = [];
    }
    
    // Remove expired timestamps
    timestamps = timestamps.filter(timestamp => timestamp > windowStart);
    
    if (timestamps.length < limit) {
      timestamps.push(currentTime);
      store.set(key, timestamps);
      return true;
    } else {
      store.set(key, timestamps);
      return false;
    }
  }
}

module.exports = { RateLimiter };