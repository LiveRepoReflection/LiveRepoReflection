#include "route_optimizer.h"
#include "catch.hpp"
#include <vector>
#include <tuple>

TEST_CASE("Simple direct route", "[basic]") {
    std::vector<int> locations = {0, 1};
    std::vector<std::tuple<int, int, std::string, double, double>> edges = {
        {0, 1, "truck", 10.0, 1.0}
    };
    std::vector<std::tuple<int, std::string, std::string, double>> transfers = {};
    
    REQUIRE(route_optimizer::find_minimum_time(locations, edges, transfers, 0, 1) == 10.0);
}

TEST_CASE("Route with one transfer", "[transfer]") {
    std::vector<int> locations = {0, 1, 2};
    std::vector<std::tuple<int, int, std::string, double, double>> edges = {
        {0, 1, "truck", 10.0, 1.0},
        {1, 2, "train", 20.0, 0.5}
    };
    std::vector<std::tuple<int, std::string, std::string, double>> transfers = {
        {1, "truck", "train", 2.0}
    };
    
    REQUIRE(route_optimizer::find_minimum_time(locations, edges, transfers, 0, 2) == 22.0);
}

TEST_CASE("Multiple possible routes", "[multiple_routes]") {
    std::vector<int> locations = {0, 1, 2};
    std::vector<std::tuple<int, int, std::string, double, double>> edges = {
        {0, 2, "airplane", 100.0, 0.2},
        {0, 1, "truck", 10.0, 1.0},
        {1, 2, "train", 20.0, 0.5}
    };
    std::vector<std::tuple<int, std::string, std::string, double>> transfers = {
        {1, "truck", "train", 2.0}
    };
    
    REQUIRE(route_optimizer::find_minimum_time(locations, edges, transfers, 0, 2) == 20.0);
}

TEST_CASE("Same start and destination", "[edge_case]") {
    std::vector<int> locations = {0};
    std::vector<std::tuple<int, int, std::string, double, double>> edges = {};
    std::vector<std::tuple<int, std::string, std::string, double>> transfers = {};
    
    REQUIRE(route_optimizer::find_minimum_time(locations, edges, transfers, 0, 0) == 0.0);
}

TEST_CASE("No possible route", "[edge_case]") {
    std::vector<int> locations = {0, 1};
    std::vector<std::tuple<int, int, std::string, double, double>> edges = {};
    std::vector<std::tuple<int, std::string, std::string, double>> transfers = {};
    
    REQUIRE(route_optimizer::find_minimum_time(locations, edges, transfers, 0, 1) == -1.0);
}

TEST_CASE("Complex network with multiple transfers", "[complex]") {
    std::vector<int> locations = {0, 1, 2, 3, 4};
    std::vector<std::tuple<int, int, std::string, double, double>> edges = {
        {0, 1, "truck", 10.0, 1.0},
        {1, 2, "train", 20.0, 0.5},
        {2, 3, "ship", 30.0, 0.3},
        {3, 4, "airplane", 40.0, 0.2},
        {0, 4, "airplane", 100.0, 0.2},
        {1, 4, "train", 80.0, 0.5}
    };
    std::vector<std::tuple<int, std::string, std::string, double>> transfers = {
        {1, "truck", "train", 2.0},
        {2, "train", "ship", 3.0},
        {3, "ship", "airplane", 4.0}
    };
    
    REQUIRE(route_optimizer::find_minimum_time(locations, edges, transfers, 0, 4) == 20.0);
}

TEST_CASE("Cycle in graph", "[cycle]") {
    std::vector<int> locations = {0, 1, 2};
    std::vector<std::tuple<int, int, std::string, double, double>> edges = {
        {0, 1, "truck", 10.0, 1.0},
        {1, 2, "train", 20.0, 0.5},
        {2, 0, "ship", 30.0, 0.3}
    };
    std::vector<std::tuple<int, std::string, std::string, double>> transfers = {
        {1, "truck", "train", 2.0},
        {2, "train", "ship", 3.0},
        {0, "ship", "truck", 4.0}
    };
    
    REQUIRE(route_optimizer::find_minimum_time(locations, edges, transfers, 0, 2) == 22.0);
}

TEST_CASE("Multiple edges between same nodes", "[multiple_edges]") {
    std::vector<int> locations = {0, 1};
    std::vector<std::tuple<int, int, std::string, double, double>> edges = {
        {0, 1, "truck", 10.0, 1.0},
        {0, 1, "train", 15.0, 0.5},
        {0, 1, "airplane", 20.0, 0.2}
    };
    std::vector<std::tuple<int, std::string, std::string, double>> transfers = {};
    
    REQUIRE(route_optimizer::find_minimum_time(locations, edges, transfers, 0, 1) == 4.0);
}

TEST_CASE("Large network stress test", "[stress]") {
    std::vector<int> locations;
    std::vector<std::tuple<int, int, std::string, double, double>> edges;
    std::vector<std::tuple<int, std::string, std::string, double>> transfers;
    
    // Generate 1000 locations
    for (int i = 0; i < 1000; i++) {
        locations.push_back(i);
    }
    
    // Generate 10000 random edges
    for (int i = 0; i < 10000; i++) {
        int source = i % 1000;
        int dest = (i + 1) % 1000;
        edges.push_back({source, dest, "truck", 10.0, 1.0});
    }
    
    // Generate 500 transfers
    for (int i = 0; i < 500; i++) {
        transfers.push_back({i, "truck", "train", 2.0});
    }
    
    double result = route_optimizer::find_minimum_time(locations, edges, transfers, 0, 999);
    REQUIRE(result >= 0.0);
}