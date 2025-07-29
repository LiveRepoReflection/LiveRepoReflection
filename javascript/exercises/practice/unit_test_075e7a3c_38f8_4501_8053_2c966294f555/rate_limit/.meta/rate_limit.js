'use strict';

const { performance } = require('perf_hooks');

let config = {
  timeWindow: 60000,            // default window in ms
  capacity: 100,                // maximum token capacity
  replenishRate: 100 / 60000,   // tokens replenished per ms (default: 100 tokens per 60,000 ms)
  redisHost: 'localhost',
  redisPort: 6379
};

let simulatedRedisStore = {};
let simulateError = false;

function getCurrentTime() {
  return Date.now();
}

// Simulates an atomic token bucket update using an in-memory store.
async function redisTokenBucket(key, requestCost, currentTime) {
  let entry = simulatedRedisStore[key];
  if (!entry) {
    // New user entry: start with full capacity
    entry = { tokens: config.capacity, last: currentTime };
  }
  let elapsed = currentTime - entry.last;
  let refill = elapsed * config.replenishRate;
  let newTokens = Math.min(config.capacity, entry.tokens + refill);
  if (newTokens < requestCost) {
    // Not enough tokens to cover requestCost; update entry and block request.
    entry.tokens = newTokens;
    entry.last = currentTime;
    simulatedRedisStore[key] = entry;
    return false;
  } else {
    // Allow the request and deduct the requested cost.
    entry.tokens = newTokens - requestCost;
    entry.last = currentTime;
    simulatedRedisStore[key] = entry;
    return true;
  }
}

async function rateLimit(userId, requestCost) {
  return new Promise(async (resolve, reject) => {
    try {
      if (simulateError) {
        // Fallback mechanism: allow the request when Redis is simulated to be in error.
        return resolve(true);
      }
      if (userId === null || userId === undefined || userId === '') {
        throw new Error('Invalid userId');
      }
      if (typeof requestCost !== 'number' || requestCost <= 0) {
        throw new Error('Invalid requestCost');
      }
      const currentTime = getCurrentTime();
      const allowed = await redisTokenBucket(userId, requestCost, currentTime);
      resolve(allowed);
    } catch (err) {
      reject(err);
    }
  });
}

function configure(newConfig) {
  if (newConfig.timeWindow !== undefined) {
    config.timeWindow = newConfig.timeWindow;
  }
  if (newConfig.capacity !== undefined) {
    config.capacity = newConfig.capacity;
  }
  if (newConfig.replenishRate !== undefined) {
    config.replenishRate = newConfig.replenishRate;
  }
  if (newConfig.redisHost !== undefined) {
    config.redisHost = newConfig.redisHost;
  }
  if (newConfig.redisPort !== undefined) {
    config.redisPort = newConfig.redisPort;
  }
  // Reset the simulated store when configuration changes for isolation in tests.
  simulatedRedisStore = {};
}

function simulateRedisError(flag) {
  simulateError = flag;
}

module.exports = {
  rateLimit,
  configure,
  simulateRedisError
};