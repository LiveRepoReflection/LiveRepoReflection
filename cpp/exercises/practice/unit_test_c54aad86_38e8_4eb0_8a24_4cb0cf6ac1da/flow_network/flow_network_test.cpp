#include "catch.hpp"
#include "flow_network.h"
#include <vector>
#include <tuple>
#include <algorithm>
#include <cmath>

using std::vector;
using std::tuple;
using std::get;
using std::sort;

// A helper comparator to sort results by (u,v)
bool compareTuples(const tuple<int, int, double>& a, const tuple<int, int, double>& b) {
    if(get<0>(a) != get<0>(b))
        return get<0>(a) < get<0>(b);
    return get<1>(a) < get<1>(b);
}

// A helper function to compare two vectors of tuples with tolerance for double comparison.
bool compareResults(const vector<tuple<int, int, double>>& res,
                    const vector<tuple<int, int, double>>& expected,
                    double tol = 1e-6) {
    if(res.size() != expected.size())
        return false;
    vector<tuple<int, int, double>> r = res;
    vector<tuple<int, int, double>> e = expected;
    sort(r.begin(), r.end(), compareTuples);
    sort(e.begin(), e.end(), compareTuples);
    for (size_t i = 0; i < r.size(); ++i) {
        if(get<0>(r[i]) != get<0>(e[i]) ||
           get<1>(r[i]) != get<1>(e[i]) ||
           std::fabs(get<2>(r[i]) - get<2>(e[i])) > tol)
            return false;
    }
    return true;
}

TEST_CASE("Single commodity simple network", "[flow_network]") {
    int N = 4;
    vector<tuple<int, int, double>> edges = {
        {0, 1, 1.0},
        {0, 2, 2.0},
        {1, 2, 1.0},
        {1, 3, 3.0},
        {2, 3, 1.0}
    };
    vector<tuple<int, int, double>> commodities = {
        {0, 3, 2.0}
    };
    // Expected one possible solution:
    vector<tuple<int, int, double>> expected = {
        {0, 1, 2.0},
        {0, 2, 0.0},
        {1, 2, 0.0},
        {1, 3, 2.0},
        {2, 3, 0.0}
    };

    auto result = flow_network::design_network(N, edges, commodities);
    REQUIRE(compareResults(result, expected));
}

TEST_CASE("Multiple commodities on single edge", "[flow_network]") {
    int N = 2;
    vector<tuple<int, int, double>> edges = {
        {0, 1, 1.0}
    };
    vector<tuple<int, int, double>> commodities = {
        {0, 1, 5.0},
        {0, 1, 5.0}
    };
    vector<tuple<int, int, double>> expected = {
        {0, 1, 10.0}
    };

    auto result = flow_network::design_network(N, edges, commodities);
    REQUIRE(compareResults(result, expected));
}

TEST_CASE("Infeasible network", "[flow_network]") {
    int N = 2;
    vector<tuple<int, int, double>> edges = {
        {0, 1, 1.0}
    };
    vector<tuple<int, int, double>> commodities = {
        {0, 1, 5.0},
        {1, 0, 5.0}
    };
    // Infeasible solution should return an empty vector.
    auto result = flow_network::design_network(N, edges, commodities);
    REQUIRE(result.empty());
}

TEST_CASE("Complex network with alternative routes", "[flow_network]") {
    int N = 4;
    vector<tuple<int, int, double>> edges = {
        {0, 1, 1.0},
        {1, 3, 2.0},
        {0, 2, 1.0},
        {2, 3, 2.0},
        {1, 2, 0.5},
        {2, 1, 0.5}
    };
    vector<tuple<int, int, double>> commodities = {
        {0, 3, 3.0}
    };
    // One potential optimal solution:
    vector<tuple<int, int, double>> expected = {
        {0, 1, 1.5},
        {1, 3, 1.5},
        {0, 2, 1.5},
        {2, 3, 1.5},
        {1, 2, 0.0},
        {2, 1, 0.0}
    };

    auto result = flow_network::design_network(N, edges, commodities);
    REQUIRE(compareResults(result, expected));
}

TEST_CASE("No commodity demand", "[flow_network]") {
    int N = 3;
    vector<tuple<int, int, double>> edges = {
        {0, 1, 1.0},
        {1, 2, 2.0}
    };
    vector<tuple<int, int, double>> commodities; // empty
    // With no commodities, optimal capacities are all 0.
    vector<tuple<int, int, double>> expected = {
        {0, 1, 0.0},
        {1, 2, 0.0}
    };

    auto result = flow_network::design_network(N, edges, commodities);
    REQUIRE(compareResults(result, expected));
}