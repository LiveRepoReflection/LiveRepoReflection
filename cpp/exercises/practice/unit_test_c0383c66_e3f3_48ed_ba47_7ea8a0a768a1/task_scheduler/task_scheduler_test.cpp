#include "task_scheduler.h"
#include "catch.hpp"
#include <vector>

using namespace std;

TEST_CASE("Simple schedule with dependencies", "[task_scheduler]") {
    // Sample provided: Three tasks with a dependency chain 0 → 1 → 2.
    // Task 0: duration 5, deadline 10, profit 100.
    // Task 1: duration 3, deadline 8, profit 50 (depends on task 0).
    // Task 2: duration 2, deadline 12, profit 75 (depends on tasks 0 and 1).
    // Optimal schedule: Task 0 (0-5), Task 1 (5-8), Task 2 (8-10) yielding profit 225.
    vector<Task> tasks = {
        {0, 5, 10, 100, {}},
        {1, 3, 8, 50, {0}},
        {2, 2, 12, 75, {0, 1}}
    };
    int N = 3;
    int M = 2;
    int result = maxProfit(N, M, tasks);
    REQUIRE(result == 225);
}

TEST_CASE("No dependency, tasks schedulable in parallel", "[task_scheduler]") {
    // Three independent tasks scheduled with enough worker threads
    // All tasks can be executed concurrently without waiting.
    vector<Task> tasks = {
        {0, 2, 10, 20, {}},
        {1, 3, 12, 30, {}},
        {2, 1, 5, 15, {}}
    };
    int N = 3;
    int M = 3;
    int result = maxProfit(N, M, tasks);
    // Expected profit is the sum of all individual profits.
    REQUIRE(result == 20 + 30 + 15);
}

TEST_CASE("Single worker sequential scheduling", "[task_scheduler]") {
    // With a single worker thread, tasks must be scheduled sequentially.
    vector<Task> tasks = {
        {0, 3, 5, 50, {}},
        {1, 2, 7, 40, {}},
        {2, 4, 12, 60, {}}
    };
    int N = 3;
    int M = 1;
    // Optimal schedule: Task 0 (0-3), Task 1 (3-5), Task 2 (5-9) all within deadlines.
    int result = maxProfit(N, M, tasks);
    REQUIRE(result == 50 + 40 + 60);
}

TEST_CASE("Chain dependency with tight deadlines", "[task_scheduler]") {
    // Tasks in a dependency chain where the final task misses its deadline if scheduled.
    vector<Task> tasks = {
        {0, 4, 4, 100, {}},    // Must finish by time 4.
        {1, 3, 8, 80, {0}},     // Must finish by time 8.
        {2, 2, 8, 50, {1}}      // Cannot finish by time 8 if scheduled after task 1.
    };
    int N = 3;
    int M = 1;
    // The best option is to schedule tasks 0 and 1 only.
    int result = maxProfit(N, M, tasks);
    REQUIRE(result == 100 + 80);
}

TEST_CASE("Multiple possible schedules with trade-offs", "[task_scheduler]") {
    // A mix of independent tasks and tasks with dependencies.
    // Task details:
    // Task 0: duration 2, deadline 6, profit 40.
    // Task 1: duration 3, deadline 10, profit 100.
    // Task 2: duration 4, deadline 9, profit 70, depends on task 0.
    // Task 3: duration 1, deadline 5, profit 30, depends on task 0.
    // Task 4: duration 2, deadline 12, profit 60, depends on tasks 1 and 3.
    // One optimal schedule:
    //  - At time 0: Start Task 0 and Task 1 concurrently (M=2).
    //  - At time 2: Task 0 finishes; start Task 3.
    //  - At time 3: Task 1 and Task 3 finish; start Tasks 2 and 4 concurrently.
    //  - Tasks complete within deadlines, yielding total profit = 300.
    vector<Task> tasks = {
        {0, 2, 6, 40, {}},
        {1, 3, 10, 100, {}},
        {2, 4, 9, 70, {0}},
        {3, 1, 5, 30, {0}},
        {4, 2, 12, 60, {1, 3}}
    };
    int N = 5;
    int M = 2;
    int result = maxProfit(N, M, tasks);
    REQUIRE(result == 300);
}

TEST_CASE("Unachievable tasks due to deadlines", "[task_scheduler]") {
    // Tasks where one task has a deadline shorter than its duration,
    // making it impossible to complete on time, so the scheduler should skip it.
    vector<Task> tasks = {
        {0, 5, 4, 100, {}}, // Cannot be completed as duration > deadline.
        {1, 2, 6, 50, {}},
        {2, 1, 3, 30, {}}
    };
    int N = 3;
    int M = 2;
    // Best schedule: Execute tasks 2 and 1 (order: Task 2 then Task 1) to collect profit.
    int result = maxProfit(N, M, tasks);
    REQUIRE(result == 50 + 30);
}

TEST_CASE("All tasks unschedulable due to deadlines", "[task_scheduler]") {
    // All tasks are unschedulable since deadlines are too tight.
    vector<Task> tasks = {
        {0, 3, 2, 100, {}},
        {1, 4, 3, 80, {0}},
        {2, 2, 4, 60, {1}}
    };
    int N = 3;
    int M = 2;
    // No task can be completed on time.
    int result = maxProfit(N, M, tasks);
    REQUIRE(result == 0);
}