class RateLimiter {
  constructor(config, sharedStore) {
    if (!config || typeof config !== 'object') {
      throw new Error('Invalid configuration');
    }
    const { limit, window } = config;
    if (typeof limit !== 'number' || limit <= 0) {
      throw new Error('Limit must be a positive number');
    }
    if (typeof window !== 'number' || window <= 0) {
      throw new Error('Window must be a positive number');
    }
    this.limit = limit;
    this.window = window;
    if (sharedStore && typeof sharedStore === 'object') {
      // If sharedStore is provided, check if it is a plain object or a Map.
      this.useObjectStore = !(sharedStore instanceof Map);
      this.store = sharedStore;
    } else {
      // Use local store with Map if no shared store is provided.
      this.useObjectStore = false;
      this.store = new Map();
    }
  }

  async consume(key) {
    return new Promise((resolve, reject) => {
      if (typeof key !== 'string') {
        reject(new Error('Invalid key: key must be a string'));
        return;
      }
      const now = Date.now();
      let timestamps;
      if (this.useObjectStore) {
        if (!Object.prototype.hasOwnProperty.call(this.store, key)) {
          this.store[key] = [];
        }
        timestamps = this.store[key];
      } else {
        if (!this.store.has(key)) {
          this.store.set(key, []);
        }
        timestamps = this.store.get(key);
      }
      // Remove timestamps older than the sliding window.
      while (timestamps.length && now - timestamps[0] >= this.window) {
        timestamps.shift();
      }
      if (timestamps.length < this.limit) {
        timestamps.push(now);
        resolve(true);
      } else {
        resolve(false);
      }
    });
  }
}

module.exports = { RateLimiter };