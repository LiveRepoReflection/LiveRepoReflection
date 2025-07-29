#include "influence_network.h"
#include "catch.hpp"
#include <vector>
#include <utility>

using std::vector;
using std::pair;

// Test Case 1: Simple Propagation Test
// Graph:
// 0 -> 1, 0 -> 2, 1 -> 3, 2 -> 4
// Initial activated: {0}
// Influence scores and activation thresholds are set to guarantee propagation.
TEST_CASE("simple_propagation") {
    int numUsers = 5;
    // Define directed edges
    vector<pair<int, int>> edges = { {0, 1}, {0, 2}, {1, 3}, {2, 4} };
    // Influence scores for each user (non-negative)
    // Higher influence scores mean stronger ability to activate neighbors.
    vector<double> influenceScores = {1.0, 0.5, 0.5, 0.5, 0.5};
    // Activation thresholds are set so that any neighbor's influence meeting or exceeding the threshold triggers activation.
    // For simplicity, use low thresholds that are exceeded by one neighbor's influence.
    vector<double> activationThresholds = {0.0, 0.8, 0.8, 0.8, 0.8};
    // Only user 0 is initially activated.
    vector<int> initialActivated = {0};
    // Simulate for 3 time steps.
    int timeSteps = 3;

    // Expected propagation:
    // Time step 1: Users 1 and 2 become activated (influence from 0 = 1.0 > 0.8)
    // Time step 2: Users 3 and 4 become activated (influence from 1 or 2 = 0.5 but may need combined influence from multiple neighbors if applicable.
    // To ensure activation, assume that even a single neighbor's influence suffices if the threshold is low enough.
    // Here, since thresholds are set at 0.8 and influenceScores for 1 and 2 are 0.5, 
    // the propagation to nodes 3 and 4 will only occur if they receive influence from multiple activated neighbors.
    // Therefore, we adjust the thresholds for nodes 3 and 4.
    activationThresholds[3] = 0.3;
    activationThresholds[4] = 0.3;

    int activatedCount = influence_network::simulateInfluence(numUsers, edges, influenceScores, activationThresholds, initialActivated, timeSteps);
    // All nodes should be activated.
    REQUIRE(activatedCount == 5);
}

// Test Case 2: No Propagation Test
// Set thresholds too high to allow any propagation.
TEST_CASE("no_propagation_due_to_high_thresholds") {
    int numUsers = 4;
    vector<pair<int, int>> edges = { {0, 1}, {1, 2}, {2, 3} };
    vector<double> influenceScores = {1.0, 0.5, 0.5, 0.5};
    // Set thresholds so high that no propagation can occur.
    vector<double> activationThresholds = {0.0, 2.0, 2.0, 2.0};
    vector<int> initialActivated = {0};
    int timeSteps = 5;

    int activatedCount = influence_network::simulateInfluence(numUsers, edges, influenceScores, activationThresholds, initialActivated, timeSteps);
    // Only the initially activated user remains active.
    REQUIRE(activatedCount == 1);
}

// Test Case 3: Cycle in Graph Test
// Graph with a cycle to verify that simulation does not loop indefinitely.
TEST_CASE("cycle_in_graph") {
    int numUsers = 3;
    // Create a cycle: 0 -> 1, 1 -> 2, 2 -> 0.
    vector<pair<int, int>> edges = { {0, 1}, {1, 2}, {2, 0} };
    vector<double> influenceScores = {0.6, 0.6, 0.6};
    // Set thresholds to allow propagation with influence from one neighbor.
    vector<double> activationThresholds = {0.4, 0.4, 0.4};
    vector<int> initialActivated = {0};
    int timeSteps = 4;  // More than enough time steps

    int activatedCount = influence_network::simulateInfluence(numUsers, edges, influenceScores, activationThresholds, initialActivated, timeSteps);
    // Entire cycle should become activated.
    REQUIRE(activatedCount == 3);
}

// Test Case 4: Self-loop and Duplicate Edges
// Test edge cases where a node has a self-loop and duplicate incoming edges.
TEST_CASE("self_loop_and_duplicate_edges") {
    int numUsers = 3;
    // Graph:
    // 0 -> 1 (duplicate), 0 -> 1 (duplicate), 1 -> 1 (self-loop), 1 -> 2.
    vector<pair<int, int>> edges = { {0, 1}, {0, 1}, {1, 1}, {1, 2} };
    vector<double> influenceScores = {1.0, 0.5, 0.5};
    vector<double> activationThresholds = {0.0, 0.7, 0.4};
    vector<int> initialActivated = {0};
    int timeSteps = 3;

    // Explanation:
    // Time step 1: User 1 receives influence 1.0 from 0, surpassing threshold 0.7, so becomes activated.
    // Time step 2: User 2 receives influence 0.5 from 1 (satisfies threshold 0.4) and becomes activated.
    int activatedCount = influence_network::simulateInfluence(numUsers, edges, influenceScores, activationThresholds, initialActivated, timeSteps);
    REQUIRE(activatedCount == 3);
}

// Test Case 5: Empty Graph Test
// Test simulation on an empty network.
TEST_CASE("empty_graph") {
    int numUsers = 0;
    vector<pair<int, int>> edges;
    vector<double> influenceScores;
    vector<double> activationThresholds;
    vector<int> initialActivated;
    int timeSteps = 5;

    int activatedCount = influence_network::simulateInfluence(numUsers, edges, influenceScores, activationThresholds, initialActivated, timeSteps);
    REQUIRE(activatedCount == 0);
}