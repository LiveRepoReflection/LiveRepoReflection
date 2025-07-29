#include "social_reach.h"
#include "catch.hpp"
#include <set>
#include <vector>
#include <string>
#include <functional>
#include <map>
#include <tuple>
#include <iostream>

// Mock network data for testing
class MockNetwork {
public:
    // Add a directed connection from -> to
    void addConnection(int from, int to) {
        network[from].followees.push_back(to);
        network[to].followers.push_back(from);
    }
    
    // Get network data for specific user
    std::tuple<std::vector<int>, std::vector<int>, std::vector<std::string>> getData(int userID) {
        callCount++;
        
        // If user doesn't exist, return empty data
        if (network.find(userID) == network.end()) {
            return std::make_tuple(std::vector<int>{}, std::vector<int>{}, std::vector<std::string>{});
        }
        
        return std::make_tuple(
            network[userID].followers,
            network[userID].followees,
            network[userID].content
        );
    }
    
    // Reset call counter
    void resetCounter() {
        callCount = 0;
    }
    
    // Get number of API calls made
    int getCallCount() const {
        return callCount;
    }
    
    // Add content to user
    void addContent(int userID, const std::string& content) {
        network[userID].content.push_back(content);
    }

private:
    struct UserData {
        std::vector<int> followers;
        std::vector<int> followees;
        std::vector<std::string> content;
    };
    
    std::map<int, UserData> network;
    int callCount = 0;
};

TEST_CASE("Simple network with no cycles") {
    MockNetwork mockNetwork;
    
    // User 1 follows User 2 and 3
    mockNetwork.addConnection(1, 2);
    mockNetwork.addConnection(1, 3);
    
    // User 2 follows User 4
    mockNetwork.addConnection(2, 4);
    
    // User 3 follows User 5
    mockNetwork.addConnection(3, 5);
    
    auto networkData = [&mockNetwork](int userID) {
        return mockNetwork.getData(userID);
    };
    
    SECTION("k = 0: Only starting user") {
        mockNetwork.resetCounter();
        std::set<int> result = socialReachKHop(1, 0, networkData);
        REQUIRE(result == std::set<int>{1});
        // Verify minimal API calls
        REQUIRE(mockNetwork.getCallCount() <= 1);
    }
    
    SECTION("k = 1: Direct connections") {
        mockNetwork.resetCounter();
        std::set<int> result = socialReachKHop(1, 1, networkData);
        REQUIRE(result == std::set<int>{1, 2, 3});
        // Verify minimal API calls
        REQUIRE(mockNetwork.getCallCount() <= 3);
    }
    
    SECTION("k = 2: Two-hop connections") {
        mockNetwork.resetCounter();
        std::set<int> result = socialReachKHop(1, 2, networkData);
        REQUIRE(result == std::set<int>{1, 2, 3, 4, 5});
        // Verify minimal API calls
        REQUIRE(mockNetwork.getCallCount() <= 5);
    }
    
    SECTION("Different starting node") {
        mockNetwork.resetCounter();
        std::set<int> result = socialReachKHop(3, 1, networkData);
        REQUIRE(result == std::set<int>{3, 5});
        // Verify minimal API calls
        REQUIRE(mockNetwork.getCallCount() <= 2);
    }
}

TEST_CASE("Network with cycles") {
    MockNetwork mockNetwork;
    
    // Create a cycle: 1 -> 2 -> 3 -> 1
    mockNetwork.addConnection(1, 2);
    mockNetwork.addConnection(2, 3);
    mockNetwork.addConnection(3, 1);
    
    // Add additional connections
    mockNetwork.addConnection(3, 4);
    mockNetwork.addConnection(4, 5);
    
    auto networkData = [&mockNetwork](int userID) {
        return mockNetwork.getData(userID);
    };
    
    SECTION("k = 1: Direct connections with cycle") {
        mockNetwork.resetCounter();
        std::set<int> result = socialReachKHop(1, 1, networkData);
        REQUIRE(result == std::set<int>{1, 2});
        // Verify minimal API calls
        REQUIRE(mockNetwork.getCallCount() <= 2);
    }
    
    SECTION("k = 2: Two-hop connections with cycle") {
        mockNetwork.resetCounter();
        std::set<int> result = socialReachKHop(1, 2, networkData);
        REQUIRE(result == std::set<int>{1, 2, 3});
        // Verify minimal API calls
        REQUIRE(mockNetwork.getCallCount() <= 3);
    }
    
    SECTION("k = 3: Three-hop connections with cycle") {
        mockNetwork.resetCounter();
        std::set<int> result = socialReachKHop(1, 3, networkData);
        REQUIRE(result == std::set<int>{1, 2, 3, 4});
        // Verify minimal API calls
        REQUIRE(mockNetwork.getCallCount() <= 4);
    }
    
    SECTION("k = 4: Four-hop connections with cycle") {
        mockNetwork.resetCounter();
        std::set<int> result = socialReachKHop(1, 4, networkData);
        REQUIRE(result == std::set<int>{1, 2, 3, 4, 5});
        // Verify minimal API calls
        REQUIRE(mockNetwork.getCallCount() <= 5);
    }
}

