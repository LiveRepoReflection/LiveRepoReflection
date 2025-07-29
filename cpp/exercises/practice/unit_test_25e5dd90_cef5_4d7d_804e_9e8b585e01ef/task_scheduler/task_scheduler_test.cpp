#include "catch.hpp"
#include "task_scheduler.h"
#include <vector>
#include <utility>

using std::vector;
using std::pair;

TEST_CASE("Single Task - No Dependencies", "[task_scheduler]") {
    // One task with duration 5, requires resource 0: quantity 1.
    // Resource 0 capacity is 2.
    Task t0;
    t0.duration = 5;
    t0.resource_requirements = { {0, 1} };
    // No dependencies
    t0.dependencies = {};
    vector<Task> tasks = { t0 };
    
    Resource r0;
    r0.capacity = 2;
    vector<Resource> resources = { r0 };

    int makespan = scheduleTasks(tasks, resources);
    // Should finish at time = 5
    REQUIRE(makespan == 5);
}

TEST_CASE("Two Tasks - Linear Dependency", "[task_scheduler]") {
    // Two tasks:
    // Task 0: duration = 5, no dependency.
    // Task 1: duration = 7, depends on task 0.
    // Resources have high capacity.
    Task t0;
    t0.duration = 5;
    t0.resource_requirements = { {0, 1} };
    t0.dependencies = {};

    Task t1;
    t1.duration = 7;
    t1.resource_requirements = { {0, 1} };
    t1.dependencies = { 0 };

    vector<Task> tasks = { t0, t1 };

    Resource r0;
    r0.capacity = 10;  // Large enough capacity
    vector<Resource> resources = { r0 };

    int makespan = scheduleTasks(tasks, resources);
    // Expected schedule: Task 0 from 0 to 5, Task 1 starts at 5 and finishes at 12.
    REQUIRE(makespan == 12);
}

TEST_CASE("Multiple Tasks with Resource Contention", "[task_scheduler]") {
    // Four tasks:
    // Task 0: duration = 3, no resource requirement (or minimal) and no dependencies.
    // Task 1: duration = 5, requires resource 0: quantity 2; depends on task 0.
    // Task 2: duration = 4, requires resource 0: quantity 2; depends on task 0.
    // Task 3: duration = 2, requires resource 0: quantity 1; depends on task 1 and task 2.
    // Resource: resource 0 capacity = 3.
    Task t0;
    t0.duration = 3;
    t0.resource_requirements = { {0, 0} };
    t0.dependencies = {};

    Task t1;
    t1.duration = 5;
    t1.resource_requirements = { {0, 2} };
    t1.dependencies = { 0 };

    Task t2;
    t2.duration = 4;
    t2.resource_requirements = { {0, 2} };
    t2.dependencies = { 0 };

    Task t3;
    t3.duration = 2;
    t3.resource_requirements = { {0, 1} };
    t3.dependencies = { 1, 2 };

    vector<Task> tasks = { t0, t1, t2, t3 };

    Resource r0;
    r0.capacity = 3;
    vector<Resource> resources = { r0 };

    int makespan = scheduleTasks(tasks, resources);
    // Expected outcome: Task 0 completes at 3.
    // Then tasks 1 and 2 cannot run concurrently because their combined requirement is 4 > 3.
    // They must be run sequentially.
    // Thus, either:
    //   Task 1: 3->8, then Task 2: 8->12, then Task 3: 12->14   OR
    //   Task 2: 3->7, then Task 1: 7->12, then Task 3: 12->14
    // In both cases, makespan is 14.
    REQUIRE(makespan == 14);
}

TEST_CASE("Complex Scheduling with Multiple Dependencies", "[task_scheduler]") {
    // Five tasks:
    // Task 0: duration = 2, requires resource 0: quantity 1; no dependencies.
    // Task 1: duration = 3, requires resource 0: quantity 2; depends on task 0.
    // Task 2: duration = 1, requires resource 0: quantity 1; depends on task 0.
    // Task 3: duration = 4, requires resource 0: quantity 2; depends on task 1 and task 2.
    // Task 4: duration = 3, requires resource 0: quantity 2; depends on task 0.
    // Resource: resource 0 capacity = 3.
    Task t0;
    t0.duration = 2;
    t0.resource_requirements = { {0, 1} };
    t0.dependencies = {};

    Task t1;
    t1.duration = 3;
    t1.resource_requirements = { {0, 2} };
    t1.dependencies = { 0 };

    Task t2;
    t2.duration = 1;
    t2.resource_requirements = { {0, 1} };
    t2.dependencies = { 0 };

    Task t3;
    t3.duration = 4;
    t3.resource_requirements = { {0, 2} };
    t3.dependencies = { 1, 2 };

    Task t4;
    t4.duration = 3;
    t4.resource_requirements = { {0, 2} };
    t4.dependencies = { 0 };

    vector<Task> tasks = { t0, t1, t2, t3, t4 };

    Resource r0;
    r0.capacity = 3;
    vector<Resource> resources = { r0 };

    int makespan = scheduleTasks(tasks, resources);
    // One optimal schedule:
    // t0: 0-2;
    // then at time 2, t1 and t2 and t4 become available.
    // Schedule t1 and t2 concurrently (resource usage 2+1=3) -> t1 ends at 5, t2 at 3.
    // At time 5, schedule t3 (depends on t1 and t2) and t4 sequentially because both need 2 units (cannot run concurrently).
    // Total makespan = 12.
    REQUIRE(makespan == 12);
}