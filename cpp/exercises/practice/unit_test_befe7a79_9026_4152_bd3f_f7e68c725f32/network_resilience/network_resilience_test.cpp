#include "catch.hpp"
#include <climits>
#include <tuple>
#include <vector>

#include "network_resilience.h"

using namespace std;
using namespace network_resilience;

TEST_CASE("Single node with no edges") {
    int N = 1;
    vector<tuple<int, int, int>> edges;
    // With only one node and no edge, the sub-network is isolated so its resilience is considered infinity.
    // We represent infinity as INT_MAX.
    int expected = INT_MAX;
    REQUIRE(maximum_resilience(N, edges) == expected);
}

TEST_CASE("Two nodes with one edge") {
    int N = 2;
    vector<tuple<int, int, int>> edges = {
        make_tuple(0, 1, 5)
    };
    // Only one connected component with an edge of cost 5.
    int expected = 5;
    REQUIRE(maximum_resilience(N, edges) == expected);
}

TEST_CASE("Component and isolated node") {
    int N = 3;
    // One edge connecting node 0 and node 1; node 2 is isolated.
    vector<tuple<int, int, int>> edges = {
        make_tuple(0, 1, 4)
    };
    // Two sub-networks: one with an edge of cost 4, and one isolated node (resilience INF represented as INT_MAX).
    // Overall resilience is the minimum, i.e., min(4, INT_MAX) = 4.
    int expected = 4;
    REQUIRE(maximum_resilience(N, edges) == expected);
}

TEST_CASE("Multiple connected components with finite resiliences") {
    int N = 5;
    // Component 1: nodes {0, 1} with an edge cost 10.
    // Component 2: nodes {2, 3, 4} with edges, costs: 7, 3 and 8.
    vector<tuple<int, int, int>> edges = {
        make_tuple(0, 1, 10),
        make_tuple(2, 3, 7),
        make_tuple(3, 4, 3),
        make_tuple(2, 4, 8)
    };
    // Resilience of component 1 is 10.
    // Resilience of component 2 is min(7,3,8) = 3.
    // Overall resilience is min(10, 3) = 3.
    int expected = 3;
    REQUIRE(maximum_resilience(N, edges) == expected);
}

TEST_CASE("Two non-trivial components with different edge sets") {
    int N = 6;
    // Component 1: nodes {0, 1, 2} with edges: (0,1,15), (1,2,20), (0,2,10)
    // Component 2: nodes {3, 4, 5} with edges: (3,4,5), (4,5,12)
    vector<tuple<int, int, int>> edges = {
        make_tuple(0, 1, 15),
        make_tuple(1, 2, 20),
        make_tuple(0, 2, 10),
        make_tuple(3, 4, 5),
        make_tuple(4, 5, 12)
    };
    // Resilience of component 1 is min(15,20,10) = 10.
    // Resilience of component 2 is min(5,12) = 5.
    // Overall resilience is min(10, 5) = 5.
    int expected = 5;
    REQUIRE(maximum_resilience(N, edges) == expected);
}

TEST_CASE("Graph with all high cost edges yields high resilience") {
    int N = 4;
    // A connected graph where the minimum cost within the only component is high
    vector<tuple<int, int, int>> edges = {
        make_tuple(0, 1, 100),
        make_tuple(1, 2, 150),
        make_tuple(2, 3, 200),
        make_tuple(0, 3, 120)
    };
    // Only one connected component. Its resilience is min(100,150,200,120)=100.
    int expected = 100;
    REQUIRE(maximum_resilience(N, edges) == expected);
}

TEST_CASE("Graph with isolated nodes mixed with multi-node component") {
    int N = 7;
    // Component 1: nodes {0,1,2} with edges: (0,1,50), (1,2,60)
    // Nodes 3, 4, 5, 6 are isolated.
    vector<tuple<int, int, int>> edges = {
        make_tuple(0, 1, 50),
        make_tuple(1, 2, 60)
    };
    // Component 1 resilience = 50.
    // Each isolated node has resilience = INT_MAX.
    // Overall resilience = min(50, INT_MAX, INT_MAX, INT_MAX, INT_MAX) = 50.
    int expected = 50;
    REQUIRE(maximum_resilience(N, edges) == expected);
}