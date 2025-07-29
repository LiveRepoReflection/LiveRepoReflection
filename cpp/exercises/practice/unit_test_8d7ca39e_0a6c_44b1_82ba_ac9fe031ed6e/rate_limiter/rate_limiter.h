#pragma once

#include <string>

class RateLimiter {
public:
    // Constructor: takes the rate limit (requests per window),
    // window duration (in milliseconds), and any necessary configuration
    // for the data store.
    RateLimiter(int rateLimit, int windowDurationMs);
    
    virtual ~RateLimiter() = default;

    // Attempts to acquire a permit for the given key.
    // Returns true if the request is allowed, false if it is rate limited.
    virtual bool allow(const std::string& key);

private:
    // Implementation details (data store, rate limiting algorithm, etc.)
    // To be implemented by the candidate
    int rateLimit_;
    int windowDurationMs_;
};