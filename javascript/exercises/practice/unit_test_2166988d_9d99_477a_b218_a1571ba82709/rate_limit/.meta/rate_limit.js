class RateLimiter {
  constructor(options) {
    if (!options || typeof options.limit !== 'number' || typeof options.window !== 'number' || !options.redisClient) {
      throw new Error('Missing or invalid options. Must include limit, window, and redisClient.');
    }
    this.limit = options.limit;
    this.window = options.window;
    this.redisClient = options.redisClient;
    // Preload the Lua script that implements sliding window rate limiting.
    this.luaScript = `
      local key = KEYS[1]
      local now = tonumber(ARGV[1])
      local window = tonumber(ARGV[2])
      local limit = tonumber(ARGV[3])
      -- Remove timestamps older than (now - window)
      redis.call('ZREMRANGEBYSCORE', key, '-inf', now - window)
      local currentCount = redis.call('ZCARD', key)
      if currentCount < limit then
        redis.call('ZADD', key, now, tostring(now))
        -- Set expiry for the key to avoid unbounded growth
        redis.call('EXPIRE', key, math.floor(window / 1000) + 1)
        return 1
      else
        return 0
      end
    `;
  }

  async isAllowed(userId) {
    if (!userId) {
      throw new Error('User ID is required.');
    }
    const key = `rate_limit:${userId}`;
    const now = Date.now();
    const args = [now.toString(), this.window.toString(), this.limit.toString()];
    try {
      const result = await this.redisClient.eval(this.luaScript, [key], args);
      return result === 1;
    } catch (err) {
      throw err;
    }
  }
}

module.exports = RateLimiter;