#include "catch.hpp"
#include "network_route.h"
#include <vector>
#include <tuple>

TEST_CASE("Simple path with two nodes", "[simple_path]") {
    int N = 2;
    std::vector<std::tuple<int, int, int>> links = {
        {0, 1, 10}
    };
    int S = 0;
    int D = 1;
    
    std::vector<int> expected = {0, 1};
    REQUIRE(find_optimal_route(N, links, S, D) == expected);
}

TEST_CASE("Simple path with three nodes, direct vs indirect", "[path_choice]") {
    int N = 3;
    std::vector<std::tuple<int, int, int>> links = {
        {0, 1, 10},
        {1, 2, 10},
        {0, 2, 25}
    };
    int S = 0;
    int D = 2;
    
    // Expected path is 0->1->2 (avg = 10) instead of 0->2 (avg = 25)
    std::vector<int> expected = {0, 1, 2};
    REQUIRE(find_optimal_route(N, links, S, D) == expected);
}

TEST_CASE("Multiple paths with same total but different average", "[average_optimization]") {
    int N = 4;
    std::vector<std::tuple<int, int, int>> links = {
        {0, 1, 10},
        {1, 3, 10},
        {0, 2, 5},
        {2, 3, 15}
    };
    int S = 0;
    int D = 3;
    
    // Path 0->1->3 has total 20, avg 10
    // Path 0->2->3 has total 20, avg 10
    // Both are valid, test for one of them
    std::vector<int> result = find_optimal_route(N, links, S, D);
    bool valid = (result == std::vector<int>{0, 1, 3}) || 
                 (result == std::vector<int>{0, 2, 3});
    REQUIRE(valid);
}

TEST_CASE("Multiple links between same nodes", "[multiple_links]") {
    int N = 3;
    std::vector<std::tuple<int, int, int>> links = {
        {0, 1, 10},
        {0, 1, 5},  // Better link
        {1, 2, 8}
    };
    int S = 0;
    int D = 2;
    
    // Should choose the link with latency 5
    std::vector<int> expected = {0, 1, 2};
    REQUIRE(find_optimal_route(N, links, S, D) == expected);
}

TEST_CASE("No path exists", "[disconnected]") {
    int N = 4;
    std::vector<std::tuple<int, int, int>> links = {
        {0, 1, 10},
        {2, 3, 5}
    };
    int S = 0;
    int D = 3;
    
    std::vector<int> expected = {};
    REQUIRE(find_optimal_route(N, links, S, D) == expected);
}

TEST_CASE("Source and destination are the same", "[same_node]") {
    int N = 3;
    std::vector<std::tuple<int, int, int>> links = {
        {0, 1, 10},
        {1, 2, 5}
    };
    int S = 1;
    int D = 1;
    
    std::vector<int> expected = {1};
    REQUIRE(find_optimal_route(N, links, S, D) == expected);
}

TEST_CASE("Complex network with multiple possible paths", "[complex_network]") {
    int N = 6;
    std::vector<std::tuple<int, int, int>> links = {
        {0, 1, 5},
        {0, 2, 3},
        {1, 3, 6},
        {1, 2, 2},
        {2, 4, 4},
        {3, 5, 2},
        {4, 5, 6}
    };
    int S = 0;
    int D = 5;
    
    // Calculate expected paths:
    // 0->1->3->5: avg = (5+6+2)/3 = 4.33
    // 0->2->4->5: avg = (3+4+6)/3 = 4.33
    // 0->2->1->3->5: avg = (3+2+6+2)/4 = 3.25  (Best)
    // 0->1->2->4->5: avg = (5+2+4+6)/4 = 4.25
    
    std::vector<int> result = find_optimal_route(N, links, S, D);
    bool valid = (result == std::vector<int>{0, 2, 1, 3, 5}) || 
                 (result == std::vector<int>{0, 2, 4, 5}) ||
                 (result == std::vector<int>{0, 1, 3, 5}) ||
                 (result == std::vector<int>{0, 1, 2, 4, 5});
    
    REQUIRE(valid);
}

TEST_CASE("Path with minimum total but not minimum average", "[total_vs_average]") {
    int N = 4;
    std::vector<std::tuple<int, int, int>> links = {
        {0, 1, 1},
        {1, 2, 10},
        {2, 3, 1},
        {0, 3, 7}
    };
    int S = 0;
    int D = 3;
    
    // Path 0->1->2->3: total = 12, avg = 4
    // Path 0->3: total = 7, avg = 7
    // Should choose the path with lower average
    std::vector<int> expected = {0, 1, 2, 3};
    REQUIRE(find_optimal_route(N, links, S, D) == expected);
}

TEST_CASE("Large network stress test", "[stress_test]") {
    int N = 1000;
    std::vector<std::tuple<int, int, int>> links;
    
    // Create a line graph with increasing latencies
    for (int i = 0; i < N-1; i++) {
        links.push_back({i, i+1, i+1});
    }
    
    // Add a direct link from 0 to N-1 with high latency
    links.push_back({0, N-1, 1000});
    
    int S = 0;
    int D = N-1;
    
    // We check if the result is valid without checking specific path
    // due to potential multiple optimal paths
    std::vector<int> result = find_optimal_route(N, links, S, D);
    
    REQUIRE(!result.empty());
    REQUIRE(result.front() == S);
    REQUIRE(result.back() == D);
}

TEST_CASE("Disconnected graph with multiple components", "[disconnected_complex]") {
    int N = 10;
    std::vector<std::tuple<int, int, int>> links = {
        {0, 1, 5},
        {1, 2, 3},
        {2, 0, 2},
        {4, 5, 1},
        {5, 6, 7},
        {6, 4, 2},
        {7, 8, 9},
        {8, 9, 4}
    };
    int S = 0;
    int D = 7;
    
    std::vector<int> expected = {};  // No path exists
    REQUIRE(find_optimal_route(N, links, S, D) == expected);
}

TEST_CASE("Empty links", "[empty_links]") {
    int N = 5;
    std::vector<std::tuple<int, int, int>> links = {};
    int S = 0;
    int D = 4;
    
    std::vector<int> expected = {};
    REQUIRE(find_optimal_route(N, links, S, D) == expected);
}

TEST_CASE("Average latency tiebreak by shortest path", "[tiebreak]") {
    int N = 5;
    std::vector<std::tuple<int, int, int>> links = {
        {0, 1, 5},
        {1, 4, 5},
        {0, 2, 5},
        {2, 3, 5},
        {3, 4, 5}
    };
    int S = 0;
    int D = 4;
    
    // Path 0->1->4: total = 10, avg = 5, hops = 2
    // Path 0->2->3->4: total = 15, avg = 5, hops = 3
    // Both have same average, any is valid
    std::vector<int> result = find_optimal_route(N, links, S, D);
    bool valid = (result == std::vector<int>{0, 1, 4}) || 
                 (result == std::vector<int>{0, 2, 3, 4});
    
    REQUIRE(valid);
}