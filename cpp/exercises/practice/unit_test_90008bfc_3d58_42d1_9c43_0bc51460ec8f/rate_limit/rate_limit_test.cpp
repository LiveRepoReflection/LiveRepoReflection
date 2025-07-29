#include "rate_limit.h"
#include "catch.hpp"
#include <thread>
#include <vector>
#include <chrono>

TEST_CASE("Basic rate limiting") {
    SECTION("Single client, single resource") {
        RateLimiter limiter;
        std::string clientId = "client1";
        std::string resourceId = "resource1";
        
        // First request should be allowed
        REQUIRE(limiter.allowRequest(clientId, resourceId) == true);
        
        // Subsequent requests within the same second should be denied
        for(int i = 0; i < 10; i++) {
            REQUIRE(limiter.allowRequest(clientId, resourceId) == false);
        }
        
        // After waiting, new requests should be allowed
        std::this_thread::sleep_for(std::chrono::seconds(1));
        REQUIRE(limiter.allowRequest(clientId, resourceId) == true);
    }
}

TEST_CASE("Multiple clients") {
    RateLimiter limiter;
    std::vector<std::string> clients = {"client1", "client2", "client3"};
    std::string resourceId = "resource1";
    
    SECTION("Different clients should have independent rate limits") {
        for(const auto& client : clients) {
            REQUIRE(limiter.allowRequest(client, resourceId) == true);
        }
        
        // Second request from each client should be denied
        for(const auto& client : clients) {
            REQUIRE(limiter.allowRequest(client, resourceId) == false);
        }
    }
}

TEST_CASE("Multiple resources") {
    RateLimiter limiter;
    std::string clientId = "client1";
    std::vector<std::string> resources = {"resource1", "resource2", "resource3"};
    
    SECTION("Different resources should have independent rate limits") {
        for(const auto& resource : resources) {
            REQUIRE(limiter.allowRequest(clientId, resource) == true);
        }
        
        // Second request for each resource should be denied
        for(const auto& resource : resources) {
            REQUIRE(limiter.allowRequest(clientId, resource) == false);
        }
    }
}

TEST_CASE("Concurrent requests") {
    RateLimiter limiter;
    std::string clientId = "client1";
    std::string resourceId = "resource1";
    
    SECTION("Multiple concurrent requests should be handled correctly") {
        const int numThreads = 10;
        std::vector<std::thread> threads;
        std::vector<bool> results(numThreads);
        
        for(int i = 0; i < numThreads; i++) {
            threads.emplace_back([&limiter, &results, i, &clientId, &resourceId]() {
                results[i] = limiter.allowRequest(clientId, resourceId);
            });
        }
        
        for(auto& thread : threads) {
            thread.join();
        }
        
        // Only one request should be allowed
        int allowedCount = 0;
        for(bool result : results) {
            if(result) allowedCount++;
        }
        REQUIRE(allowedCount == 1);
    }
}

TEST_CASE("Edge cases") {
    RateLimiter limiter;
    
    SECTION("Empty client ID") {
        REQUIRE_THROWS_AS(limiter.allowRequest("", "resource1"), std::invalid_argument);
    }
    
    SECTION("Empty resource ID") {
        REQUIRE_THROWS_AS(limiter.allowRequest("client1", ""), std::invalid_argument);
    }
    
    SECTION("Very long IDs") {
        std::string longId(1000000, 'a');
        REQUIRE_THROWS_AS(limiter.allowRequest(longId, "resource1"), std::invalid_argument);
        REQUIRE_THROWS_AS(limiter.allowRequest("client1", longId), std::invalid_argument);
    }
}

TEST_CASE("Time-based tests") {
    RateLimiter limiter;
    std::string clientId = "client1";
    std::string resourceId = "resource1";
    
    SECTION("Rate limit reset after time window") {
        REQUIRE(limiter.allowRequest(clientId, resourceId) == true);
        REQUIRE(limiter.allowRequest(clientId, resourceId) == false);
        
        std::this_thread::sleep_for(std::chrono::seconds(2));
        REQUIRE(limiter.allowRequest(clientId, resourceId) == true);
    }
    
    SECTION("Multiple time windows") {
        for(int i = 0; i < 3; i++) {
            REQUIRE(limiter.allowRequest(clientId, resourceId) == true);
            REQUIRE(limiter.allowRequest(clientId, resourceId) == false);
            std::this_thread::sleep_for(std::chrono::seconds(2));
        }
    }
}

TEST_CASE("Performance tests") {
    RateLimiter limiter;
    
    SECTION("High volume of requests") {
        const int numRequests = 100000;
        auto start = std::chrono::high_resolution_clock::now();
        
        for(int i = 0; i < numRequests; i++) {
            std::string clientId = "client" + std::to_string(i % 100);
            std::string resourceId = "resource" + std::to_string(i % 10);
            limiter.allowRequest(clientId, resourceId);
        }
        
        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
        
        // Ensure processing time is reasonable (less than 1ms per request on average)
        REQUIRE(duration.count() < numRequests);
    }
}