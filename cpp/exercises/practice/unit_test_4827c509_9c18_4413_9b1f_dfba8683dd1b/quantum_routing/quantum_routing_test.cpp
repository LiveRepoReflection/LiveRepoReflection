#include "quantum_routing.h"
#include "catch.hpp"
#include <vector>
#include <tuple>
#include <cmath>

TEST_CASE("Optimal path with multiple options") {
    int N = 4;
    std::vector<std::tuple<int, int, double>> edges = {
        {0, 1, 0.9}, {1, 2, 0.8}, {2, 3, 0.7}, {0, 2, 0.6}
    };
    int S = 0;
    int D = 3;
    double swap_penalty = 0.9;
    
    double expected = 0.40824; // 0.9 * 0.8 * 0.7 * 0.9 * 0.9
    REQUIRE_THAT(quantum_routing::find_optimal_path(N, edges, S, D, swap_penalty), 
                 Catch::Matchers::WithinAbs(expected, 0.00001));
}

TEST_CASE("Direct edge is optimal") {
    int N = 3;
    std::vector<std::tuple<int, int, double>> edges = {
        {0, 1, 0.8}, {1, 2, 0.7}, {0, 2, 0.6}
    };
    int S = 0;
    int D = 2;
    double swap_penalty = 0.5;
    
    // Direct edge: 0.6
    // Path through node 1: 0.8 * 0.7 * 0.5 = 0.28
    double expected = 0.6;
    REQUIRE_THAT(quantum_routing::find_optimal_path(N, edges, S, D, swap_penalty), 
                 Catch::Matchers::WithinAbs(expected, 0.00001));
}

TEST_CASE("Longer path with better fidelity is optimal") {
    int N = 4;
    std::vector<std::tuple<int, int, double>> edges = {
        {0, 1, 0.95}, {1, 2, 0.95}, {2, 3, 0.95}, {0, 3, 0.8}
    };
    int S = 0;
    int D = 3;
    double swap_penalty = 0.95;
    
    // Direct edge: 0.8
    // Path through nodes 1 and 2: 0.95 * 0.95 * 0.95 * 0.95^2 = 0.77129...
    double expected = 0.8; // Direct edge is better
    REQUIRE_THAT(quantum_routing::find_optimal_path(N, edges, S, D, swap_penalty), 
                 Catch::Matchers::WithinAbs(expected, 0.00001));
}

TEST_CASE("No path exists") {
    int N = 4;
    std::vector<std::tuple<int, int, double>> edges = {
        {0, 1, 0.9}, {1, 2, 0.8} // No connection to node 3
    };
    int S = 0;
    int D = 3;
    double swap_penalty = 0.9;
    
    double expected = 0.0;
    REQUIRE_THAT(quantum_routing::find_optimal_path(N, edges, S, D, swap_penalty), 
                 Catch::Matchers::WithinAbs(expected, 0.00001));
}

TEST_CASE("Multiple edges between same nodes") {
    int N = 3;
    std::vector<std::tuple<int, int, double>> edges = {
        {0, 1, 0.7}, {0, 1, 0.9}, {1, 2, 0.8}
    };
    int S = 0;
    int D = 2;
    double swap_penalty = 0.9;
    
    // Should choose edge with higher fidelity (0.9) between nodes 0 and 1
    double expected = 0.9 * 0.8 * 0.9;
    REQUIRE_THAT(quantum_routing::find_optimal_path(N, edges, S, D, swap_penalty), 
                 Catch::Matchers::WithinAbs(expected, 0.00001));
}

TEST_CASE("Large network with complex topology") {
    int N = 6;
    std::vector<std::tuple<int, int, double>> edges = {
        {0, 1, 0.9}, {1, 2, 0.8}, {2, 5, 0.7},
        {0, 3, 0.85}, {3, 4, 0.95}, {4, 5, 0.9},
        {1, 3, 0.75}, {2, 4, 0.8}
    };
    int S = 0;
    int D = 5;
    double swap_penalty = 0.85;
    
    // Multiple paths exist:
    // 0->1->2->5: 0.9 * 0.8 * 0.7 * 0.85^2 = 0.36414
    // 0->3->4->5: 0.85 * 0.95 * 0.9 * 0.85^2 = 0.55345...
    // 0->1->3->4->5: 0.9 * 0.75 * 0.95 * 0.9 * 0.85^3 = 0.41128...
    // 0->3->1->2->5: 0.85 * 0.75 * 0.8 * 0.7 * 0.85^3 = 0.23267...
    // And more complex paths...
    
    // The path 0->3->4->5 should be optimal
    double expected = 0.85 * 0.95 * 0.9 * 0.85 * 0.85;
    REQUIRE_THAT(quantum_routing::find_optimal_path(N, edges, S, D, swap_penalty), 
                 Catch::Matchers::WithinAbs(expected, 0.00001));
}

TEST_CASE("Extreme edge case - single edge") {
    int N = 2;
    std::vector<std::tuple<int, int, double>> edges = {
        {0, 1, 0.75}
    };
    int S = 0;
    int D = 1;
    double swap_penalty = 0.9;
    
    // Direct connection, no swaps needed
    double expected = 0.75;
    REQUIRE_THAT(quantum_routing::find_optimal_path(N, edges, S, D, swap_penalty), 
                 Catch::Matchers::WithinAbs(expected, 0.00001));
}

TEST_CASE("Extreme penalty makes shorter paths better") {
    int N = 4;
    std::vector<std::tuple<int, int, double>> edges = {
        {0, 1, 0.9}, {1, 3, 0.9}, {0, 2, 0.6}, {2, 3, 0.6}
    };
    int S = 0;
    int D = 3;
    double swap_penalty = 0.3;
    
    // Path 0->1->3: 0.9 * 0.9 * 0.3 = 0.243
    // Path 0->2->3: 0.6 * 0.6 * 0.3 = 0.108
    // The higher fidelity path through nodes 1 is optimal despite the swap penalty
    double expected = 0.9 * 0.9 * 0.3;
    REQUIRE_THAT(quantum_routing::find_optimal_path(N, edges, S, D, swap_penalty), 
                 Catch::Matchers::WithinAbs(expected, 0.00001));
}

TEST_CASE("Perfect fidelity and penalty") {
    int N = 3;
    std::vector<std::tuple<int, int, double>> edges = {
        {0, 1, 1.0}, {1, 2, 1.0}
    };
    int S = 0;
    int D = 2;
    double swap_penalty = 1.0;
    
    // Perfect transmission
    double expected = 1.0;
    REQUIRE_THAT(quantum_routing::find_optimal_path(N, edges, S, D, swap_penalty), 
                 Catch::Matchers::WithinAbs(expected, 0.00001));
}

TEST_CASE("Very low fidelity edges") {
    int N = 3;
    std::vector<std::tuple<int, int, double>> edges = {
        {0, 1, 0.01}, {1, 2, 0.01}
    };
    int S = 0;
    int D = 2;
    double swap_penalty = 0.5;
    
    // Very low probability of success
    double expected = 0.01 * 0.01 * 0.5;
    REQUIRE_THAT(quantum_routing::find_optimal_path(N, edges, S, D, swap_penalty), 
                 Catch::Matchers::WithinAbs(expected, 0.00001));
}