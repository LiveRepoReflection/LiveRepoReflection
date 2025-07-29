#include "tenant_rate_limit.h"
#include "catch.hpp"
#include <thread>
#include <vector>
#include <chrono>

TEST_CASE("Basic rate limiting for single tenant") {
    RateLimiter limiter;
    const std::string tenantId = "tenant1";
    limiter.configureTenant(tenantId, 5, 1); // 5 requests per 1 second

    SECTION("Allow requests within limit") {
        for (int i = 0; i < 5; i++) {
            REQUIRE(limiter.isAllowed(tenantId) == true);
        }
        REQUIRE(limiter.isAllowed(tenantId) == false);
    }

    SECTION("Reset after time window") {
        for (int i = 0; i < 5; i++) {
            REQUIRE(limiter.isAllowed(tenantId) == true);
        }
        REQUIRE(limiter.isAllowed(tenantId) == false);
        
        std::this_thread::sleep_for(std::chrono::seconds(1));
        REQUIRE(limiter.isAllowed(tenantId) == true);
    }
}

TEST_CASE("Multiple tenants with different limits") {
    RateLimiter limiter;
    limiter.configureTenant("tenant1", 3, 1);  // 3 requests per second
    limiter.configureTenant("tenant2", 5, 1);  // 5 requests per second

    SECTION("Independent rate limits") {
        for (int i = 0; i < 3; i++) {
            REQUIRE(limiter.isAllowed("tenant1") == true);
        }
        REQUIRE(limiter.isAllowed("tenant1") == false);

        for (int i = 0; i < 5; i++) {
            REQUIRE(limiter.isAllowed("tenant2") == true);
        }
        REQUIRE(limiter.isAllowed("tenant2") == false);
    }
}

TEST_CASE("Dynamic configuration updates") {
    RateLimiter limiter;
    const std::string tenantId = "tenant1";
    
    SECTION("Update rate limit") {
        limiter.configureTenant(tenantId, 3, 1);
        for (int i = 0; i < 3; i++) {
            REQUIRE(limiter.isAllowed(tenantId) == true);
        }
        REQUIRE(limiter.isAllowed(tenantId) == false);

        limiter.configureTenant(tenantId, 5, 1);
        for (int i = 0; i < 2; i++) {
            REQUIRE(limiter.isAllowed(tenantId) == true);
        }
    }
}

TEST_CASE("Concurrent requests") {
    RateLimiter limiter;
    const std::string tenantId = "tenant1";
    limiter.configureTenant(tenantId, 1000, 1);

    SECTION("Multiple threads") {
        std::vector<std::thread> threads;
        std::atomic<int> successCount(0);

        for (int i = 0; i < 1200; i++) {
            threads.emplace_back([&limiter, &successCount, tenantId]() {
                if (limiter.isAllowed(tenantId)) {
                    successCount++;
                }
            });
        }

        for (auto& thread : threads) {
            thread.join();
        }

        REQUIRE(successCount == 1000);
    }
}

TEST_CASE("Edge cases") {
    RateLimiter limiter;

    SECTION("Invalid tenant configuration") {
        REQUIRE_THROWS(limiter.configureTenant("tenant1", 0, 1));
        REQUIRE_THROWS(limiter.configureTenant("tenant1", -1, 1));
        REQUIRE_THROWS(limiter.configureTenant("tenant1", 1, 0));
        REQUIRE_THROWS(limiter.configureTenant("tenant1", 1, -1));
    }

    SECTION("Unconfigured tenant") {
        REQUIRE_THROWS(limiter.isAllowed("nonexistent"));
    }

    SECTION("Empty tenant ID") {
        REQUIRE_THROWS(limiter.configureTenant("", 1, 1));
        REQUIRE_THROWS(limiter.isAllowed(""));
    }
}

TEST_CASE("Memory limit test") {
    RateLimiter limiter;
    
    SECTION("Large number of tenants") {
        for (int i = 0; i < 1000000; i++) {
            std::string tenantId = "tenant" + std::to_string(i);
            limiter.configureTenant(tenantId, 10, 1);
            REQUIRE(limiter.isAllowed(tenantId) == true);
        }
    }
}

TEST_CASE("Different time windows") {
    RateLimiter limiter;
    const std::string tenantId = "tenant1";
    
    SECTION("Very short window") {
        limiter.configureTenant(tenantId, 3, 1);
        for (int i = 0; i < 3; i++) {
            REQUIRE(limiter.isAllowed(tenantId) == true);
        }
        std::this_thread::sleep_for(std::chrono::seconds(1));
        REQUIRE(limiter.isAllowed(tenantId) == true);
    }

    SECTION("Longer window") {
        limiter.configureTenant(tenantId, 10, 5);
        for (int i = 0; i < 10; i++) {
            REQUIRE(limiter.isAllowed(tenantId) == true);
        }
        REQUIRE(limiter.isAllowed(tenantId) == false);
        std::this_thread::sleep_for(std::chrono::seconds(5));
        REQUIRE(limiter.isAllowed(tenantId) == true);
    }
}