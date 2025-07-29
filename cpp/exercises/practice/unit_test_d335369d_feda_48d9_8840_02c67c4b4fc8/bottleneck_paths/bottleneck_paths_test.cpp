#include "bottleneck_paths.h"
#include "catch.hpp"
#include <vector>
#include <tuple>
#include <algorithm>

using std::vector;
using std::tuple;

namespace {
    // Helper function to sort results by destination.
    void sort_results(vector<bottleneck_paths::Result>& results) {
        std::sort(results.begin(), results.end(), [](const bottleneck_paths::Result &a, const bottleneck_paths::Result &b) {
            return a.destination < b.destination;
        });
    }
}

TEST_CASE("Single source, linear graph", "[bottleneck_paths]") {
    int N = 4;
    // Graph: 1->2 (5), 2->3 (3), 3->4 (4)
    vector<tuple<int, int, int>> edges = {
        {1, 2, 5},
        {2, 3, 3},
        {3, 4, 4}
    };
    vector<int> sources = {1};

    // Expected:
    // City 2: bottleneck = 5, minimal source set = {1}
    // City 3: bottleneck = 3, minimal source set = {1}
    // City 4: bottleneck = 3, minimal source set = {1}
    vector<bottleneck_paths::Result> results = bottleneck_paths::compute_bottleneck_paths(N, edges, sources);
    sort_results(results);

    REQUIRE(results.size() == 3);

    // Validate City 2
    auto res2 = results[0];
    REQUIRE(res2.destination == 2);
    REQUIRE(res2.max_bottleneck_capacity == 5);
    std::sort(res2.sources.begin(), res2.sources.end());
    REQUIRE(res2.sources == vector<int>({1}));

    // Validate City 3
    auto res3 = results[1];
    REQUIRE(res3.destination == 3);
    REQUIRE(res3.max_bottleneck_capacity == 3);
    std::sort(res3.sources.begin(), res3.sources.end());
    REQUIRE(res3.sources == vector<int>({1}));

    // Validate City 4
    auto res4 = results[2];
    REQUIRE(res4.destination == 4);
    REQUIRE(res4.max_bottleneck_capacity == 3);
    std::sort(res4.sources.begin(), res4.sources.end());
    REQUIRE(res4.sources == vector<int>({1}));
}

TEST_CASE("Multiple sources with different optimal paths", "[bottleneck_paths]") {
    int N = 5;
    // Graph:
    // 1 -> 3 (5)
    // 2 -> 3 (7)
    // 3 -> 4 (4)
    // 2 -> 5 (6)
    // 4 -> 5 (10)
    vector<tuple<int, int, int>> edges = {
        {1, 3, 5},
        {2, 3, 7},
        {3, 4, 4},
        {2, 5, 6},
        {4, 5, 10}
    };
    vector<int> sources = {1, 2};

    // Expected:
    // City 3:
    //    - From source 1: capacity = 5.
    //    - From source 2: capacity = 7.
    // Maximum bottleneck = 7, minimal source set = {2}.
    //
    // City 4:
    //    - From source 1: 1 -> 3 -> 4: min(5,4) = 4.
    //    - From source 2: 2 -> 3 -> 4: min(7,4) = 4.
    // Maximum bottleneck = 4, minimal set could be {1}, {2} or {1, 2}.
    //
    // City 5:
    //    - From source 1: 1 -> 3 -> 4 -> 5: min(5,4,10)=4.
    //    - From source 2: direct 2 -> 5: capacity = 6.
    // Maximum bottleneck = 6, minimal source set = {2}.
    vector<bottleneck_paths::Result> results = bottleneck_paths::compute_bottleneck_paths(N, edges, sources);
    sort_results(results);

    REQUIRE(results.size() == 3);

    // Validate City 3
    auto res3 = results[0];
    REQUIRE(res3.destination == 3);
    REQUIRE(res3.max_bottleneck_capacity == 7);
    std::sort(res3.sources.begin(), res3.sources.end());
    REQUIRE(res3.sources == vector<int>({2}));

    // Validate City 4
    auto res4 = results[1];
    REQUIRE(res4.destination == 4);
    REQUIRE(res4.max_bottleneck_capacity == 4);
    // The minimal source set can be either {1}, {2} or {1, 2}.
    REQUIRE_FALSE(res4.sources.empty());
    for (auto s : res4.sources) {
        REQUIRE((s == 1 || s == 2));
    }
    vector<vector<int>> valid_options = {{1}, {2}, {1, 2}};
    bool valid = false;
    vector<int> sorted_sources = res4.sources;
    std::sort(sorted_sources.begin(), sorted_sources.end());
    for (auto &opt : valid_options) {
        vector<int> temp = opt;
        std::sort(temp.begin(), temp.end());
        if (temp == sorted_sources) {
            valid = true;
            break;
        }
    }
    REQUIRE(valid);

    // Validate City 5
    auto res5 = results[2];
    REQUIRE(res5.destination == 5);
    REQUIRE(res5.max_bottleneck_capacity == 6);
    std::sort(res5.sources.begin(), res5.sources.end());
    REQUIRE(res5.sources == vector<int>({2}));
}

