#include "task_scheduler.h"
#include "catch.hpp"
#include <vector>

using std::vector;

TEST_CASE("Single task with sufficient resources", "[minimum_makespan]") {
    int N = 1;
    int M = 1;
    // Single task that takes 5 time units, no dependency, requires one unit of resource 0.
    vector<int> duration = {5};
    vector<vector<int>> dependencies = {{}};
    vector<vector<int>> resource_requirements = {{0}};
    vector<int> resource_capacities = {1};
    
    int result = task_scheduler::minimum_makespan(N, M, duration, dependencies, resource_requirements, resource_capacities);
    // The single task runs from time 0 to 5.
    REQUIRE(result == 5);
}

TEST_CASE("Two tasks in sequence due to dependency", "[minimum_makespan]") {
    int N = 2;
    int M = 2;
    // Task 0: duration 3, no dependency, requires resource 0.
    // Task 1: duration 4, depends on task 0, requires resource 1.
    vector<int> duration = {3, 4};
    vector<vector<int>> dependencies = { {}, {0} };
    vector<vector<int>> resource_requirements = { {0}, {1} };
    vector<int> resource_capacities = {1, 1};
    
    int result = task_scheduler::minimum_makespan(N, M, duration, dependencies, resource_requirements, resource_capacities);
    // Task 0 finishes at T=3, then task 1 runs T=3 to T=7.
    REQUIRE(result == 7);
}

TEST_CASE("Multiple tasks executed concurrently", "[minimum_makespan]") {
    int N = 3;
    int M = 1;
    // All tasks have no dependencies.
    // Resource capacity of resource 0 is 2, and each task requires one unit.
    // durations: 4, 5, 2.
    vector<int> duration = {4, 5, 2};
    vector<vector<int>> dependencies = { {}, {}, {} };
    vector<vector<int>> resource_requirements = { {0}, {0}, {0} };
    vector<int> resource_capacities = {2};
    
    int result = task_scheduler::minimum_makespan(N, M, duration, dependencies, resource_requirements, resource_capacities);
    // Optimal scheduling:
    // Start tasks 0 and 1 at t=0. At t=4 task0 finishes and task2 can start.
    // Task1 finishes at t=5, task2 finishes at t=4+2 = 6.
    REQUIRE(result == 6);
}

TEST_CASE("Complex dependency and resource management", "[minimum_makespan]") {
    int N = 4;
    int M = 2;
    // Example scenario:
    // Task 0: duration 5, no dependency, requires resource 0.
    // Task 1: duration 3, depends on task 0, requires resource 1.
    // Task 2: duration 2, depends on tasks 0 and 1, requires resources 0 and 1.
    // Task 3: duration 4, depends on task 2, requires resource 0.
    vector<int> duration = {5, 3, 2, 4};
    vector<vector<int>> dependencies = { {}, {0}, {0, 1}, {2} };
    vector<vector<int>> resource_requirements = { {0}, {1}, {0, 1}, {0} };
    vector<int> resource_capacities = {2, 1};
    
    int result = task_scheduler::minimum_makespan(N, M, duration, dependencies, resource_requirements, resource_capacities);
    // As per the constructed optimal schedule, the total makespan should be 14.
    REQUIRE(result == 14);
}

TEST_CASE("Task requiring unavailable resources", "[minimum_makespan]") {
    int N = 2;
    int M = 1;
    // Task 0: duration 2, no dependency, requires resource 0 twice (i.e. needs 2 units).
    // Task 1: duration 3, no dependency, requires no resource.
    vector<int> duration = {2, 3};
    vector<vector<int>> dependencies = { {}, {} };
    vector<vector<int>> resource_requirements = { {0, 0}, {} };
    // Resource capacity for resource 0 is 1, so task 0 cannot be scheduled.
    vector<int> resource_capacities = {1};
    
    int result = task_scheduler::minimum_makespan(N, M, duration, dependencies, resource_requirements, resource_capacities);
    // Scheduling is impossible since task 0's requirements cannot be satisfied.
    REQUIRE(result == -1);
}

TEST_CASE("Concurrent scheduling with release of resources", "[minimum_makespan]") {
    int N = 5;
    int M = 2;
    // Task details:
    // Task 0: duration 4, no dependency, requires resource 0 once.
    // Task 1: duration 6, no dependency, requires resource 1 once.
    // Task 2: duration 3, depends on task 0, requires resource 0 once.
    // Task 3: duration 2, depends on task 1, requires resource 1 once.
    // Task 4: duration 5, depends on tasks 2 and 3, requires resources 0 and 1.
    vector<int> duration = {4, 6, 3, 2, 5};
    vector<vector<int>> dependencies = { {}, {}, {0}, {1}, {2, 3} };
    vector<vector<int>> resource_requirements = { {0}, {1}, {0}, {1}, {0, 1} };
    // Resource capacities: both resource 0 and 1 have capacity 1.
    vector<int> resource_capacities = {1, 1};
    
    int result = task_scheduler::minimum_makespan(N, M, duration, dependencies, resource_requirements, resource_capacities);
    // Expected timeline:
    // t=0: start Task 0 and Task 1 concurrently.
    // Task 0 finishes at t=4, Task 1 finishes at t=6.
    // t=4: start Task 2 (requires resource 0) since resource 0 becomes free.
    // Task 2 finishes at t=7.
    // t=6: start Task 3 (requires resource 1) since resource 1 becomes free.
    // Task 3 finishes at t=8.
    // t=8: both dependencies for Task 4 complete, start Task 4, which finishes at t=8+5 = 13.
    REQUIRE(result == 13);
}