#include "dynamic_balancer.h"
#include "catch.hpp"
#include <stdexcept>
#include <set>
#include <string>

TEST_CASE("No backend servers available", "[dynamic_balancer]") {
    dynamic_balancer::LoadBalancer lb;
    lb.setShardingKey("user_id");
    dynamic_balancer::Request req{"user42"};
    // Expect an exception when routing request with no backend servers configured.
    REQUIRE_THROWS_AS(lb.routeRequest(req), std::runtime_error);
}

TEST_CASE("Single backend routing", "[dynamic_balancer]") {
    dynamic_balancer::LoadBalancer lb;
    lb.setShardingKey("user_id");
    lb.addBackend("server1", 1);
    dynamic_balancer::Request req{"user42"};
    std::string routed = lb.routeRequest(req);
    REQUIRE(routed == "server1");
}

TEST_CASE("Multiple backend round-robin routing", "[dynamic_balancer]") {
    dynamic_balancer::LoadBalancer lb;
    lb.setShardingKey("session");
    lb.addBackend("server1", 1);
    lb.addBackend("server2", 1);

    int count1 = 0, count2 = 0;
    // Simulate multiple requests to check distribution across servers.
    for (int i = 0; i < 100; ++i) {
        dynamic_balancer::Request req{"session" + std::to_string(i)};
        std::string server = lb.routeRequest(req);
        if (server == "server1") {
            ++count1;
        } else if (server == "server2") {
            ++count2;
        } else {
            FAIL("Unknown server returned");
        }
    }
    REQUIRE(count1 > 0);
    REQUIRE(count2 > 0);
}

TEST_CASE("Dynamic backend removal", "[dynamic_balancer]") {
    dynamic_balancer::LoadBalancer lb;
    lb.setShardingKey("location");
    lb.addBackend("server1", 1);
    lb.addBackend("server2", 1);

    dynamic_balancer::Request req{"loc123"};
    std::string initialServer = lb.routeRequest(req);
    lb.removeBackend(initialServer);

    // After removal, the routed server should not be the one that was removed.
    for (int i = 0; i < 10; ++i) {
        std::string routed = lb.routeRequest(req);
        REQUIRE(routed != initialServer);
    }
}

TEST_CASE("Health monitoring: mark backend unhealthy", "[dynamic_balancer]") {
    dynamic_balancer::LoadBalancer lb;
    lb.setShardingKey("product");
    lb.addBackend("server1", 1);
    lb.addBackend("server2", 1);

    // Confirm both backends are used initially.
    std::set<std::string> servers;
    for (int i = 0; i < 20; ++i) {
        dynamic_balancer::Request req{"prod" + std::to_string(i)};
        servers.insert(lb.routeRequest(req));
    }
    REQUIRE(servers.size() == 2);

    // Mark 'server1' as unhealthy.
    lb.updateHealth("server1", false);
    for (int i = 0; i < 20; ++i) {
        dynamic_balancer::Request req{"prod" + std::to_string(i)};
        std::string server = lb.routeRequest(req);
        REQUIRE(server == "server2");
    }

    // Restore health to 'server1' and test that both servers are available again.
    lb.updateHealth("server1", true);
    servers.clear();
    for (int i = 0; i < 20; ++i) {
        dynamic_balancer::Request req{"prod" + std::to_string(i)};
        servers.insert(lb.routeRequest(req));
    }
    REQUIRE(servers.size() == 2);
}

TEST_CASE("Dynamic sharding rule update", "[dynamic_balancer]") {
    dynamic_balancer::LoadBalancer lb;
    lb.setShardingKey("user_id");
    lb.addBackend("server1", 1);
    lb.addBackend("server2", 1);

    dynamic_balancer::Request req1{"user_a"};
    dynamic_balancer::Request req2{"user_b"};
    
    std::string serverBefore1 = lb.routeRequest(req1);
    std::string serverBefore2 = lb.routeRequest(req2);
    REQUIRE((serverBefore1 == "server1" || serverBefore1 == "server2"));
    REQUIRE((serverBefore2 == "server1" || serverBefore2 == "server2"));

    // Update the sharding rule to use a different algorithm.
    dynamic_balancer::ShardingRule newRule;
    newRule.algorithm = "consistent_hashing";
    lb.updateShardingRule(newRule);

    // After sharding rule update, routing might change.
    std::string serverAfter1 = lb.routeRequest(req1);
    std::string serverAfter2 = lb.routeRequest(req2);
    REQUIRE((serverAfter1 == "server1" || serverAfter1 == "server2"));
    REQUIRE((serverAfter2 == "server1" || serverAfter2 == "server2"));
}