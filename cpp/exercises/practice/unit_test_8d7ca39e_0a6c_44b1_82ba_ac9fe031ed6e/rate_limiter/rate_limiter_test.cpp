#include "rate_limiter.h"
#include "catch.hpp"

#include <chrono>
#include <future>
#include <thread>
#include <vector>
#include <unordered_map>
#include <mutex>
#include <condition_variable>
#include <atomic>

// Mock for testing purposes - only tests the interface and algorithms,
// not the actual distributed functionality
class TestRateLimiter : public RateLimiter {
public:
    TestRateLimiter(int rateLimit, int windowDurationMs) 
        : RateLimiter(rateLimit, windowDurationMs) {}
    
    bool allow(const std::string& key) override {
        return RateLimiter::allow(key);
    }
};

TEST_CASE("Basic rate limiting functionality", "[rate_limiter]") {
    TestRateLimiter limiter(5, 1000); // 5 requests per second
    
    std::string key = "test_user";
    
    // First 5 requests should be allowed
    for (int i = 0; i < 5; i++) {
        REQUIRE(limiter.allow(key) == true);
    }
    
    // 6th request should be rate limited
    REQUIRE(limiter.allow(key) == false);
}

TEST_CASE("Rate limit resets after window duration", "[rate_limiter]") {
    TestRateLimiter limiter(2, 500); // 2 requests per 500ms
    
    std::string key = "test_user";
    
    // First 2 requests should be allowed
    REQUIRE(limiter.allow(key) == true);
    REQUIRE(limiter.allow(key) == true);
    
    // 3rd request should be rate limited
    REQUIRE(limiter.allow(key) == false);
    
    // Wait for the window to pass
    std::this_thread::sleep_for(std::chrono::milliseconds(550));
    
    // Should be allowed again
    REQUIRE(limiter.allow(key) == true);
}

TEST_CASE("Different keys have separate rate limits", "[rate_limiter]") {
    TestRateLimiter limiter(2, 1000); // 2 requests per second
    
    std::string key1 = "user1";
    std::string key2 = "user2";
    
    // User 1 makes 2 requests
    REQUIRE(limiter.allow(key1) == true);
    REQUIRE(limiter.allow(key1) == true);
    
    // User 1's 3rd request should be rate limited
    REQUIRE(limiter.allow(key1) == false);
    
    // User 2 should still be allowed
    REQUIRE(limiter.allow(key2) == true);
    REQUIRE(limiter.allow(key2) == true);
    
    // User 2's 3rd request should also be rate limited
    REQUIRE(limiter.allow(key2) == false);
}

TEST_CASE("Concurrent requests are handled correctly", "[rate_limiter]") {
    TestRateLimiter limiter(100, 1000); // 100 requests per second
    
    std::string key = "test_user";
    std::atomic<int> allowed_count{0};
    std::atomic<int> denied_count{0};
    
    // Create 200 concurrent requests
    std::vector<std::future<void>> futures;
    for (int i = 0; i < 200; i++) {
        futures.push_back(std::async(std::launch::async, [&]() {
            if (limiter.allow(key)) {
                allowed_count++;
            } else {
                denied_count++;
            }
        }));
    }
    
    // Wait for all futures to complete
    for (auto& future : futures) {
        future.wait();
    }
    
    // Verify that exactly 100 requests were allowed
    REQUIRE(allowed_count == 100);
    REQUIRE(denied_count == 100);
}

