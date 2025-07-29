#include "catch.hpp"
#include "task_scheduler.h"
#include <vector>

using std::vector;

TEST_CASE("Single task, no dependencies and no penalty", "[task_scheduler]") {
    vector<int> duration = {10};
    vector<int> deadline = {20};
    vector<vector<int>> dependencies = {{}};
    int result = task_scheduler::min_total_penalty(duration, deadline, dependencies);
    // The task finishes at time 10 which is before the deadline of 20, so penalty is 0.
    REQUIRE(result == 0);
}

TEST_CASE("Chain dependencies with penalty", "[task_scheduler]") {
    // Tasks 0 -> 1 -> 2
    // Task0: duration 50, deadline 30 -> penalty = 20 as it finishes at 50.
    // Task1: duration 10, deadline 80 -> finishes at 60, penalty = 0.
    // Task2: duration 20, deadline 100 -> finishes at 80, penalty = 0.
    vector<int> duration = {50, 10, 20};
    vector<int> deadline = {30, 80, 100};
    vector<vector<int>> dependencies = {
        {},    // Task 0 has no dependencies.
        {0},   // Task 1 depends on Task 0.
        {1}    // Task 2 depends on Task 1.
    };
    int result = task_scheduler::min_total_penalty(duration, deadline, dependencies);
    // Expected total penalty = 20 (only task0 incurs penalty)
    REQUIRE(result == 20);
}

TEST_CASE("Multiple independent tasks with reordering", "[task_scheduler]") {
    // Three independent tasks where order can be optimized.
    // Task0: duration=30, deadline=25 -> penalty if delayed = (finish time - 25)
    // Task1: duration=10, deadline=50 -> penalty if finish > 50
    // Task2: duration=20, deadline=30 -> penalty if finish > 30
    // Optimal ordering gives total penalty = 35.
    vector<int> duration = {30, 10, 20};
    vector<int> deadline = {25, 50, 30};
    vector<vector<int>> dependencies = {
        {}, // Task0 has no dependencies.
        {}, // Task1 has no dependencies.
        {}  // Task2 has no dependencies.
    };
    int result = task_scheduler::min_total_penalty(duration, deadline, dependencies);
    REQUIRE(result == 35);
}

TEST_CASE("Parallel dependencies with merging", "[task_scheduler]") {
    // Graph structure:
    // Task0: no dependency, duration=10, deadline=10 -> finishes at 10, penalty=0.
    // Task1: depends on Task0, duration=20, deadline=25 -> if scheduled next, finishes at 30, penalty=5.
    // Task2: depends on Task0, duration=5, deadline=100 -> if scheduled after task0, finishes at 15, penalty=0.
    // Task3: depends on Task1 and Task2, duration=15, deadline=40 -> finishes after both are complete.
    // Optimal scheduling: Task0, Task1, Task2, Task3 results: Task0(10), Task1(30, penalty=5), Task2(35, no penalty), Task3(50, penalty=10) -> total = 15.
    // Alternatively, if Task2 is scheduled before Task1, penalty increases.
    vector<int> duration = {10, 20, 5, 15};
    vector<int> deadline = {10, 25, 100, 40};
    vector<vector<int>> dependencies = {
        {},      // Task0 no dependencies.
        {0},     // Task1 depends on Task0.
        {0},     // Task2 depends on Task0.
        {1, 2}   // Task3 depends on Task1 and Task2.
    };
    int result = task_scheduler::min_total_penalty(duration, deadline, dependencies);
    REQUIRE(result == 15);
}

TEST_CASE("Complex scenario with mixed dependencies", "[task_scheduler]") {
    // This test contains a more complex dependency graph:
    // Task0: duration=15, deadline=20
    // Task1: duration=25, deadline=50, depends on Task0.
    // Task2: duration=10, deadline=25, depends on Task0.
    // Task3: duration=20, deadline=60, depends on Task1 and Task2.
    // Task4: duration=30, deadline=100, depends on Task2.
    // Expected schedule example:
    // - Task0: [0,15] => penalty = max(15-20, 0) = 0.
    // - Task2: [15,25] => penalty = max(25-25, 0) = 0.
    // - Task1: [25,50] => penalty = max(50-50, 0) = 0.
    // - Task3: [50,70] => penalty = max(70-60, 10) = 10.
    // - Task4: [70,100] => penalty = max(100-100, 0) = 0.
    // Total penalty expected = 10.
    vector<int> duration = {15, 25, 10, 20, 30};
    vector<int> deadline = {20, 50, 25, 60, 100};
    vector<vector<int>> dependencies = {
        {},      // Task0 no dependencies.
        {0},     // Task1 depends on Task0.
        {0},     // Task2 depends on Task0.
        {1, 2},  // Task3 depends on Task1 and Task2.
        {2}      // Task4 depends on Task2.
    };
    int result = task_scheduler::min_total_penalty(duration, deadline, dependencies);
    REQUIRE(result == 10);
}
  
// Main runner for catch if needed to compile tests as standalone
#define CATCH_CONFIG_MAIN
#include "catch.hpp"