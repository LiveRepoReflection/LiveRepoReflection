#include "social_influence.h"
#include <vector>
#include <utility>
#include <stdexcept>
#include <algorithm>
#include "catch.hpp"

// Helper function to compare two vectors for equality.
bool vectors_equal(const std::vector<int>& a, const std::vector<int>& b) {
    return a == b;
}

TEST_CASE("single_node", "[social_influence]") {
    int N = 1;
    std::vector<std::pair<int, int>> edges;
    std::vector<int> activity_scores = {100};
    int K = 1;
    int max_steps = 5;
    
    std::vector<int> result = social_influence::find_top_influencers(N, edges, activity_scores, K, max_steps);
    std::vector<int> expected = {0};
    
    REQUIRE(vectors_equal(result, expected));
}

TEST_CASE("example_network", "[social_influence]") {
    // Provided sample test.
    int N = 5;
    std::vector<std::pair<int, int>> edges = { {0,1}, {0,2}, {1,2}, {2,3}, {3,4} };
    std::vector<int> activity_scores = {10, 5, 12, 8, 3};
    int K = 2;
    int max_steps = 10;
    
    std::vector<int> result = social_influence::find_top_influencers(N, edges, activity_scores, K, max_steps);
    std::vector<int> expected = {2, 0}; // As per the example description.
    
    REQUIRE(vectors_equal(result, expected));
}

TEST_CASE("disconnected_graph", "[social_influence]") {
    // Two disconnected components and an isolated node.
    int N = 6;
    // Component 1: 0,1,2; Component 2: 3,4; Node 5 is isolated.
    std::vector<std::pair<int, int>> edges = { {0,1}, {1,2}, {3,4} };
    std::vector<int> activity_scores = {10, 20, 30, 40, 50, 60};
    int K = 3;
    // Set max_steps to 1 so cascade stops at the initial node.
    int max_steps = 1;
    
    // With max_steps = 1, each user's WCR equals their own activity.
    // The top three users by activity are nodes 5 (60), 4 (50), and 3 (40).
    std::vector<int> result = social_influence::find_top_influencers(N, edges, activity_scores, K, max_steps);
    std::vector<int> expected = {5, 4, 3};
    
    REQUIRE(vectors_equal(result, expected));
}

TEST_CASE("cycle_graph_max_steps_one", "[social_influence]") {
    // Cycle graph where cascade is not propagated beyond the initial node.
    int N = 3;
    std::vector<std::pair<int, int>> edges = { {0,1}, {1,2}, {2,0} };
    std::vector<int> activity_scores = {5, 15, 10};
    int K = 3;
    int max_steps = 1;
    
    // With max_steps = 1, influence is based solely on self activity.
    // Sorted by activity descending, tie-break using user id ascending.
    // Here expected output is [1, 2, 0].
    std::vector<int> result = social_influence::find_top_influencers(N, edges, activity_scores, K, max_steps);
    std::vector<int> expected = {1, 2, 0};
    
    REQUIRE(vectors_equal(result, expected));
}

TEST_CASE("deterministic_consistency", "[social_influence]") {
    // Verify that repeated calls with the same inputs yield identical outputs.
    int N = 7;
    std::vector<std::pair<int, int>> edges = { {0,1}, {1,2}, {2,3}, {3,4}, {4,5}, {5,6}, {0,6} };
    std::vector<int> activity_scores = {12, 7, 9, 15, 8, 11, 14};
    int K = 4;
    int max_steps = 5;
    
    std::vector<int> result1 = social_influence::find_top_influencers(N, edges, activity_scores, K, max_steps);
    std::vector<int> result2 = social_influence::find_top_influencers(N, edges, activity_scores, K, max_steps);
    
    REQUIRE(vectors_equal(result1, result2));
}

TEST_CASE("invalid_parameters", "[social_influence]") {
    // Test that invalid parameters trigger error handling when appropriate.
    int N = 3;
    std::vector<std::pair<int, int>> edges = { {0,1}, {1,2} };
    std::vector<int> activity_scores = {10, 20, 30};
    
    SECTION("K exceeds number of users") {
        int K = 5;  // K is greater than N.
        int max_steps = 5;
        // Assuming implementation should throw std::invalid_argument for invalid K.
        REQUIRE_THROWS_AS(social_influence::find_top_influencers(N, edges, activity_scores, K, max_steps), std::invalid_argument);
    }
    
    SECTION("empty activity_scores") {
        std::vector<int> empty_scores;
        int K = 1;
        int max_steps = 5;
        REQUIRE_THROWS_AS(social_influence::find_top_influencers(N, edges, empty_scores, K, max_steps), std::invalid_argument);
    }
}