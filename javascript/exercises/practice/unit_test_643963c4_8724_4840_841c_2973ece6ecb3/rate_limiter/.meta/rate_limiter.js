'use strict';

// Default global configuration values
const DEFAULT_REQUEST_LIMIT = 100;
const DEFAULT_TIME_WINDOW = 60; // in seconds

// Use the global user configuration store if available; otherwise, create a new Map.
const userLimits = global.userLimits || new Map();

/**
 * Configure a specific rate limit for a user. This configuration overrides the default limit.
 *
 * @param {string} userId - Unique identifier for the user (alphanumeric characters only).
 * @param {number} requestLimit - Maximum allowed number of requests within the time window.
 * @param {number} timeWindow - Time window in seconds.
 * @throws Will throw an error if input parameters are invalid.
 */
function configureUserLimit(userId, requestLimit, timeWindow) {
  if (typeof userId !== 'string' || !/^[a-z0-9]+$/i.test(userId)) {
    throw new Error('Invalid userId');
  }
  if (!Number.isInteger(requestLimit) || requestLimit <= 0) {
    throw new Error('requestLimit must be a positive integer');
  }
  if (!Number.isInteger(timeWindow) || timeWindow <= 0) {
    throw new Error('timeWindow must be a positive integer');
  }
  userLimits.set(userId, { requestLimit, timeWindow });
}

/**
 * Determine if a request from a given user is allowed based on the configured rate limit.
 *
 * The function calculates the current time window based on the user's configuration (or default configuration)
 * and uses an atomic increment operation to count the number of requests within the current window.
 * If the count exceeds the request limit, the function returns false, indicating that the request is blocked.
 *
 * @param {string} userId - Unique identifier for the user.
 * @returns {boolean} - Returns true if the request is allowed; false otherwise.
 */
function isAllowed(userId) {
  // Get the configuration for this user, or fall back to default configuration.
  let config = userLimits.get(userId);
  if (!config) {
    config = { requestLimit: DEFAULT_REQUEST_LIMIT, timeWindow: DEFAULT_TIME_WINDOW };
  }
  const { requestLimit, timeWindow } = config;

  // Get the current time (in seconds). Assumes a global getTimeInSeconds() function.
  const currentTime = global.getTimeInSeconds();
  // Calculate the current time window start time.
  const windowStart = Math.floor(currentTime / timeWindow) * timeWindow;
  
  // Construct a unique key for this user's current time window.
  const key = `rl:${userId}:${windowStart}`;
  
  // Atomically increment the request count for the given key. The key expires after timeWindow seconds.
  // Assumes a global atomicIncrement(key, expiryInSeconds) function.
  const requestCount = global.atomicIncrement(key, timeWindow);
  
  // If the number of requests does not exceed the limit, the request is allowed.
  return requestCount <= requestLimit;
}

module.exports = {
  isAllowed,
  configureUserLimit
};