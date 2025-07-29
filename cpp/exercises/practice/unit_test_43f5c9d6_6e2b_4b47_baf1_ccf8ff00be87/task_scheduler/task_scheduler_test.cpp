#include "catch.hpp"
#include "task_scheduler.h"

#include <vector>

using std::vector;

TEST_CASE("single_task_feasible") {
    // One task with no dependencies, and deadline is met.
    // Expected maximum lateness is 0.
    vector<Task> tasks = {
        {0, 5, 10, {}}
    };
    int result = schedule_tasks(1, 1, tasks);
    REQUIRE(result == 0);
}

TEST_CASE("chain_tasks_feasible") {
    // Three tasks in a dependency chain: 0 -> 1 -> 2
    // Their deadlines are set exactly to the cumulative finish times.
    vector<Task> tasks = {
        {0, 4, 4, {}},
        {1, 4, 8, {0}},
        {2, 4, 12, {1}}
    };
    int result = schedule_tasks(3, 1, tasks);
    REQUIRE(result == 0);
}

TEST_CASE("parallel_tasks_feasible") {
    // Four tasks with a mix of independent tasks and dependencies.
    // Task 1 depends on task 0; task 2 depends on tasks 0 and 1.
    // With two machines, an optimal schedule exists with zero lateness.
    vector<Task> tasks = {
        {0, 5, 10, {}},
        {1, 3, 12, {0}},
        {2, 4, 15, {0, 1}},
        {3, 2, 20, {}}
    };
    int result = schedule_tasks(4, 2, tasks);
    REQUIRE(result == 0);
}

TEST_CASE("single_task_impossible") {
    // A single task that cannot meet its deadline even if scheduled immediately.
    vector<Task> tasks = {
        {0, 10, 5, {}}
    };
    int result = schedule_tasks(1, 1, tasks);
    REQUIRE(result == -1);
}

TEST_CASE("dependent_task_impossible") {
    // Two tasks in a dependency chain where the first task cannot finish by its deadline.
    // Even with optimal scheduling on one machine, it's impossible to meet all deadlines.
    vector<Task> tasks = {
        {0, 5, 3, {}},
        {1, 5, 15, {0}}
    };
    int result = schedule_tasks(2, 1, tasks);
    REQUIRE(result == -1);
}

TEST_CASE("complex_dag_feasible") {
    // Six tasks forming a complex DAG (dependencies form a tree structure).
    // With two machines, a schedule exists that meets all deadlines.
    // Task structure:
    //   Task 0: no dependencies.
    //   Task 1 and Task 2: depend on Task 0.
    //   Task 3: depends on Task 1.
    //   Task 4: depends on Task 2.
    //   Task 5: depends on both Task 3 and Task 4.
    vector<Task> tasks = {
        {0, 3, 5, {}},
        {1, 2, 6, {0}},
        {2, 4, 10, {0}},
        {3, 3, 12, {1}},
        {4, 2, 12, {2}},
        {5, 1, 15, {3, 4}}
    };
    int result = schedule_tasks(6, 2, tasks);
    REQUIRE(result == 0);
}