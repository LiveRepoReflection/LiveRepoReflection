#include "catch.hpp"
#include "route_optimizer.h"

#include <tuple>
#include <vector>

TEST_CASE("Start and destination are the same") {
    int n = 5;
    std::vector<std::tuple<int, int, int, int, int>> edges = {
        {0, 1, 50, 5, 2},
        {0, 2, 100, 10, 3},
        {1, 2, 50, 0, 1}
    };
    int start = 2;
    int destination = 2;
    int max_travel_time = 350;
    int max_toll_cost = 30;
    
    REQUIRE(solve(n, edges, start, destination, max_travel_time, max_toll_cost) == 0);
}

TEST_CASE("Simple path with one edge") {
    int n = 2;
    std::vector<std::tuple<int, int, int, int, int>> edges = {
        {0, 1, 50, 5, 2}
    };
    int start = 0;
    int destination = 1;
    int max_travel_time = 100;
    int max_toll_cost = 10;
    
    REQUIRE(solve(n, edges, start, destination, max_travel_time, max_toll_cost) == 2);
}

TEST_CASE("Two possible paths with same total congestion") {
    int n = 4;
    std::vector<std::tuple<int, int, int, int, int>> edges = {
        {0, 1, 50, 5, 2},
        {0, 2, 100, 10, 3},
        {1, 3, 150, 20, 4},
        {2, 3, 100, 15, 3}
    };
    int start = 0;
    int destination = 3;
    int max_travel_time = 350;
    int max_toll_cost = 30;
    
    // Two possible paths:
    // 0 -> 1 -> 3 (Time: 200, Toll: 25, Congestion: 2 + 4 = 6)
    // 0 -> 2 -> 3 (Time: 200, Toll: 25, Congestion: 3 + 3 = 6)
    // Both have same congestion, so either is optimal
    REQUIRE(solve(n, edges, start, destination, max_travel_time, max_toll_cost) == 6);
}

TEST_CASE("Multiple paths with different congestion levels") {
    int n = 5;
    std::vector<std::tuple<int, int, int, int, int>> edges = {
        {0, 1, 50, 5, 2},
        {0, 2, 100, 10, 3},
        {1, 2, 50, 0, 1},
        {1, 3, 150, 20, 4},
        {2, 3, 50, 5, 2},
        {2, 4, 100, 10, 3},
        {3, 4, 100, 0, 1}
    };
    int start = 0;
    int destination = 4;
    int max_travel_time = 350;
    int max_toll_cost = 30;
    
    // Optimal path: 0 -> 1 -> 2 -> 3 -> 4 (Time: 300, Toll: 10, Congestion: 2 + 1 + 2 + 1 = 6)
    REQUIRE(solve(n, edges, start, destination, max_travel_time, max_toll_cost) == 6);
}

TEST_CASE("Time constraint violation") {
    int n = 3;
    std::vector<std::tuple<int, int, int, int, int>> edges = {
        {0, 1, 200, 5, 2},
        {1, 2, 200, 5, 1}
    };
    int start = 0;
    int destination = 2;
    int max_travel_time = 300;
    int max_toll_cost = 20;
    
    // Total time would be 400, exceeding the limit of 300
    REQUIRE(solve(n, edges, start, destination, max_travel_time, max_toll_cost) == -1);
}

TEST_CASE("Toll constraint violation") {
    int n = 3;
    std::vector<std::tuple<int, int, int, int, int>> edges = {
        {0, 1, 100, 15, 2},
        {1, 2, 100, 15, 1}
    };
    int start = 0;
    int destination = 2;
    int max_travel_time = 300;
    int max_toll_cost = 20;
    
    // Total toll would be 30, exceeding the limit of 20
    REQUIRE(solve(n, edges, start, destination, max_travel_time, max_toll_cost) == -1);
}

TEST_CASE("No path exists") {
    int n = 3;
    std::vector<std::tuple<int, int, int, int, int>> edges = {
        {0, 1, 50, 5, 2},
        {2, 1, 50, 5, 1}
    };
    int start = 0;
    int destination = 2;
    int max_travel_time = 300;
    int max_toll_cost = 20;
    
    // No path from 0 to 2
    REQUIRE(solve(n, edges, start, destination, max_travel_time, max_toll_cost) == -1);
}

