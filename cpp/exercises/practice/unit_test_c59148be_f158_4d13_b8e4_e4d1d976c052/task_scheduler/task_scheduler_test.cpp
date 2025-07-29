#include "task_scheduler.h"
#include "catch.hpp"
#include <vector>
#include <tuple>

using namespace std;

TEST_CASE("Basic case with no late tasks") {
    int N = 4;
    int K = 2;
    vector<tuple<int, int, int, vector<int>>> tasks = {
        {1, 2, 5, {}},
        {2, 3, 7, {1}},
        {3, 1, 4, {}},
        {4, 2, 9, {2, 3}}
    };
    
    auto result = schedule_tasks(N, K, tasks);
    REQUIRE(result == make_pair(0, 0));
}

TEST_CASE("Single worker case") {
    int N = 3;
    int K = 1;
    vector<tuple<int, int, int, vector<int>>> tasks = {
        {1, 2, 3, {}},
        {2, 1, 4, {1}},
        {3, 1, 6, {2}}
    };
    
    auto result = schedule_tasks(N, K, tasks);
    REQUIRE(result == make_pair(0, 0));
}

TEST_CASE("Impossible case with circular dependencies") {
    int N = 3;
    int K = 2;
    vector<tuple<int, int, int, vector<int>>> tasks = {
        {1, 2, 5, {3}},
        {2, 3, 7, {1}},
        {3, 1, 4, {2}}
    };
    
    auto result = schedule_tasks(N, K, tasks);
    REQUIRE(result == make_pair(-1, -1));
}

TEST_CASE("Multiple late tasks case") {
    int N = 5;
    int K = 2;
    vector<tuple<int, int, int, vector<int>>> tasks = {
        {1, 3, 3, {}},
        {2, 2, 4, {}},
        {3, 4, 6, {1}},
        {4, 1, 5, {2}},
        {5, 2, 8, {3, 4}}
    };
    
    auto result = schedule_tasks(N, K, tasks);
    REQUIRE(result.first == 2);
    REQUIRE(result.second > 0);
}

TEST_CASE("Large number of independent tasks") {
    int N = 10;
    int K = 3;
    vector<tuple<int, int, int, vector<int>>> tasks;
    for (int i = 1; i <= N; ++i) {
        tasks.emplace_back(i, 1, i, vector<int>{});
    }
    
    auto result = schedule_tasks(N, K, tasks);
    REQUIRE(result == make_pair(0, 0));
}

TEST_CASE("Complex dependency tree") {
    int N = 6;
    int K = 2;
    vector<tuple<int, int, int, vector<int>>> tasks = {
        {1, 2, 10, {}},
        {2, 3, 15, {1}},
        {3, 1, 20, {1}},
        {4, 4, 25, {2, 3}},
        {5, 2, 30, {4}},
        {6, 3, 35, {4}}
    };
    
    auto result = schedule_tasks(N, K, tasks);
    REQUIRE(result == make_pair(0, 0));
}

#if defined(EXERCISM_RUN_ALL_TESTS)
TEST_CASE("Edge case with single task") {
    int N = 1;
    int K = 1;
    vector<tuple<int, int, int, vector<int>>> tasks = {
        {1, 5, 10, {}}
    };
    
    auto result = schedule_tasks(N, K, tasks);
    REQUIRE(result == make_pair(0, 0));
}

TEST_CASE("More workers than tasks") {
    int N = 3;
    int K = 5;
    vector<tuple<int, int, int, vector<int>>> tasks = {
        {1, 2, 5, {}},
        {2, 3, 6, {}},
        {3, 1, 4, {}}
    };
    
    auto result = schedule_tasks(N, K, tasks);
    REQUIRE(result == make_pair(0, 0));
}

TEST_CASE("Tight deadlines") {
    int N = 4;
    int K = 2;
    vector<tuple<int, int, int, vector<int>>> tasks = {
        {1, 3, 3, {}},
        {2, 2, 2, {}},
        {3, 4, 7, {1}},
        {4, 1, 5, {2}}
    };
    
    auto result = schedule_tasks(N, K, tasks);
    REQUIRE(result.first >= 1);
}
#endif