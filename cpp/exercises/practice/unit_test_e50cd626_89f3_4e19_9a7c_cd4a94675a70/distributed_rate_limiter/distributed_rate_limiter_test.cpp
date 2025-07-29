#include "distributed_rate_limiter.h"
#include "catch.hpp"

TEST_CASE("Single request within limit", "[RateLimiter]") {
    RateLimiter limiter;
    limiter.setRateLimit("user1", 5, 10); // 5 requests per 10 seconds

    // First 5 requests should be allowed.
    for (int i = 0; i < 5; ++i) {
        REQUIRE(limiter.allowRequest("user1", 100));
    }
}

TEST_CASE("Exceeding rate limit", "[RateLimiter]") {
    RateLimiter limiter;
    limiter.setRateLimit("user2", 3, 10); // 3 requests per 10 seconds
    int timestamp = 200;

    // 3 requests allowed.
    REQUIRE(limiter.allowRequest("user2", timestamp));
    REQUIRE(limiter.allowRequest("user2", timestamp));
    REQUIRE(limiter.allowRequest("user2", timestamp));
    // 4th request within same window should be rejected.
    REQUIRE_FALSE(limiter.allowRequest("user2", timestamp));
}

TEST_CASE("Window expiration resets limit", "[RateLimiter]") {
    RateLimiter limiter;
    limiter.setRateLimit("user3", 2, 5); // 2 requests per 5 seconds

    int t1 = 300;
    // Consume the rate limit.
    REQUIRE(limiter.allowRequest("user3", t1));
    REQUIRE(limiter.allowRequest("user3", t1));
    REQUIRE_FALSE(limiter.allowRequest("user3", t1));

    // After time window expires, the limit should reset.
    int t2 = t1 + 6;
    REQUIRE(limiter.allowRequest("user3", t2));
    REQUIRE(limiter.allowRequest("user3", t2));
    REQUIRE_FALSE(limiter.allowRequest("user3", t2));
}

TEST_CASE("Multiple users", "[RateLimiter]") {
    RateLimiter limiter;
    limiter.setRateLimit("userA", 2, 10); // User A: 2 req per 10 sec
    limiter.setRateLimit("userB", 4, 10); // User B: 4 req per 10 sec

    int t = 400;
    // Test for userA.
    REQUIRE(limiter.allowRequest("userA", t));
    REQUIRE(limiter.allowRequest("userA", t));
    REQUIRE_FALSE(limiter.allowRequest("userA", t));

    // Test for userB.
    for (int i = 0; i < 4; ++i) {
        REQUIRE(limiter.allowRequest("userB", t));
    }
    REQUIRE_FALSE(limiter.allowRequest("userB", t));
}

TEST_CASE("Consecutive windows with expiring requests", "[RateLimiter]") {
    RateLimiter limiter;
    limiter.setRateLimit("userX", 3, 10); // 3 requests per 10 seconds

    // Issue requests at different timestamps.
    REQUIRE(limiter.allowRequest("userX", 0));  // first request at t=0
    REQUIRE(limiter.allowRequest("userX", 5));  // second request at t=5
    REQUIRE(limiter.allowRequest("userX", 9));  // third request at t=9
    // At t=10, the request at t=0 should expire.
    REQUIRE(limiter.allowRequest("userX", 10));
    // Within window [5,10], there are now 3 requests; next should be rejected.
    REQUIRE_FALSE(limiter.allowRequest("userX", 10));
}

TEST_CASE("Rapid succession and random timing", "[RateLimiter]") {
    RateLimiter limiter;
    limiter.setRateLimit("user_random", 5, 10); // 5 requests per 10 sec

    int start = 500;
    int allowedCount = 0;
    // Simulate requests at timestamps start, start+1, ..., start+9.
    for (int i = 0; i < 10; ++i) {
        if (limiter.allowRequest("user_random", start + i)) {
            allowedCount++;
        }
    }
    // Ensure that within any 10 second window, the allowed count does not exceed 5.
    REQUIRE(allowedCount <= 5);
}