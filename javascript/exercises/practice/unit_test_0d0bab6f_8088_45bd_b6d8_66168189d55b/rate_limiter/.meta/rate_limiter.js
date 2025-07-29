"use strict";

const config = {
  bucketCapacity: 3,
  refillInterval: 1000
};

const tokenBuckets = new Map();

function getCompositeKey(userId, endpoint) {
  return `${userId}#${endpoint}`;
}

function allowRequest(userId, endpoint) {
  if (typeof userId !== "string" || !userId.trim()) {
    throw new Error("Invalid userId");
  }
  if (typeof endpoint !== "string" || !endpoint.trim()) {
    throw new Error("Invalid endpoint");
  }
  
  const now = Date.now();
  const key = getCompositeKey(userId, endpoint);
  let bucket = tokenBuckets.get(key);
  
  if (!bucket) {
    bucket = {
      tokens: config.bucketCapacity,
      lastRefillTime: now
    };
    tokenBuckets.set(key, bucket);
  } else {
    const elapsed = now - bucket.lastRefillTime;
    if (elapsed > 0) {
      const tokensToAdd = Math.floor(elapsed / config.refillInterval);
      if (tokensToAdd > 0) {
        bucket.tokens = Math.min(config.bucketCapacity, bucket.tokens + tokensToAdd);
        bucket.lastRefillTime += tokensToAdd * config.refillInterval;
      }
    }
  }
  
  if (bucket.tokens > 0) {
    bucket.tokens -= 1;
    return true;
  }
  return false;
}

function resetRateLimiter() {
  tokenBuckets.clear();
}

function configureRateLimiter(options) {
  if (typeof options !== "object" || options === null) {
    throw new Error("Configuration options must be an object");
  }
  if (options.bucketCapacity !== undefined) {
    if (typeof options.bucketCapacity !== "number" || options.bucketCapacity <= 0) {
      throw new Error("Invalid bucketCapacity");
    }
    config.bucketCapacity = options.bucketCapacity;
  }
  if (options.refillInterval !== undefined) {
    if (typeof options.refillInterval !== "number" || options.refillInterval <= 0) {
      throw new Error("Invalid refillInterval");
    }
    config.refillInterval = options.refillInterval;
  }
}

module.exports = {
  allowRequest,
  resetRateLimiter,
  configureRateLimiter
};