#include "task_scheduler.h"
#include "catch.hpp"
#include <vector>

TEST_CASE("Single task with no dependencies", "[task_scheduler]") {
    std::vector<int> id = {1};
    std::vector<int> duration = {100};
    std::vector<int> deadline = {200};
    std::vector<std::vector<int>> dependencies = {{}};
    
    REQUIRE(task_scheduler::get_max_completed_tasks(1, id, duration, deadline, dependencies) == 1);
}

TEST_CASE("Two independent tasks, both can complete", "[task_scheduler]") {
    std::vector<int> id = {1, 2};
    std::vector<int> duration = {100, 100};
    std::vector<int> deadline = {200, 300};
    std::vector<std::vector<int>> dependencies = {{}, {}};
    
    REQUIRE(task_scheduler::get_max_completed_tasks(2, id, duration, deadline, dependencies) == 2);
}

TEST_CASE("Two tasks with dependency, both can complete", "[task_scheduler]") {
    std::vector<int> id = {1, 2};
    std::vector<int> duration = {100, 100};
    std::vector<int> deadline = {200, 300};
    std::vector<std::vector<int>> dependencies = {{}, {1}};
    
    REQUIRE(task_scheduler::get_max_completed_tasks(2, id, duration, deadline, dependencies) == 2);
}

TEST_CASE("Two tasks with dependency, second task cannot complete", "[task_scheduler]") {
    std::vector<int> id = {1, 2};
    std::vector<int> duration = {100, 100};
    std::vector<int> deadline = {200, 150};
    std::vector<std::vector<int>> dependencies = {{}, {1}};
    
    REQUIRE(task_scheduler::get_max_completed_tasks(2, id, duration, deadline, dependencies) == 1);
}

TEST_CASE("Complex dependency chain", "[task_scheduler]") {
    std::vector<int> id = {1, 2, 3, 4};
    std::vector<int> duration = {100, 200, 150, 100};
    std::vector<int> deadline = {350, 500, 400, 600};
    std::vector<std::vector<int>> dependencies = {{}, {1}, {1}, {2, 3}};
    
    REQUIRE(task_scheduler::get_max_completed_tasks(4, id, duration, deadline, dependencies) == 3);
}

TEST_CASE("Impossible schedule due to tight deadlines", "[task_scheduler]") {
    std::vector<int> id = {1, 2, 3};
    std::vector<int> duration = {100, 100, 100};
    std::vector<int> deadline = {50, 50, 50};
    std::vector<std::vector<int>> dependencies = {{}, {}, {}};
    
    REQUIRE(task_scheduler::get_max_completed_tasks(3, id, duration, deadline, dependencies) == 0);
}

TEST_CASE("Complex dependency graph with multiple paths", "[task_scheduler]") {
    std::vector<int> id = {1, 2, 3, 4, 5};
    std::vector<int> duration = {100, 100, 100, 100, 100};
    std::vector<int> deadline = {200, 300, 400, 500, 600};
    std::vector<std::vector<int>> dependencies = {{}, {1}, {1}, {2}, {3, 4}};
    
    REQUIRE(task_scheduler::get_max_completed_tasks(5, id, duration, deadline, dependencies) == 5);
}

TEST_CASE("Maximum size input test", "[task_scheduler]") {
    std::vector<int> id(1000);
    std::vector<int> duration(1000);
    std::vector<int> deadline(1000);
    std::vector<std::vector<int>> dependencies(1000);
    
    for(int i = 0; i < 1000; i++) {
        id[i] = i + 1;
        duration[i] = 1;
        deadline[i] = 1000000;
        dependencies[i] = {};
    }
    
    REQUIRE(task_scheduler::get_max_completed_tasks(1000, id, duration, deadline, dependencies) == 1000);
}

TEST_CASE("Empty input test", "[task_scheduler]") {
    std::vector<int> id;
    std::vector<int> duration;
    std::vector<int> deadline;
    std::vector<std::vector<int>> dependencies;
    
    REQUIRE(task_scheduler::get_max_completed_tasks(0, id, duration, deadline, dependencies) == 0);
}