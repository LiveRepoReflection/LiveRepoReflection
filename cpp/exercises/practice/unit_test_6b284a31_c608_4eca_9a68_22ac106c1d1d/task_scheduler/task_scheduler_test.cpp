#include "task_scheduler.h"
#include "catch.hpp"
#include <vector>
#include <string>
#include <unordered_set>

TEST_CASE("Empty task list returns empty result") {
    std::vector<Task> tasks;
    std::vector<Worker> workers{{0, 4, 8192}};  // One worker with 4 cores, 8GB RAM
    TaskScheduler scheduler;
    
    auto result = scheduler.scheduleTasks(tasks, workers);
    REQUIRE(result.empty());
}

TEST_CASE("Single task without dependencies") {
    std::vector<Task> tasks{
        {"task1", "command1", {}, 1, 1024, TaskStatus::PENDING}
    };
    std::vector<Worker> workers{{0, 4, 8192}};
    TaskScheduler scheduler;
    
    auto result = scheduler.scheduleTasks(tasks, workers);
    REQUIRE(result.size() == 1);
    REQUIRE(result["task1"] == TaskStatus::COMPLETED);
}

TEST_CASE("Tasks with simple dependency chain") {
    std::vector<Task> tasks{
        {"task1", "command1", {}, 1, 1024, TaskStatus::PENDING},
        {"task2", "command2", {"task1"}, 1, 1024, TaskStatus::PENDING},
        {"task3", "command3", {"task2"}, 1, 1024, TaskStatus::PENDING}
    };
    std::vector<Worker> workers{{0, 4, 8192}};
    TaskScheduler scheduler;
    
    auto result = scheduler.scheduleTasks(tasks, workers);
    REQUIRE(result.size() == 3);
    REQUIRE(result["task1"] == TaskStatus::COMPLETED);
    REQUIRE(result["task2"] == TaskStatus::COMPLETED);
    REQUIRE(result["task3"] == TaskStatus::COMPLETED);
}

TEST_CASE("Circular dependency detection") {
    std::vector<Task> tasks{
        {"task1", "command1", {"task3"}, 1, 1024, TaskStatus::PENDING},
        {"task2", "command2", {"task1"}, 1, 1024, TaskStatus::PENDING},
        {"task3", "command3", {"task2"}, 1, 1024, TaskStatus::PENDING}
    };
    std::vector<Worker> workers{{0, 4, 8192}};
    TaskScheduler scheduler;
    
    auto result = scheduler.scheduleTasks(tasks, workers);
    REQUIRE(result.size() == 3);
    REQUIRE(result["task1"] == TaskStatus::FAILED);
    REQUIRE(result["task2"] == TaskStatus::FAILED);
    REQUIRE(result["task3"] == TaskStatus::FAILED);
}

TEST_CASE("Insufficient resources") {
    std::vector<Task> tasks{
        {"task1", "command1", {}, 16, 1024, TaskStatus::PENDING}  // Requires 16 cores
    };
    std::vector<Worker> workers{{0, 4, 8192}};  // Only has 4 cores
    TaskScheduler scheduler;
    
    auto result = scheduler.scheduleTasks(tasks, workers);
    REQUIRE(result.size() == 1);
    REQUIRE(result["task1"] == TaskStatus::FAILED);
}

TEST_CASE("Multiple workers handling parallel tasks") {
    std::vector<Task> tasks{
        {"task1", "command1", {}, 2, 1024, TaskStatus::PENDING},
        {"task2", "command2", {}, 2, 1024, TaskStatus::PENDING},
        {"task3", "command3", {}, 2, 1024, TaskStatus::PENDING}
    };
    std::vector<Worker> workers{
        {0, 2, 4096},
        {1, 2, 4096},
        {2, 2, 4096}
    };
    TaskScheduler scheduler;
    
    auto result = scheduler.scheduleTasks(tasks, workers);
    REQUIRE(result.size() == 3);
    REQUIRE(result["task1"] == TaskStatus::COMPLETED);
    REQUIRE(result["task2"] == TaskStatus::COMPLETED);
    REQUIRE(result["task3"] == TaskStatus::COMPLETED);
}

TEST_CASE("Complex dependency graph") {
    std::vector<Task> tasks{
        {"task1", "command1", {}, 1, 1024, TaskStatus::PENDING},
        {"task2", "command2", {}, 1, 1024, TaskStatus::PENDING},
        {"task3", "command3", {"task1", "task2"}, 1, 1024, TaskStatus::PENDING},
        {"task4", "command4", {"task2"}, 1, 1024, TaskStatus::PENDING},
        {"task5", "command5", {"task3", "task4"}, 1, 1024, TaskStatus::PENDING}
    };
    std::vector<Worker> workers{{0, 4, 8192}};
    TaskScheduler scheduler;
    
    auto result = scheduler.scheduleTasks(tasks, workers);
    REQUIRE(result.size() == 5);
    REQUIRE(result["task1"] == TaskStatus::COMPLETED);
    REQUIRE(result["task2"] == TaskStatus::COMPLETED);
    REQUIRE(result["task3"] == TaskStatus::COMPLETED);
    REQUIRE(result["task4"] == TaskStatus::COMPLETED);
    REQUIRE(result["task5"] == TaskStatus::COMPLETED);
}

TEST_CASE("Failed dependency cascade") {
    std::vector<Task> tasks{
        {"task1", "command1", {}, 33, 1024, TaskStatus::PENDING},  // Will fail due to excessive CPU requirement
        {"task2", "command2", {"task1"}, 1, 1024, TaskStatus::PENDING},
        {"task3", "command3", {"task2"}, 1, 1024, TaskStatus::PENDING}
    };
    std::vector<Worker> workers{{0, 32, 8192}};  // Max 32 cores
    TaskScheduler scheduler;
    
    auto result = scheduler.scheduleTasks(tasks, workers);
    REQUIRE(result.size() == 3);
    REQUIRE(result["task1"] == TaskStatus::FAILED);
    REQUIRE(result["task2"] == TaskStatus::FAILED);
    REQUIRE(result["task3"] == TaskStatus::FAILED);
}

TEST_CASE("Memory constraints") {
    std::vector<Task> tasks{
        {"task1", "command1", {}, 1, 65536, TaskStatus::PENDING}  // Requires 64GB RAM
    };
    std::vector<Worker> workers{{0, 4, 32768}};  // Only has 32GB RAM
    TaskScheduler scheduler;
    
    auto result = scheduler.scheduleTasks(tasks, workers);
    REQUIRE(result.size() == 1);
    REQUIRE(result["task1"] == TaskStatus::FAILED);
}

TEST_CASE("Maximum worker and task limits") {
    std::vector<Task> tasks;
    std::vector<Worker> workers;
    
    // Create 100 workers (maximum allowed)
    for (int i = 0; i < 100; i++) {
        workers.push_back({i, 4, 8192});
    }
    
    // Create 10000 tasks (maximum allowed)
    for (int i = 0; i < 10000; i++) {
        tasks.push_back({
            "task" + std::to_string(i),
            "command" + std::to_string(i),
            {},
            1,
            1024,
            TaskStatus::PENDING
        });
    }
    
    TaskScheduler scheduler;
    auto result = scheduler.scheduleTasks(tasks, workers);
    REQUIRE(result.size() == 10000);
    
    // All tasks should complete since they have no dependencies and sufficient resources
    for (int i = 0; i < 10000; i++) {
        REQUIRE(result["task" + std::to_string(i)] == TaskStatus::COMPLETED);
    }
}