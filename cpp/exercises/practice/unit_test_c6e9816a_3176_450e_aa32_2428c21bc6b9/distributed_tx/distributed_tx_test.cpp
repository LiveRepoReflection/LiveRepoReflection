#include "distributed_tx.h"
#include "catch.hpp"
#include <vector>
#include <tuple>
#include <cmath>

using namespace std;
using namespace distributed_tx;

TEST_CASE("Single Microservice (only coordinator)") {
    int N = 1;
    vector<tuple<int, int, int>> edges; // No edges
    vector<double> failure_probability; // Empty for coordinator only
    vector<int> prep_cost; // Empty for coordinator only
    vector<int> commit_cost; // Empty for coordinator only

    // Expected cost is 0 since there is only coordinator and no messages or operations.
    double expected = 0.0;
    double result = expected_transaction_cost(N, edges, failure_probability, prep_cost, commit_cost);
    REQUIRE(result == Approx(expected).epsilon(0.001));
}

TEST_CASE("Basic three microservices example") {
    int N = 3;
    // Graph: (0, 1, 10), (0, 2, 15), (1, 2, 5)
    vector<tuple<int, int, int>> edges = { make_tuple(0, 1, 10),
                                            make_tuple(0, 2, 15),
                                            make_tuple(1, 2, 5) };

    // For microservices 1 and 2 (ids 1 and 2)
    // Shortest distances from coordinator:
    // Microservice 1: 10, Microservice 2: 15 (0->2 or 0->1->2 both are 15)
    // Network cost = 2*(10+15) = 50.
    // Preparation cost = 50 + 60 = 110.
    // Probability of commit = (1-0.1)*(1-0.2) = 0.9*0.8 = 0.72.
    // Commit cost = 70 + 80 = 150. Expected commit cost = 150 * 0.72 = 108.
    // Total expected cost = 50 + 110 + 108 = 268.
    vector<double> failure_probability = {0.1, 0.2};
    vector<int> prep_cost = {50, 60};
    vector<int> commit_cost = {70, 80};
    double expected = 268.0;
    double result = expected_transaction_cost(N, edges, failure_probability, prep_cost, commit_cost);
    REQUIRE(result == Approx(expected).epsilon(0.001));
}

TEST_CASE("Four microservices with varied network distances") {
    int N = 4;
    // Graph:
    // (0, 1, 5), (0, 2, 10), (1, 2, 3), (1, 3, 20), (2, 3, 2)
    // Shortest distances:
    // For microservice 1: 5
    // For microservice 2: 0->1->2 = 5+3 = 8 (better than direct 10)
    // For microservice 3: 0->1->2->3 = 5+3+2 = 10
    // Network cost = 2*(5+8+10) = 46.
    // Preparation cost = 100 + 200 + 300 = 600.
    // Failure probabilities: 0.0, 0.1, 0.2, so commit probability = 1*0.9*0.8 = 0.72.
    // Commit cost = 50 + 75 + 100 = 225. Expected commit cost = 225*0.72 = 162.
    // Total expected cost = 46 + 600 + 162 = 808.
    vector<tuple<int, int, int>> edges = { make_tuple(0, 1, 5),
                                            make_tuple(0, 2, 10),
                                            make_tuple(1, 2, 3),
                                            make_tuple(1, 3, 20),
                                            make_tuple(2, 3, 2) };
    vector<double> failure_probability = {0.0, 0.1, 0.2};
    vector<int> prep_cost = {100, 200, 300};
    vector<int> commit_cost = {50, 75, 100};
    double expected = 808.0;
    double result = expected_transaction_cost(N, edges, failure_probability, prep_cost, commit_cost);
    REQUIRE(result == Approx(expected).epsilon(0.001));
}

TEST_CASE("Transaction always fails (failure probability 1)") {
    int N = 3;
    // Graph: (0, 1, 4), (0, 2, 6)
    // Shortest distances:
    // Microservice 1: 4
    // Microservice 2: 6
    // Network cost = 2*(4+6) = 20.
    // Preparation cost = 30 + 40 = 70.
    // Commit probability = (1-1)*(1-1) = 0.
    // Commit cost = 50+70 = 120, expected commit cost = 0.
    // Total expected cost = 20 + 70 + 0 = 90.
    vector<tuple<int, int, int>> edges = { make_tuple(0, 1, 4),
                                            make_tuple(0, 2, 6) };
    vector<double> failure_probability = {1.0, 1.0};
    vector<int> prep_cost = {30, 40};
    vector<int> commit_cost = {50, 70};
    double expected = 90.0;
    double result = expected_transaction_cost(N, edges, failure_probability, prep_cost, commit_cost);
    REQUIRE(result == Approx(expected).epsilon(0.001));
}

TEST_CASE("Complex graph with multiple paths and floating point precision") {
    int N = 5;
    // Graph definition:
    // (0, 1, 7), (0, 2, 3), (1, 2, 1), (1, 3, 8),
    // (2, 3, 2), (2, 4, 7), (3, 4, 4)
    // Compute shortest distances from 0:
    // Microservice 1: 0->2->1 = 3+1 = 4 (instead of direct 7)
    // Microservice 2: 3
    // Microservice 3: 0->2->3 = 3+2 = 5
    // Microservice 4: 0->2->3->4 = 3+2+4 = 9 (or 0->2->4 = 3+7 = 10, so use 9)
    // Network cost = 2*(4 + 3 + 5 + 9) = 2*21 = 42.
    // Preparation costs: 20, 30, 40, 50 => total = 140.
    // Commit costs: 10, 15, 20, 25 => total = 70.
    // Failure probabilities: 0.05, 0.1, 0.15, 0.2
    // Commit probability = 0.95*0.9*0.85*0.8 = 0.5814 (approx).
    // Expected commit cost = 70 * 0.5814 = 40.698 (approx).
    // Total expected cost = 42 + 140 + 40.698 = 222.698 (approx).
    vector<tuple<int, int, int>> edges = { make_tuple(0, 1, 7),
                                            make_tuple(0, 2, 3),
                                            make_tuple(1, 2, 1),
                                            make_tuple(1, 3, 8),
                                            make_tuple(2, 3, 2),
                                            make_tuple(2, 4, 7),
                                            make_tuple(3, 4, 4) };
    vector<double> failure_probability = {0.05, 0.1, 0.15, 0.2};
    vector<int> prep_cost = {20, 30, 40, 50};
    vector<int> commit_cost = {10, 15, 20, 25};
    double expected = 222.698;
    double result = expected_transaction_cost(N, edges, failure_probability, prep_cost, commit_cost);
    REQUIRE(result == Approx(expected).epsilon(0.001));
}