#include "task_scheduler.h"
#include "catch.hpp"
#include <vector>

using namespace std;
using namespace task_scheduler;

// Helper function to construct a Task.
Task make_task(int id, int exec_time, int deadline, const vector<int>& deps, int priority) {
    Task t;
    t.id = id;
    t.execution_time = exec_time;
    t.deadline = deadline;
    t.dependencies = deps;
    t.priority = priority;
    return t;
}

TEST_CASE("Example schedule with 4 tasks and 2 machines", "[task_scheduler]") {
    // n = 4, k = 2
    // Task 1: id=1, execution_time=5, deadline=10, dependencies=[], priority=1
    // Task 2: id=2, execution_time=3, deadline=12, dependencies=[1], priority=2
    // Task 3: id=3, execution_time=4, deadline=15, dependencies=[1], priority=3
    // Task 4: id=4, execution_time=2, deadline=20, dependencies=[2,3], priority=4
    int n = 4;
    int k = 2;
    vector<Task> tasks;
    tasks.push_back(make_task(1, 5, 10, {}, 1));
    tasks.push_back(make_task(2, 3, 12, {1}, 2));
    tasks.push_back(make_task(3, 4, 15, {1}, 3));
    tasks.push_back(make_task(4, 2, 20, {2, 3}, 4));

    int result = scheduleTasks(n, k, tasks);
    // Expected optimal schedule leads to total weighted tardiness = 0
    REQUIRE(result == 0);
}

TEST_CASE("Example schedule with 3 tasks and 1 machine", "[task_scheduler]") {
    // n = 3, k = 1
    // Task 1: id=1, execution_time=5, deadline=7, dependencies=[], priority=10
    // Task 2: id=2, execution_time=4, deadline=8, dependencies=[1], priority=5
    // Task 3: id=3, execution_time=6, deadline=10, dependencies=[2], priority=1
    int n = 3;
    int k = 1;
    vector<Task> tasks;
    tasks.push_back(make_task(1, 5, 7, {}, 10));
    tasks.push_back(make_task(2, 4, 8, {1}, 5));
    tasks.push_back(make_task(3, 6, 10, {2}, 1));

    int result = scheduleTasks(n, k, tasks);
    // The optimal schedule described should achieve a total weighted tardiness of 10.
    REQUIRE(result == 10);
}

TEST_CASE("Unschedulable scenario due to tight deadline", "[task_scheduler]") {
    // n = 2, k = 1
    // Task 1: id=1, execution_time=5, deadline=3, dependencies=[], priority=1
    // Task 2: id=2, execution_time=4, deadline=10, dependencies=[1], priority=1
    int n = 2;
    int k = 1;
    vector<Task> tasks;
    tasks.push_back(make_task(1, 5, 3, {}, 1));
    tasks.push_back(make_task(2, 4, 10, {1}, 1));

    int result = scheduleTasks(n, k, tasks);
    // It is impossible to complete Task 1 before its deadline. Expect -1.
    REQUIRE(result == -1);
}

TEST_CASE("Complex schedule with 5 tasks and 2 machines", "[task_scheduler]") {
    // n = 5, k = 2
    // Task 1: id=1, execution_time=2, deadline=5, dependencies=[], priority=3
    // Task 2: id=2, execution_time=3, deadline=8, dependencies=[], priority=2
    // Task 3: id=3, execution_time=4, deadline=12, dependencies=[1], priority=5
    // Task 4: id=4, execution_time=2, deadline=10, dependencies=[2], priority=4
    // Task 5: id=5, execution_time=1, deadline=6, dependencies=[1,2], priority=10
    int n = 5;
    int k = 2;
    vector<Task> tasks;
    tasks.push_back(make_task(1, 2, 5, {}, 3));
    tasks.push_back(make_task(2, 3, 8, {}, 2));
    tasks.push_back(make_task(3, 4, 12, {1}, 5));
    tasks.push_back(make_task(4, 2, 10, {2}, 4));
    tasks.push_back(make_task(5, 1, 6, {1, 2}, 10));

    int result = scheduleTasks(n, k, tasks);
    // With an optimal schedule, all deadlines can be met, resulting in total weighted tardiness = 0.
    REQUIRE(result == 0);
}

TEST_CASE("Schedule with interdependent tasks and chain dependencies", "[task_scheduler]") {
    // n = 6, k = 2
    // A chain of dependencies and some parallel tasks.
    // Task 1: id=1, execution_time=3, deadline=10, dependencies=[], priority=2
    // Task 2: id=2, execution_time=2, deadline=8, dependencies=[1], priority=3
    // Task 3: id=3, execution_time=4, deadline=15, dependencies=[2], priority=1
    // Task 4: id=4, execution_time=2, deadline=12, dependencies=[1], priority=4
    // Task 5: id=5, execution_time=1, deadline=9, dependencies=[2,4], priority=5
    // Task 6: id=6, execution_time=3, deadline=20, dependencies=[3,5], priority=2
    int n = 6;
    int k = 2;
    vector<Task> tasks;
    tasks.push_back(make_task(1, 3, 10, {}, 2));
    tasks.push_back(make_task(2, 2, 8, {1}, 3));
    tasks.push_back(make_task(3, 4, 15, {2}, 1));
    tasks.push_back(make_task(4, 2, 12, {1}, 4));
    tasks.push_back(make_task(5, 1, 9, {2, 4}, 5));
    tasks.push_back(make_task(6, 3, 20, {3, 5}, 2));

    int result = scheduleTasks(n, k, tasks);
    // Expect the scheduling algorithm to find an optimal ordering with total weighted tardiness = 0.
    REQUIRE(result == 0);
}