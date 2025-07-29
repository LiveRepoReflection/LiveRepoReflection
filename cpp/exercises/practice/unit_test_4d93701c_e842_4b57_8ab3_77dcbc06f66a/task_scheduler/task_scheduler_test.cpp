#include "task_scheduler.h"
#include "catch.hpp"
#include <vector>
#include <string>
#include <set>

using namespace task_scheduler;

// A helper to compare sets of strings (order does not matter)
static std::set<std::string> to_set(const std::vector<std::string>& vec) {
    return std::set<std::string>(vec.begin(), vec.end());
}

TEST_CASE("Basic workflow with linear dependencies", "[task_scheduler]") {
    int num_workers = 2;
    int worker_memory = 100;
    std::vector<Task> tasks = {
        {"A", 10, 50, {}, 1},
        {"B", 5, 30, {"A"}, 2},
        {"C", 15, 70, {"B"}, 1}
    };

    ScheduleResult result = schedule_tasks(num_workers, worker_memory, tasks);
    REQUIRE(result.circular_dependency == false);
    REQUIRE(result.unfulfillable_dependencies.empty());
    REQUIRE(result.tasks_not_executed.empty());
    // Verify that each task has a START and END event in the schedule
    std::set<std::string> started;
    std::set<std::string> ended;
    for (const auto &event : result.schedule) {
        if (event.event_type == "START")
            started.insert(event.task_id);
        else if (event.event_type == "END")
            ended.insert(event.task_id);
    }
    std::set<std::string> expected = {"A", "B", "C"};
    REQUIRE(started == expected);
    REQUIRE(ended == expected);
    // Makespan should be at least the sum of processing times in a serial chain.
    REQUIRE(result.makespan >= 30);
}

TEST_CASE("Parallel scheduling with independent tasks", "[task_scheduler]") {
    int num_workers = 3;
    int worker_memory = 100;
    std::vector<Task> tasks = {
        {"A", 10, 50, {}, 1},
        {"B", 8, 30, {}, 2},
        {"C", 12, 70, {}, 3},
        {"D", 7, 40, {"A", "B"}, 2},
    };

    ScheduleResult result = schedule_tasks(num_workers, worker_memory, tasks);
    REQUIRE(result.circular_dependency == false);
    REQUIRE(result.unfulfillable_dependencies.empty());
    REQUIRE(result.tasks_not_executed.empty());
    // Since tasks A, B, and C are independent, they may run in parallel.
    // Check that makespan is not simply the sum of all processing times.
    int total_time = 10 + 8 + 12 + 7;
    REQUIRE(result.makespan < total_time);
}

TEST_CASE("Detect circular dependency", "[task_scheduler]") {
    int num_workers = 2;
    int worker_memory = 100;
    std::vector<Task> tasks = {
        {"A", 10, 50, {"C"}, 1},
        {"B", 5, 30, {"A"}, 2},
        {"C", 15, 70, {"B"}, 1}
    };

    ScheduleResult result = schedule_tasks(num_workers, worker_memory, tasks);
    REQUIRE(result.circular_dependency == true);
    // In a circular dependency, no tasks should be scheduled.
    REQUIRE(result.schedule.empty());
}

TEST_CASE("Unfulfillable dependencies", "[task_scheduler]") {
    int num_workers = 2;
    int worker_memory = 100;
    // Task B depends on non-existent task "Z"
    std::vector<Task> tasks = {
        {"A", 10, 50, {}, 1},
        {"B", 5, 30, {"Z"}, 2},
        {"C", 15, 70, {"A"}, 1}
    };

    ScheduleResult result = schedule_tasks(num_workers, worker_memory, tasks);
    REQUIRE(result.circular_dependency == false);
    // Task B dependency "Z" is unfulfillable, so B should be flagged.
    REQUIRE_FALSE(result.unfulfillable_dependencies.empty());
    std::set<std::string> uf = to_set(result.unfulfillable_dependencies);
    std::set<std::string> expected = {"B"};
    REQUIRE(uf == expected);
}

TEST_CASE("Resource constraints: task cannot be scheduled due to insufficient memory", "[task_scheduler]") {
    int num_workers = 2;
    int worker_memory = 50;
    // Task A requires more memory than available on any worker.
    std::vector<Task> tasks = {
        {"A", 10, 60, {}, 1},
        {"B", 5, 30, {}, 2}
    };

    ScheduleResult result = schedule_tasks(num_workers, worker_memory, tasks);
    REQUIRE(result.circular_dependency == false);
    // Task A should be in the tasks_not_executed list.
    REQUIRE(result.tasks_not_executed.size() == 1);
    REQUIRE(result.tasks_not_executed[0] == "A");
    // Task B should execute correctly.
    bool taskBExecuted = false;
    for (const auto &event : result.schedule) {
        if (event.task_id == "B" && event.event_type == "END") {
            taskBExecuted = true;
            break;
        }
    }
    REQUIRE(taskBExecuted);
}

TEST_CASE("Fault tolerance: task failure and retry", "[task_scheduler]") {
    int num_workers = 1;
    int worker_memory = 100;
    // Simulate a task that fails initially before eventually succeeding.
    // The task "F" will be designed (via internal simulation) to fail one or more times but succeed within the maximum retry limit.
    std::vector<Task> tasks = {
        {"F", 10, 50, {}, 1}
    };

    ScheduleResult result = schedule_tasks(num_workers, worker_memory, tasks);
    REQUIRE(result.circular_dependency == false);
    // Count events for task "F": should contain at least one START, possibly one or more FAILED events, and exactly one END.
    int startCount = 0;
    int failedCount = 0;
    int endCount = 0;
    for (const auto &event : result.schedule) {
        if (event.task_id == "F") {
            if (event.event_type == "START") 
                startCount++;
            else if (event.event_type == "FAILED")
                failedCount++;
            else if (event.event_type == "END")
                endCount++;
        }
    }
    // At least one start and exactly one successful end must be recorded.
    REQUIRE(startCount >= 1);
    REQUIRE(endCount == 1);
    // Failed count can be 0 if no failure occurred or up to 2 if it retried before success (max 3 attempts total)
    REQUIRE(failedCount <= 2);
}