TEST_CASE("Cycle and unreachable nodes", "[bottleneck_paths]") {
    int N = 6;
    // Graph:
    // Cycle: 1 -> 2 (10), 2 -> 3 (5), 3 -> 1 (7)
    // Additional edges: 2 -> 4 (6), 4 -> 5 (8)
    // Node 6 is disconnected.
    vector<tuple<int, int, int>> edges = {
        {1, 2, 10},
        {2, 3, 5},
        {3, 1, 7},
        {2, 4, 6},
        {4, 5, 8}
    };
    vector<int> sources = {1};

    // Expected:
    // City 2: 1 -> 2, capacity = 10.
    // City 3: 1 -> 2 -> 3, capacity = min(10,5) = 5.
    // City 4: 1 -> 2 -> 4, capacity = min(10,6) = 6.
    // City 5: 1 -> 2 -> 4 -> 5, capacity = min(10,6,8) = 6.
    // City 6: unreachable, capacity = 0.
    vector<bottleneck_paths::Result> results = bottleneck_paths::compute_bottleneck_paths(N, edges, sources);
    sort_results(results);

    REQUIRE(results.size() == 5);

    // Validate City 2
    auto res2 = results[0];
    REQUIRE(res2.destination == 2);
    REQUIRE(res2.max_bottleneck_capacity == 10);
    REQUIRE(res2.sources == vector<int>({1}));

    // Validate City 3
    auto res3 = results[1];
    REQUIRE(res3.destination == 3);
    REQUIRE(res3.max_bottleneck_capacity == 5);
    REQUIRE(res3.sources == vector<int>({1}));

    // Validate City 4
    auto res4 = results[2];
    REQUIRE(res4.destination == 4);
    REQUIRE(res4.max_bottleneck_capacity == 6);
    REQUIRE(res4.sources == vector<int>({1}));

    // Validate City 5
    auto res5 = results[3];
    REQUIRE(res5.destination == 5);
    REQUIRE(res5.max_bottleneck_capacity == 6);
    REQUIRE(res5.sources == vector<int>({1}));

    // Validate City 6 (unreachable)
    auto res6 = results[4];
    REQUIRE(res6.destination == 6);
    REQUIRE(res6.max_bottleneck_capacity == 0);
    REQUIRE(res6.sources.empty());
}

TEST_CASE("Multiple paths with identical bottlenecks", "[bottleneck_paths]") {
    int N = 4;
    // Graph:
    // 1 -> 2 (5), 1 -> 3 (5), 2 -> 4 (5), 3 -> 4 (5)
    vector<tuple<int, int, int>> edges = {
        {1, 2, 5},
        {1, 3, 5},
        {2, 4, 5},
        {3, 4, 5}
    };
    vector<int> sources = {1};

    // Expected:
    // City 2: capacity = 5, source = {1}.
    // City 3: capacity = 5, source = {1}.
    // City 4: capacity = 5, source = {1} (regardless of which path is taken).
    vector<bottleneck_paths::Result> results = bottleneck_paths::compute_bottleneck_paths(N, edges, sources);
    sort_results(results);

    REQUIRE(results.size() == 3);

    // Validate City 2
    auto res2 = results[0];
    REQUIRE(res2.destination == 2);
    REQUIRE(res2.max_bottleneck_capacity == 5);
    REQUIRE(res2.sources == vector<int>({1}));

    // Validate City 3
    auto res3 = results[1];
    REQUIRE(res3.destination == 3);
    REQUIRE(res3.max_bottleneck_capacity == 5);
    REQUIRE(res3.sources == vector<int>({1}));

    // Validate City 4
    auto res4 = results[2];
    REQUIRE(res4.destination == 4);
    REQUIRE(res4.max_bottleneck_capacity == 5);
    REQUIRE(res4.sources == vector<int>({1}));
}

TEST_CASE("Disconnected graph with multiple sources", "[bottleneck_paths]") {
    int N = 7;
    // Graph:
    // Component 1: 1 -> 2 (10), 2 -> 3 (10)
    // Component 2: 4 -> 5 (15), 5 -> 6 (5)
    // Node 7 is isolated.
    vector<tuple<int, int, int>> edges = {
        {1, 2, 10},
        {2, 3, 10},
        {4, 5, 15},
        {5, 6, 5}
    };
    vector<int> sources = {1, 4};

    // Expected:
    // For Component 1:
    //   City 2: capacity = 10, source = {1}
    //   City 3: capacity = 10, source = {1}
    // For Component 2:
    //   City 5: capacity = 15, source = {4}
    //   City 6: capacity = 5, source = {4}
    // Node 7: unreachable, capacity = 0.
    vector<bottleneck_paths::Result> results = bottleneck_paths::compute_bottleneck_paths(N, edges, sources);
    sort_results(results);

    REQUIRE(results.size() == 5);

    // Validate City 2
    auto res2 = results[0];
    REQUIRE(res2.destination == 2);
    REQUIRE(res2.max_bottleneck_capacity == 10);
    REQUIRE(res2.sources == vector<int>({1}));

    // Validate City 3
    auto res3 = results[1];
    REQUIRE(res3.destination == 3);
    REQUIRE(res3.max_bottleneck_capacity == 10);
    REQUIRE(res3.sources == vector<int>({1}));

    // Validate City 5
    auto res5 = results[2];
    REQUIRE(res5.destination == 5);
    REQUIRE(res5.max_bottleneck_capacity == 15);
    REQUIRE(res5.sources == vector<int>({4}));

    // Validate City 6
    auto res6 = results[3];
    REQUIRE(res6.destination == 6);
    REQUIRE(res6.max_bottleneck_capacity == 5);
    REQUIRE(res6.sources == vector<int>({4}));

    // Validate City 7 (unreachable)
    auto res7 = results[4];
    REQUIRE(res7.destination == 7);
    REQUIRE(res7.max_bottleneck_capacity == 0);
    REQUIRE(res7.sources.empty());
}