TEST_CASE("Complex network with multiple paths") {
    MockNetwork mockNetwork;
    
    // Create a more complex network
    // 1 -> 2 -> 3
    // |    |    |
    // v    v    v
    // 4 -> 5 -> 6
    mockNetwork.addConnection(1, 2);
    mockNetwork.addConnection(1, 4);
    mockNetwork.addConnection(2, 3);
    mockNetwork.addConnection(2, 5);
    mockNetwork.addConnection(3, 6);
    mockNetwork.addConnection(4, 5);
    mockNetwork.addConnection(5, 6);
    
    auto networkData = [&mockNetwork](int userID) {
        return mockNetwork.getData(userID);
    };
    
    SECTION("k = 1: Direct connections") {
        mockNetwork.resetCounter();
        std::set<int> result = socialReachKHop(1, 1, networkData);
        REQUIRE(result == std::set<int>{1, 2, 4});
        // Verify minimal API calls
        REQUIRE(mockNetwork.getCallCount() <= 3);
    }
    
    SECTION("k = 2: Two-hop connections") {
        mockNetwork.resetCounter();
        std::set<int> result = socialReachKHop(1, 2, networkData);
        REQUIRE(result == std::set<int>{1, 2, 3, 4, 5});
        // Verify minimal API calls
        REQUIRE(mockNetwork.getCallCount() <= 5);
    }
    
    SECTION("k = 3: Three-hop connections") {
        mockNetwork.resetCounter();
        std::set<int> result = socialReachKHop(1, 3, networkData);
        REQUIRE(result == std::set<int>{1, 2, 3, 4, 5, 6});
        // Verify minimal API calls
        REQUIRE(mockNetwork.getCallCount() <= 7);
    }
}

TEST_CASE("Edge cases") {
    MockNetwork mockNetwork;
    
    // Create a simple network
    mockNetwork.addConnection(1, 2);
    mockNetwork.addConnection(2, 3);
    
    auto networkData = [&mockNetwork](int userID) {
        return mockNetwork.getData(userID);
    };
    
    SECTION("Isolated user") {
        mockNetwork.resetCounter();
        std::set<int> result = socialReachKHop(4, 3, networkData);
        REQUIRE(result == std::set<int>{4});
        // Verify minimal API calls
        REQUIRE(mockNetwork.getCallCount() <= 1);
    }
    
    SECTION("Non-existent user") {
        mockNetwork.resetCounter();
        std::set<int> result = socialReachKHop(99, 2, networkData);
        REQUIRE(result == std::set<int>{99});
        // Verify minimal API calls
        REQUIRE(mockNetwork.getCallCount() <= 1);
    }
    
    SECTION("Large k value") {
        mockNetwork.resetCounter();
        std::set<int> result = socialReachKHop(1, 100, networkData);
        REQUIRE(result == std::set<int>{1, 2, 3});
        // Verify minimal API calls - we should only need to explore each node once
        REQUIRE(mockNetwork.getCallCount() <= 3);
    }
}

TEST_CASE("Performance test - larger network") {
    MockNetwork mockNetwork;
    
    // Create a larger network
    for (int i = 1; i <= 20; ++i) {
        for (int j = 1; j <= 3; ++j) {
            int target = (i * j) % 20 + 1;
            if (target != i) {
                mockNetwork.addConnection(i, target);
            }
        }
    }
    
    auto networkData = [&mockNetwork](int userID) {
        return mockNetwork.getData(userID);
    };
    
    SECTION("Larger network with k = 3") {
        mockNetwork.resetCounter();
        std::set<int> result = socialReachKHop(1, 3, networkData);
        // Don't check specific result, just ensure it completes and call count is reasonable
        REQUIRE(!result.empty());
        // We should visit each node at most once
        REQUIRE(mockNetwork.getCallCount() <= 20);
    }
}