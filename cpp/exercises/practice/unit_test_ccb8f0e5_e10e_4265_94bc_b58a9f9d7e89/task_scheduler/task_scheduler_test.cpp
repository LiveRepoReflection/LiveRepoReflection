#include "catch.hpp"
#include "task_scheduler.h"
#include <vector>

TEST_CASE("Single task with no dependencies meets deadline", "[task_scheduler]") {
    int N = 1;
    std::vector<int> id = {1};
    std::vector<int> duration = {10};
    std::vector<int> deadline = {10};
    std::vector<std::vector<int>> dependencies = {{}};

    int result = task_scheduler::schedule_tasks(N, id, duration, deadline, dependencies);
    // The only task finishes exactly at time 10.
    REQUIRE(result == 10);
}

TEST_CASE("Chain dependencies schedule correctly", "[task_scheduler]") {
    int N = 3;
    std::vector<int> id = {1, 2, 3};
    std::vector<int> duration = {10, 20, 30};
    std::vector<int> deadline = {50, 60, 70};
    std::vector<std::vector<int>> dependencies = {
        {},
        {1},
        {2}
    };

    int result = task_scheduler::schedule_tasks(N, id, duration, deadline, dependencies);
    // Optimal schedule: Task1 (0-10), Task2 (10-30), Task3 (30-60)
    REQUIRE(result == 60);
}

TEST_CASE("Impossible due to deadline miss", "[task_scheduler]") {
    int N = 2;
    std::vector<int> id = {1, 2};
    std::vector<int> duration = {10, 10};
    std::vector<int> deadline = {5, 25}; // Task 1 misses deadline.
    std::vector<std::vector<int>> dependencies = {
        {},
        {}  // No dependencies.
    };

    int result = task_scheduler::schedule_tasks(N, id, duration, deadline, dependencies);
    // Since task 1 cannot finish by its deadline, scheduling is impossible.
    REQUIRE(result == -1);
}

TEST_CASE("Parallel execution with independent tasks", "[task_scheduler]") {
    int N = 4;
    std::vector<int> id = {1, 2, 3, 4};
    std::vector<int> duration = {10, 15, 20, 30};
    std::vector<int> deadline = {20, 40, 50, 60};
    // Tasks 1 and 2 have no dependencies. Task 3 depends on 1, Task 4 depends on 2.
    std::vector<std::vector<int>> dependencies = {
        {},    // Task 1
        {},    // Task 2
        {1},   // Task 3
        {2}    // Task 4
    };

    int result = task_scheduler::schedule_tasks(N, id, duration, deadline, dependencies);
    // Optimal schedule: 
    // Task1: 0-10, then Task3: 10-30.
    // Task2: 0-15, then Task4: 15-45.
    // Makespan is max(30, 45) = 45.
    REQUIRE(result == 45);
}

TEST_CASE("Complex branching dependencies", "[task_scheduler]") {
    int N = 5;
    std::vector<int> id = {1, 2, 3, 4, 5};
    // Task durations for each task.
    std::vector<int> duration = {5, 10, 5, 10, 5};
    // Deadlines such that each task should finish before its assigned time.
    std::vector<int> deadline = {15, 30, 20, 40, 50};
    // Dependency graph:
    // Task 1: no dependencies.
    // Task 2: depends on 1.
    // Task 3: depends on 1.
    // Task 4: depends on 2 and 3.
    // Task 5: depends on 3.
    std::vector<std::vector<int>> dependencies = {
        {},      // Task 1
        {1},     // Task 2
        {1},     // Task 3
        {2, 3},  // Task 4
        {3}      // Task 5
    };

    int result = task_scheduler::schedule_tasks(N, id, duration, deadline, dependencies);
    // Optimal schedule:
    // Task1: 0-5, Task2 and Task3 can start at 5 concurrently.
    // Task2: 5-15, Task3: 5-10.
    // Task4: can start at 15 (after Task2 and Task3 finish) and finishes at 25.
    // Task5: can start at 10 (after Task3) and finishes at 15.
    // Overall makespan = 25.
    REQUIRE(result == 25);
}