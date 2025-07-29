#include "task_scheduler.h"
#include "catch.hpp"
#include <vector>
#include <utility>

using task_scheduler::Task;
using task_scheduler::schedule_tasks;

TEST_CASE("Basic test with single task") {
    std::vector<Task> tasks = {
        Task{1, 5, 3, {}}  // id, duration, resource, dependencies
    };
    REQUIRE(schedule_tasks(1, 10, tasks) == 5);
}

TEST_CASE("Test with example from problem description") {
    std::vector<Task> tasks = {
        Task{1, 5, 3, {}},
        Task{2, 3, 4, {1}},
        Task{3, 2, 5, {1}},
        Task{4, 4, 2, {2, 3}}
    };
    REQUIRE(schedule_tasks(4, 10, tasks) == 12);
}

TEST_CASE("Test with parallel execution possible") {
    std::vector<Task> tasks = {
        Task{1, 3, 2, {}},
        Task{2, 3, 2, {}},
        Task{3, 3, 2, {}}
    };
    REQUIRE(schedule_tasks(3, 6, tasks) == 3);
}

TEST_CASE("Test with resource constraints forcing sequential execution") {
    std::vector<Task> tasks = {
        Task{1, 3, 10, {}},
        Task{2, 3, 10, {}},
        Task{3, 3, 10, {}}
    };
    REQUIRE(schedule_tasks(3, 10, tasks) == 9);
}

TEST_CASE("Test with complex dependencies") {
    std::vector<Task> tasks = {
        Task{1, 2, 3, {}},
        Task{2, 2, 3, {1}},
        Task{3, 2, 3, {1}},
        Task{4, 2, 3, {2, 3}},
        Task{5, 2, 3, {4}},
    };
    REQUIRE(schedule_tasks(5, 10, tasks) == 8);
}

TEST_CASE("Test with tight resource constraints") {
    std::vector<Task> tasks = {
        Task{1, 2, 3, {}},
        Task{2, 2, 2, {}},
        Task{3, 2, 2, {}}
    };
    REQUIRE(schedule_tasks(3, 5, tasks) == 4);
}

TEST_CASE("Test with long dependency chain") {
    std::vector<Task> tasks = {
        Task{1, 1, 1, {}},
        Task{2, 1, 1, {1}},
        Task{3, 1, 1, {2}},
        Task{4, 1, 1, {3}},
        Task{5, 1, 1, {4}}
    };
    REQUIRE(schedule_tasks(5, 10, tasks) == 5);
}

TEST_CASE("Test with fan-out dependencies") {
    std::vector<Task> tasks = {
        Task{1, 2, 2, {}},
        Task{2, 2, 2, {1}},
        Task{3, 2, 2, {1}},
        Task{4, 2, 2, {1}},
        Task{5, 2, 2, {1}}
    };
    REQUIRE(schedule_tasks(5, 4, tasks) == 6);
}

TEST_CASE("Test with maximum constraints") {
    std::vector<Task> tasks;
    for(int i = 1; i <= 10; i++) {
        std::vector<int> deps;
        if(i > 1) deps.push_back(i-1);
        tasks.push_back(Task{i, 1000, 1000, deps});
    }
    REQUIRE(schedule_tasks(10, 1000, tasks) == 10000);
}

TEST_CASE("Test invalid input - empty task list") {
    std::vector<Task> tasks;
    REQUIRE_THROWS_AS(schedule_tasks(0, 10, tasks), std::invalid_argument);
}

TEST_CASE("Test invalid input - resource exceeds limit") {
    std::vector<Task> tasks = {
        Task{1, 5, 15, {}}
    };
    REQUIRE_THROWS_AS(schedule_tasks(1, 10, tasks), std::invalid_argument);
}

TEST_CASE("Test invalid input - circular dependency") {
    std::vector<Task> tasks = {
        Task{1, 2, 2, {2}},
        Task{2, 2, 2, {1}}
    };
    REQUIRE_THROWS_AS(schedule_tasks(2, 10, tasks), std::invalid_argument);
}

TEST_CASE("Test invalid input - dependency on non-existent task") {
    std::vector<Task> tasks = {
        Task{1, 2, 2, {3}},
        Task{2, 2, 2, {}}
    };
    REQUIRE_THROWS_AS(schedule_tasks(2, 10, tasks), std::invalid_argument);
}