'use strict';

class RateLimiter {
  constructor({ maxRequests, windowMs }) {
    if (typeof maxRequests !== 'number' || maxRequests <= 0) {
      throw new Error('maxRequests must be a positive number');
    }
    if (typeof windowMs !== 'number' || windowMs <= 0) {
      throw new Error('windowMs must be a positive number');
    }
    this.maxRequests = maxRequests;
    this.windowMs = windowMs;
    // Map to store each user's request timestamps (in milliseconds).
    this.userRequests = new Map();
  }

  check(userId, timestamp) {
    if (typeof userId !== 'string') {
      throw new Error('userId must be a string');
    }
    if (typeof timestamp !== 'number') {
      throw new Error('timestamp must be a number');
    }

    let timestamps = this.userRequests.get(userId);
    if (!timestamps) {
      timestamps = [];
      this.userRequests.set(userId, timestamps);
    }

    // Remove timestamps that are outside the current window.
    while (timestamps.length && timestamps[0] <= timestamp - this.windowMs) {
      timestamps.shift();
    }

    if (timestamps.length < this.maxRequests) {
      // Allow the request, record its timestamp.
      timestamps.push(timestamp);
      return { allowRequest: true, retryAfter: 0 };
    } else {
      // Request exceeds limit: calculate the time remaining until the oldest request exits the window.
      const earliestTimestamp = timestamps[0];
      let retryAfterSeconds = (earliestTimestamp + this.windowMs - timestamp) / 1000;
      if (retryAfterSeconds < 0) {
        retryAfterSeconds = 0;
      }
      return { allowRequest: false, retryAfter: retryAfterSeconds };
    }
  }
}

module.exports = RateLimiter;