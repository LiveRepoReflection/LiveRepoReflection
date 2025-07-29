#include "catch.hpp"
#include "task_scheduler.h"
#include <vector>

TEST_CASE("Basic sequential tasks") {
    std::vector<int> duration = {3, 2, 4};
    std::vector<int> resource_requirement = {2, 3, 2};
    std::vector<std::vector<int>> dependencies = {{}, {0}, {1}};
    int resource_limit = 4;

    auto result = task_scheduler::schedule(3, duration, resource_requirement, dependencies, resource_limit);
    
    REQUIRE(result.size() == 3);
    REQUIRE(result[0] == 0);
    REQUIRE(result[1] == 3);
    REQUIRE(result[2] == 5);
}

TEST_CASE("Parallel tasks with sufficient resources") {
    std::vector<int> duration = {2, 3, 2};
    std::vector<int> resource_requirement = {2, 2, 2};
    std::vector<std::vector<int>> dependencies = {{}, {}, {}};
    int resource_limit = 6;

    auto result = task_scheduler::schedule(3, duration, resource_requirement, dependencies, resource_limit);
    
    REQUIRE(result.size() == 3);
    REQUIRE(result[0] == 0);
    REQUIRE(result[1] == 0);
    REQUIRE(result[2] == 0);
}

TEST_CASE("Resource constraint prevents parallel execution") {
    std::vector<int> duration = {2, 3, 2};
    std::vector<int> resource_requirement = {3, 3, 3};
    std::vector<std::vector<int>> dependencies = {{}, {}, {}};
    int resource_limit = 3;

    auto result = task_scheduler::schedule(3, duration, resource_requirement, dependencies, resource_limit);
    
    REQUIRE(result.size() == 3);
    int makespan = 0;
    for(size_t i = 0; i < result.size(); i++) {
        makespan = std::max(makespan, result[i] + duration[i]);
    }
    REQUIRE(makespan == 7);
}

TEST_CASE("Cyclic dependencies") {
    std::vector<int> duration = {2, 2, 2};
    std::vector<int> resource_requirement = {1, 1, 1};
    std::vector<std::vector<int>> dependencies = {{1}, {2}, {0}};
    int resource_limit = 3;

    auto result = task_scheduler::schedule(3, duration, resource_requirement, dependencies, resource_limit);
    
    REQUIRE(result.empty());
}

TEST_CASE("Complex dependency chain") {
    std::vector<int> duration = {2, 3, 4, 2, 3};
    std::vector<int> resource_requirement = {2, 2, 2, 2, 2};
    std::vector<std::vector<int>> dependencies = {{}, {0}, {1}, {2}, {1, 3}};
    int resource_limit = 4;

    auto result = task_scheduler::schedule(5, duration, resource_requirement, dependencies, resource_limit);
    
    REQUIRE(result.size() == 5);
    for(size_t i = 0; i < dependencies.size(); i++) {
        for(int dep : dependencies[i]) {
            REQUIRE(result[i] >= result[dep] + duration[dep]);
        }
    }
}

TEST_CASE("Insufficient resources") {
    std::vector<int> duration = {2, 3, 2};
    std::vector<int> resource_requirement = {5, 5, 5};
    std::vector<std::vector<int>> dependencies = {{}, {}, {}};
    int resource_limit = 4;

    auto result = task_scheduler::schedule(3, duration, resource_requirement, dependencies, resource_limit);
    
    REQUIRE(result.empty());
}

TEST_CASE("Single task") {
    std::vector<int> duration = {5};
    std::vector<int> resource_requirement = {3};
    std::vector<std::vector<int>> dependencies = {{}};
    int resource_limit = 3;

    auto result = task_scheduler::schedule(1, duration, resource_requirement, dependencies, resource_limit);
    
    REQUIRE(result.size() == 1);
    REQUIRE(result[0] == 0);
}

TEST_CASE("Maximum size input") {
    std::vector<int> duration(100, 1);
    std::vector<int> resource_requirement(100, 1);
    std::vector<std::vector<int>> dependencies(100);
    for(int i = 1; i < 100; i++) {
        dependencies[i] = {i-1};
    }
    int resource_limit = 100;

    auto result = task_scheduler::schedule(100, duration, resource_requirement, dependencies, resource_limit);
    
    REQUIRE(result.size() == 100);
    for(int i = 1; i < 100; i++) {
        REQUIRE(result[i] > result[i-1]);
    }
}

TEST_CASE("Complex resource sharing") {
    std::vector<int> duration = {3, 2, 4, 3, 2};
    std::vector<int> resource_requirement = {3, 2, 2, 3, 1};
    std::vector<std::vector<int>> dependencies = {{}, {}, {0, 1}, {2}, {2}};
    int resource_limit = 5;

    auto result = task_scheduler::schedule(5, duration, resource_requirement, dependencies, resource_limit);
    
    REQUIRE(result.size() == 5);
    // Verify resource constraints
    std::vector<int> timeline(20, 0);  // Assuming makespan won't exceed 20
    for(size_t i = 0; i < result.size(); i++) {
        for(int t = result[i]; t < result[i] + duration[i]; t++) {
            timeline[t] += resource_requirement[i];
            REQUIRE(timeline[t] <= resource_limit);
        }
    }
}