#include "network_capacity.h"
#include "catch.hpp"
#include <vector>

using namespace std;
using namespace network_capacity;

TEST_CASE("no path exists returns 0.0") {
    int N = 3;
    vector<Edge> edges = {
        {0, 1, 10, 0.0} // Only one reliable edge; node 2 is disconnected.
    };
    double result = max_guaranteed_bandwidth(N, edges, 0, 2);
    REQUIRE(result == Approx(0.0));
}

TEST_CASE("simple reliable path returns correct bandwidth") {
    int N = 3;
    vector<Edge> edges = {
        {0, 1, 10, 0.0},
        {1, 2, 5, 0.0}
    };
    // The guaranteed bandwidth is the minimum capacity along the path (5)
    // multiplied by the probability that all channels are active (1.0).
    double result = max_guaranteed_bandwidth(N, edges, 0, 2);
    REQUIRE(result == Approx(5.0));
}

TEST_CASE("multiple paths choose best guaranteed bandwidth") {
    int N = 4;
    vector<Edge> edges = {
        {0, 1, 10, 0.1}, // Unreliable edge: effective factor 0.9.
        {1, 3, 10, 0.0}, // Reliable edge.
        {0, 2, 6, 0.0},  // Reliable edge.
        {2, 3, 7, 0.2}   // Unreliable edge: effective factor 0.8.
    };
    // Two possible paths:
    // Path 0->1->3: minimum capacity = 10, overall probability = (1-0.1)*1.0 = 0.9,
    //   so guaranteed bandwidth = 10 * 0.9 = 9.0.
    // Path 0->2->3: minimum capacity = min(6,7) = 6, overall probability = 1.0*0.8 = 0.8,
    //   so guaranteed bandwidth = 6 * 0.8 = 4.8.
    // The best guaranteed bandwidth is 9.0.
    double result = max_guaranteed_bandwidth(N, edges, 0, 3);
    REQUIRE(result == Approx(9.0).epsilon(0.000001));
}

TEST_CASE("complex network with cycles returns best guaranteed bandwidth") {
    int N = 6;
    vector<Edge> edges = {
        {0, 1, 15, 0.05},
        {1, 2, 10, 0.0},
        {0, 3, 10, 0.0},
        {3, 2, 10, 0.10},
        {2, 4, 20, 0.0},
        {4, 5, 5, 0.2},
        {1, 5, 5, 0.0},
        {3, 5, 15, 0.0},
        {2, 5, 10, 0.0}
    };
    // Evaluating several possible paths from 0 to 5:
    // Path 0->3->5: min capacity = min(10,15) = 10, overall probability = 1.0*1.0 = 1.0,
    //   resulting in a guaranteed bandwidth = 10.
    // Other paths yield lower effective bandwidths.
    double result = max_guaranteed_bandwidth(N, edges, 0, 5);
    REQUIRE(result == Approx(10.0).epsilon(0.000001));
}

TEST_CASE("network with all unreliable edges selects the optimal path") {
    int N = 4;
    vector<Edge> edges = {
        {0, 1, 50, 0.5},
        {1, 2, 40, 0.5},
        {2, 3, 30, 0.5},
        {0, 3, 20, 0.5}
    };
    // Two potential paths:
    // Path 0->1->2->3: min capacity = min(50,40,30) = 30, overall probability = 0.5^3 = 0.125,
    //   resulting in a guaranteed bandwidth = 30 * 0.125 = 3.75.
    // Path 0->3: capacity = 20, overall probability = 0.5,
    //   resulting in a guaranteed bandwidth = 20 * 0.5 = 10.0.
    // The optimal guaranteed bandwidth is therefore 10.0.
    double result = max_guaranteed_bandwidth(N, edges, 0, 3);
    REQUIRE(result == Approx(10.0).epsilon(0.000001));
}