TEST_CASE("Example from problem statement") {
    int n = 5;
    std::vector<std::tuple<int, int, int, int, int>> edges = {
        {0, 1, 50, 5, 2},
        {0, 2, 100, 10, 3},
        {1, 2, 50, 0, 1},
        {1, 3, 150, 20, 4},
        {2, 3, 50, 5, 2},
        {2, 4, 100, 10, 3},
        {3, 4, 100, 0, 1}
    };
    int start = 0;
    int destination = 4;
    int max_travel_time = 350;
    int max_toll_cost = 30;
    
    REQUIRE(solve(n, edges, start, destination, max_travel_time, max_toll_cost) == 6);
}

TEST_CASE("Large graph with many possible paths") {
    int n = 10;
    std::vector<std::tuple<int, int, int, int, int>> edges = {
        {0, 1, 10, 5, 1}, {0, 2, 20, 8, 2}, {1, 3, 30, 10, 3},
        {1, 4, 40, 12, 4}, {2, 4, 25, 7, 2}, {2, 5, 35, 9, 3},
        {3, 6, 15, 6, 1}, {3, 7, 25, 8, 2}, {4, 7, 30, 10, 3},
        {4, 8, 40, 12, 4}, {5, 8, 20, 7, 2}, {5, 9, 30, 9, 3},
        {6, 7, 10, 4, 1}, {7, 8, 20, 6, 2}, {8, 9, 15, 5, 1}
    };
    int start = 0;
    int destination = 9;
    int max_travel_time = 150;
    int max_toll_cost = 40;
    
    // Multiple possible paths exist, should find optimal one with congestion sum = 8
    REQUIRE(solve(n, edges, start, destination, max_travel_time, max_toll_cost) == 8);
}

TEST_CASE("Graph with loops") {
    int n = 5;
    std::vector<std::tuple<int, int, int, int, int>> edges = {
        {0, 1, 10, 5, 2}, {1, 2, 20, 8, 3}, {2, 3, 15, 6, 1},
        {3, 4, 10, 4, 2}, {4, 1, 5, 2, 1}, {1, 4, 30, 10, 4}
    };
    int start = 0;
    int destination = 3;
    int max_travel_time = 100;
    int max_toll_cost = 30;
    
    // Optimal path is 0->1->2->3 with congestion sum 6
    REQUIRE(solve(n, edges, start, destination, max_travel_time, max_toll_cost) == 6);
}

TEST_CASE("Exact constraints") {
    int n = 4;
    std::vector<std::tuple<int, int, int, int, int>> edges = {
        {0, 1, 50, 10, 2}, {0, 2, 75, 15, 1}, 
        {1, 3, 50, 10, 3}, {2, 3, 25, 5, 4}
    };
    int start = 0;
    int destination = 3;
    int max_travel_time = 100;
    int max_toll_cost = 20;
    
    // Path 0->1->3 exactly meets time constraint (100)
    // Path 0->2->3 exactly meets toll constraint (20)
    // Should choose 0->2->3 as it has lower congestion (1+4=5 vs 2+3=5)
    REQUIRE(solve(n, edges, start, destination, max_travel_time, max_toll_cost) == 5);
}

TEST_CASE("Maximum constraints edge case") {
    int n = 4;
    std::vector<std::tuple<int, int, int, int, int>> edges;
    
    // Create a complete graph with maximum allowed constraints
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            if (i != j) {
                edges.push_back({i, j, 100, 50, 5});
            }
        }
    }
    
    int start = 0;
    int destination = 3;
    int max_travel_time = 100;
    int max_toll_cost = 50;
    
    // Direct path from 0 to 3 with congestion 5
    REQUIRE(solve(n, edges, start, destination, max_travel_time, max_toll_cost) == 5);
}

TEST_CASE("Multiple equivalent optimal paths") {
    int n = 4;
    std::vector<std::tuple<int, int, int, int, int>> edges = {
        {0, 1, 10, 5, 1}, {0, 2, 10, 5, 1},
        {1, 3, 10, 5, 1}, {2, 3, 10, 5, 1}
    };
    int start = 0;
    int destination = 3;
    int max_travel_time = 30;
    int max_toll_cost = 15;
    
    // Two equivalent paths: 0->1->3 and 0->2->3
    // Both have time=20, toll=10, congestion=2
    REQUIRE(solve(n, edges, start, destination, max_travel_time, max_toll_cost) == 2);
}