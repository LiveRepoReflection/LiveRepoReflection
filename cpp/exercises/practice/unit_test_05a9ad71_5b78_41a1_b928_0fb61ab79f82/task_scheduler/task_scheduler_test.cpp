#include "task_scheduler.h"
#include "catch.hpp"
#include <vector>
#include <map>
#include <string>

TEST_CASE("Basic single machine single task", "[scheduler]") {
    std::vector<Machine> machines = {
        {1, {{"CPU", 4}, {"Memory", 8}}}
    };
    
    std::vector<Task> tasks = {
        {1, {{"CPU", 2}, {"Memory", 4}}, 2, 0}
    };
    
    TaskScheduler scheduler;
    auto schedule = scheduler.schedule(machines, tasks, 5);
    
    REQUIRE(schedule.size() == 1);
    REQUIRE(schedule[0].task_id == 1);
    REQUIRE(schedule[0].machine_id == 1);
    REQUIRE(schedule[0].start_time == 0);
    REQUIRE(schedule[0].end_time == 2);
}

TEST_CASE("Multiple machines multiple tasks", "[scheduler]") {
    std::vector<Machine> machines = {
        {1, {{"CPU", 4}, {"Memory", 8}}},
        {2, {{"CPU", 2}, {"Memory", 4}}}
    };
    
    std::vector<Task> tasks = {
        {1, {{"CPU", 2}, {"Memory", 4}}, 2, 0},
        {2, {{"CPU", 1}, {"Memory", 2}}, 3, 1},
        {3, {{"CPU", 3}, {"Memory", 6}}, 1, 2}
    };
    
    TaskScheduler scheduler;
    auto schedule = scheduler.schedule(machines, tasks, 5);
    
    REQUIRE(schedule.size() == 3);
}

TEST_CASE("Task with excessive resource requirements", "[scheduler]") {
    std::vector<Machine> machines = {
        {1, {{"CPU", 4}, {"Memory", 8}}}
    };
    
    std::vector<Task> tasks = {
        {1, {{"CPU", 8}, {"Memory", 16}}, 2, 0}
    };
    
    TaskScheduler scheduler;
    auto schedule = scheduler.schedule(machines, tasks, 5);
    
    REQUIRE(schedule.empty());
}

TEST_CASE("Tasks with non-sequential arrival times", "[scheduler]") {
    std::vector<Machine> machines = {
        {1, {{"CPU", 4}, {"Memory", 8}}}
    };
    
    std::vector<Task> tasks = {
        {1, {{"CPU", 2}, {"Memory", 4}}, 2, 3},
        {2, {{"CPU", 1}, {"Memory", 2}}, 1, 0}
    };
    
    TaskScheduler scheduler;
    auto schedule = scheduler.schedule(machines, tasks, 5);
    
    REQUIRE(schedule.size() == 2);
    for (const auto& entry : schedule) {
        if (entry.task_id == 1) {
            REQUIRE(entry.start_time >= 3);
        }
        if (entry.task_id == 2) {
            REQUIRE(entry.start_time >= 0);
        }
    }
}

TEST_CASE("Resource capacity verification", "[scheduler]") {
    std::vector<Machine> machines = {
        {1, {{"CPU", 4}, {"Memory", 8}}}
    };
    
    std::vector<Task> tasks = {
        {1, {{"CPU", 3}, {"Memory", 6}}, 2, 0},
        {2, {{"CPU", 2}, {"Memory", 4}}, 2, 0}
    };
    
    TaskScheduler scheduler;
    auto schedule = scheduler.schedule(machines, tasks, 5);
    
    // Verify that resource capacity is not exceeded at any point
    std::map<int, std::vector<ScheduleEntry>> machine_schedules;
    for (const auto& entry : schedule) {
        machine_schedules[entry.machine_id].push_back(entry);
    }
    
    for (const auto& machine_schedule : machine_schedules) {
        for (int t = 0; t < 5; ++t) {
            int cpu_usage = 0;
            int memory_usage = 0;
            
            for (const auto& entry : machine_schedule.second) {
                if (t >= entry.start_time && t < entry.end_time) {
                    for (const auto& task : tasks) {
                        if (task.id == entry.task_id) {
                            cpu_usage += task.resources.at("CPU");
                            memory_usage += task.resources.at("Memory");
                        }
                    }
                }
            }
            
            REQUIRE(cpu_usage <= 4);
            REQUIRE(memory_usage <= 8);
        }
    }
}

TEST_CASE("Scheduling horizon constraints", "[scheduler]") {
    std::vector<Machine> machines = {
        {1, {{"CPU", 4}, {"Memory", 8}}}
    };
    
    std::vector<Task> tasks = {
        {1, {{"CPU", 2}, {"Memory", 4}}, 6, 0}
    };
    
    TaskScheduler scheduler;
    auto schedule = scheduler.schedule(machines, tasks, 5);
    
    // Task cannot complete within horizon, should not be scheduled
    REQUIRE(schedule.empty());
}

TEST_CASE("Large scale scheduling", "[scheduler]") {
    std::vector<Machine> machines;
    for (int i = 1; i <= 100; ++i) {
        machines.push_back({i, {{"CPU", 4}, {"Memory", 8}}});
    }
    
    std::vector<Task> tasks;
    for (int i = 1; i <= 1000; ++i) {
        tasks.push_back({i, {{"CPU", 1}, {"Memory", 2}}, 2, i % 10});
    }
    
    TaskScheduler scheduler;
    auto schedule = scheduler.schedule(machines, tasks, 100);
    
    REQUIRE_FALSE(schedule.empty());
}

TEST_CASE("Resource type variations", "[scheduler]") {
    std::vector<Machine> machines = {
        {1, {{"CPU", 4}, {"Memory", 8}, {"GPU", 2}, {"Network", 1000}}}
    };
    
    std::vector<Task> tasks = {
        {1, {{"CPU", 2}, {"Memory", 4}, {"GPU", 1}, {"Network", 500}}, 2, 0}
    };
    
    TaskScheduler scheduler;
    auto schedule = scheduler.schedule(machines, tasks, 5);
    
    REQUIRE(schedule.size() == 1);
}

TEST_CASE("Concurrent task execution", "[scheduler]") {
    std::vector<Machine> machines = {
        {1, {{"CPU", 4}, {"Memory", 8}}}
    };
    
    std::vector<Task> tasks = {
        {1, {{"CPU", 1}, {"Memory", 2}}, 2, 0},
        {2, {{"CPU", 1}, {"Memory", 2}}, 2, 0},
        {3, {{"CPU", 1}, {"Memory", 2}}, 2, 0}
    };
    
    TaskScheduler scheduler;
    auto schedule = scheduler.schedule(machines, tasks, 5);
    
    // Should be able to run multiple tasks concurrently if resources allow
    REQUIRE(schedule.size() == 3);
}