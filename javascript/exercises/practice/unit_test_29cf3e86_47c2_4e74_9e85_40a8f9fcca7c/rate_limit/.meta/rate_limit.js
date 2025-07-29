'use strict';

// In-memory simulated distributed key-value store.
// Each key maps to an object { count: number, expireAt: number }
const store = new Map();

function rateLimit(userId, action, limit, timeWindow) {
  // Validate inputs: userId and action must be non-empty strings;
  // limit and timeWindow must be positive numbers.
  if (!userId || typeof userId !== 'string' || !action || typeof action !== 'string') {
    return false;
  }
  if (typeof limit !== 'number' || limit <= 0 || typeof timeWindow !== 'number' || timeWindow <= 0) {
    return false;
  }

  const key = `${userId}:${action}`;
  const now = Date.now();
  const entry = store.get(key);
  
  // If no entry exists or the existing entry has expired, create a new one.
  if (!entry || now > entry.expireAt) {
    store.set(key, { count: 1, expireAt: now + timeWindow * 1000 });
    return true;
  }
  
  // If the limit has not been reached, increment and allow the action.
  if (entry.count < limit) {
    entry.count++;
    store.set(key, entry);
    return true;
  }
  
  // Limit reached within the current window, so block the action.
  return false;
}

module.exports = { rateLimit };