#include "catch.hpp"
#include "load_balancer.h"
#include <vector>

TEST_CASE("Load balancer distributes requests correctly") {
    SECTION("Basic distribution test") {
        std::vector<int> server_capacities = {10, 20, 30};
        std::vector<int> requests = {5, 5, 5, 5, 5, 5, 5, 5, 5, 5}; // 10 requests of priority 5
        
        std::vector<int> distribution = load_balancer::distribute_load(server_capacities, requests);
        
        REQUIRE(distribution.size() == 3);
        REQUIRE(distribution[0] + distribution[1] + distribution[2] == 10);
        REQUIRE(distribution[0] <= 10);
        REQUIRE(distribution[1] <= 20);
        REQUIRE(distribution[2] <= 30);
    }
    
    SECTION("Priority handling test") {
        std::vector<int> server_capacities = {5, 5, 5};
        std::vector<int> requests = {1, 1, 1, 5, 5, 5, 10, 10, 10, 10}; // Mixed priorities
        
        std::vector<int> distribution = load_balancer::distribute_load(server_capacities, requests);
        
        REQUIRE(distribution.size() == 3);
        int total_distributed = distribution[0] + distribution[1] + distribution[2];
        REQUIRE(total_distributed <= 15); // Total capacity is 15
        REQUIRE(total_distributed >= 7); // At least all high priority (10) requests and some medium priority should be handled
    }
    
    SECTION("Server at capacity test") {
        std::vector<int> server_capacities = {3, 3, 3};
        std::vector<int> requests = {5, 5, 5, 5, 5, 5, 5, 5, 5, 5}; // 10 requests of priority 5
        
        std::vector<int> distribution = load_balancer::distribute_load(server_capacities, requests);
        
        REQUIRE(distribution.size() == 3);
        REQUIRE(distribution[0] + distribution[1] + distribution[2] == 9); // Total capacity is 9
        REQUIRE(distribution[0] <= 3);
        REQUIRE(distribution[1] <= 3);
        REQUIRE(distribution[2] <= 3);
    }
    
    SECTION("Server failure test") {
        std::vector<int> server_capacities = {0, 10, 20};
        std::vector<int> requests = {5, 5, 5, 5, 5, 5, 5, 5, 5, 5}; // 10 requests of priority 5
        
        std::vector<int> distribution = load_balancer::distribute_load(server_capacities, requests);
        
        REQUIRE(distribution.size() == 3);
        REQUIRE(distribution[0] == 0); // Failed server should get no requests
        REQUIRE(distribution[1] + distribution[2] == 10);
        REQUIRE(distribution[1] <= 10);
        REQUIRE(distribution[2] <= 20);
    }
    
    SECTION("All servers failed test") {
        std::vector<int> server_capacities = {0, 0, 0};
        std::vector<int> requests = {5, 5, 5, 5, 5};
        
        std::vector<int> distribution = load_balancer::distribute_load(server_capacities, requests);
        
        REQUIRE(distribution.size() == 3);
        REQUIRE(distribution[0] == 0);
        REQUIRE(distribution[1] == 0);
        REQUIRE(distribution[2] == 0);
    }
    
    SECTION("No requests test") {
        std::vector<int> server_capacities = {10, 20, 30};
        std::vector<int> requests = {};
        
        std::vector<int> distribution = load_balancer::distribute_load(server_capacities, requests);
        
        REQUIRE(distribution.size() == 3);
        REQUIRE(distribution[0] == 0);
        REQUIRE(distribution[1] == 0);
        REQUIRE(distribution[2] == 0);
    }
    
    SECTION("Insufficient capacity test") {
        std::vector<int> server_capacities = {2, 3, 4};
        std::vector<int> requests = {10, 10, 10, 5, 5, 5, 1, 1, 1, 1}; // 4 high, 3 medium, 3 low priority
        
        std::vector<int> distribution = load_balancer::distribute_load(server_capacities, requests);
        
        REQUIRE(distribution.size() == 3);
        int total_distributed = distribution[0] + distribution[1] + distribution[2];
        REQUIRE(total_distributed == 9); // All servers at capacity
        // Can't test exact distribution as it depends on implementation, but high priority should be preferred
    }
    
    SECTION("Different server capacities test") {
        std::vector<int> server_capacities = {50, 100, 200};
        std::vector<int> requests(300, 5); // 300 requests of priority 5
        
        std::vector<int> distribution = load_balancer::distribute_load(server_capacities, requests);
        
        REQUIRE(distribution.size() == 3);
        REQUIRE(distribution[0] + distribution[1] + distribution[2] == 300);
        REQUIRE(distribution[0] <= 50);
        REQUIRE(distribution[1] <= 100);
        REQUIRE(distribution[2] <= 200);
    }
    
    SECTION("Large number of servers test") {
        std::vector<int> server_capacities(100, 10); // 100 servers with capacity 10 each
        std::vector<int> requests(500, 5); // 500 requests of priority 5
        
        std::vector<int> distribution = load_balancer::distribute_load(server_capacities, requests);
        
        REQUIRE(distribution.size() == 100);
        int total_distributed = 0;
        for (int i = 0; i < 100; i++) {
            REQUIRE(distribution[i] <= 10);
            total_distributed += distribution[i];
        }
        REQUIRE(total_distributed == 500);
    }
    
    SECTION("Various priority levels test") {
        std::vector<int> server_capacities = {10, 10, 10};
        std::vector<int> requests;
        for (int i = 1; i <= 10; i++) {
            for (int j = 0; j < 3; j++) {
                requests.push_back(i); // 3 requests of each priority level
            }
        }
        
        std::vector<int> distribution = load_balancer::distribute_load(server_capacities, requests);
        
        REQUIRE(distribution.size() == 3);
        REQUIRE(distribution[0] + distribution[1] + distribution[2] == 30);
        REQUIRE(distribution[0] <= 10);
        REQUIRE(distribution[1] <= 10);
        REQUIRE(distribution[2] <= 10);
    }
    
    SECTION("Capacity change test") {
        // First distribution
        std::vector<int> server_capacities = {10, 10, 10};
        std::vector<int> requests(25, 5); // 25 requests of priority 5
        
        std::vector<int> distribution1 = load_balancer::distribute_load(server_capacities, requests);
        
        REQUIRE(distribution1.size() == 3);
        REQUIRE(distribution1[0] + distribution1[1] + distribution1[2] == 25);
        
        // Change capacity and redistribute
        server_capacities = {5, 15, 10};
        std::vector<int> distribution2 = load_balancer::distribute_load(server_capacities, requests);
        
        REQUIRE(distribution2.size() == 3);
        REQUIRE(distribution2[0] + distribution2[1] + distribution2[2] == 25);
        REQUIRE(distribution2[0] <= 5);
        REQUIRE(distribution2[1] <= 15);
        REQUIRE(distribution2[2] <= 10);
    }
}