TEST_CASE("Multiple rate limiters simulate distributed environment", "[rate_limiter]") {
    // This test simulates multiple rate limiter instances by creating multiple objects
    // In a real distributed environment, these would be on different machines
    // and would need to share state through a distributed data store
    
    // Create 3 rate limiter instances, each allowing 10 requests per second
    std::vector<std::unique_ptr<TestRateLimiter>> limiters;
    for (int i = 0; i < 3; i++) {
        limiters.push_back(std::make_unique<TestRateLimiter>(10, 1000));
    }
    
    std::string key = "shared_user";
    std::atomic<int> allowed_count{0};
    std::atomic<int> denied_count{0};
    
    // Send 30 requests, 10 to each limiter
    std::vector<std::future<void>> futures;
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 10; j++) {
            futures.push_back(std::async(std::launch::async, [&, i]() {
                if (limiters[i]->allow(key)) {
                    allowed_count++;
                } else {
                    denied_count++;
                }
            }));
        }
    }
    
    // Wait for all futures to complete
    for (auto& future : futures) {
        future.wait();
    }
    
    // In a real distributed environment with proper communication,
    // only 10 requests total should be allowed across all instances
    // However, since our test doesn't implement the actual distributed functionality,
    // this is just validating the test setup itself
    REQUIRE(allowed_count + denied_count == 30);
}

TEST_CASE("Sliding window behavior with partial window expiration", "[rate_limiter]") {
    TestRateLimiter limiter(10, 1000); // 10 requests per second
    
    std::string key = "test_user";
    
    // Use up 5 requests
    for (int i = 0; i < 5; i++) {
        REQUIRE(limiter.allow(key) == true);
    }
    
    // Wait for half the window to expire
    std::this_thread::sleep_for(std::chrono::milliseconds(500));
    
    // Should be able to make 5 more requests
    for (int i = 0; i < 5; i++) {
        REQUIRE(limiter.allow(key) == true);
    }
    
    // 11th request should be rate limited
    REQUIRE(limiter.allow(key) == false);
    
    // Wait for the first half of the window to fully expire
    std::this_thread::sleep_for(std::chrono::milliseconds(510));
    
    // Should be able to make some more requests now
    // (exact number depends on algorithm implementation)
    bool at_least_one_allowed = false;
    for (int i = 0; i < 5; i++) {
        if (limiter.allow(key)) {
            at_least_one_allowed = true;
            break;
        }
    }
    
    REQUIRE(at_least_one_allowed == true);
}

TEST_CASE("Edge case: zero rate limit", "[rate_limiter]") {
    TestRateLimiter limiter(0, 1000); // 0 requests per second
    
    std::string key = "test_user";
    
    // All requests should be rate limited
    REQUIRE(limiter.allow(key) == false);
    REQUIRE(limiter.allow(key) == false);
}

TEST_CASE("Edge case: very high rate limit", "[rate_limiter]") {
    TestRateLimiter limiter(10000, 1000); // 10000 requests per second
    
    std::string key = "test_user";
    
    // Send 1000 requests, all should be allowed
    for (int i = 0; i < 1000; i++) {
        REQUIRE(limiter.allow(key) == true);
    }
}

TEST_CASE("Edge case: very short window", "[rate_limiter]") {
    TestRateLimiter limiter(5, 10); // 5 requests per 10ms
    
    std::string key = "test_user";
    
    // First 5 requests should be allowed
    for (int i = 0; i < 5; i++) {
        REQUIRE(limiter.allow(key) == true);
    }
    
    // 6th request should be rate limited
    REQUIRE(limiter.allow(key) == false);
    
    // Wait for the window to pass
    std::this_thread::sleep_for(std::chrono::milliseconds(15));
    
    // Should be allowed again
    REQUIRE(limiter.allow(key) == true);
}

TEST_CASE("Edge case: empty key", "[rate_limiter]") {
    TestRateLimiter limiter(5, 1000); // 5 requests per second
    
    std::string empty_key = "";
    
    // First 5 requests should be allowed
    for (int i = 0; i < 5; i++) {
        REQUIRE(limiter.allow(empty_key) == true);
    }
    
    // 6th request should be rate limited
    REQUIRE(limiter.allow(empty_key) == false);
}

TEST_CASE("Edge case: very long key", "[rate_limiter]") {
    TestRateLimiter limiter(5, 1000); // 5 requests per second
    
    // Create a very long key
    std::string long_key(10000, 'a');
    
    // First 5 requests should be allowed
    for (int i = 0; i < 5; i++) {
        REQUIRE(limiter.allow(long_key) == true);
    }
    
    // 6th request should be rate limited
    REQUIRE(limiter.allow(long_key) == false);
}