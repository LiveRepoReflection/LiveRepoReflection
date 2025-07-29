#include <vector>
#include <tuple>
#include <algorithm>
#include <iostream>
#include <numeric>
#include "catch.hpp"
#include "task_scheduler.h"

TEST_CASE("No dependencies") {
    std::vector<std::tuple<int, int, int, std::vector<int>>> tasks = {
        {1, 5, 10, {}},
        {2, 3, 8, {}},
        {3, 6, 15, {}},
        {4, 4, 12, {}}
    };

    auto schedule = task_scheduler::schedule_tasks(tasks);
    
    REQUIRE(schedule.size() == 4);
    
    // Verify all tasks are in the schedule
    std::vector<int> task_ids;
    for (auto id : schedule) {
        task_ids.push_back(id);
    }
    std::sort(task_ids.begin(), task_ids.end());
    REQUIRE(task_ids == std::vector<int>{1, 2, 3, 4});
    
    // Check that the schedule respects the deadlines maximally
    int completed_by_deadline = 0;
    int current_time = 0;
    std::unordered_map<int, std::tuple<int, int>> task_map;
    for (const auto& task : tasks) {
        task_map[std::get<0>(task)] = {std::get<1>(task), std::get<2>(task)};
    }
    
    for (int id : schedule) {
        auto [duration, deadline] = task_map[id];
        current_time += duration;
        if (current_time <= deadline) {
            completed_by_deadline++;
        }
    }
    
    REQUIRE(completed_by_deadline >= 3); // At least 3 tasks should complete on time
}

TEST_CASE("With dependencies") {
    std::vector<std::tuple<int, int, int, std::vector<int>>> tasks = {
        {1, 5, 10, {}},
        {2, 3, 8, {1}},
        {3, 6, 15, {1, 2}},
        {4, 4, 12, {}}
    };

    auto schedule = task_scheduler::schedule_tasks(tasks);
    
    REQUIRE(schedule.size() == 4);
    
    // Verify the dependency relationships
    auto findIndex = [&schedule](int id) {
        return std::distance(schedule.begin(), std::find(schedule.begin(), schedule.end(), id));
    };
    
    // Task 2 must be after task 1
    REQUIRE(findIndex(1) < findIndex(2));
    
    // Task 3 must be after tasks 1 and 2
    REQUIRE(findIndex(1) < findIndex(3));
    REQUIRE(findIndex(2) < findIndex(3));
    
    // Check optimal schedule
    int completed_by_deadline = 0;
    int current_time = 0;
    std::unordered_map<int, std::tuple<int, int>> task_map;
    for (const auto& task : tasks) {
        task_map[std::get<0>(task)] = {std::get<1>(task), std::get<2>(task)};
    }
    
    for (int id : schedule) {
        auto [duration, deadline] = task_map[id];
        current_time += duration;
        if (current_time <= deadline) {
            completed_by_deadline++;
        }
    }
    
    REQUIRE(completed_by_deadline >= 2); // At least 2 tasks should complete on time with dependencies
}

TEST_CASE("Complex dependencies") {
    std::vector<std::tuple<int, int, int, std::vector<int>>> tasks = {
        {1, 3, 10, {}},
        {2, 2, 8, {1}},
        {3, 4, 15, {2}},
        {4, 5, 12, {1}},
        {5, 2, 20, {3, 4}},
        {6, 3, 18, {4}}
    };

    auto schedule = task_scheduler::schedule_tasks(tasks);
    
    REQUIRE(schedule.size() == 6);
    
    // Verify all tasks are in the schedule
    std::vector<int> task_ids(schedule.begin(), schedule.end());
    std::sort(task_ids.begin(), task_ids.end());
    REQUIRE(task_ids == std::vector<int>{1, 2, 3, 4, 5, 6});
    
    // Verify the dependency relationships
    auto findIndex = [&schedule](int id) {
        return std::distance(schedule.begin(), std::find(schedule.begin(), schedule.end(), id));
    };
    
    REQUIRE(findIndex(1) < findIndex(2));
    REQUIRE(findIndex(2) < findIndex(3));
    REQUIRE(findIndex(1) < findIndex(4));
    REQUIRE(findIndex(3) < findIndex(5));
    REQUIRE(findIndex(4) < findIndex(5));
    REQUIRE(findIndex(4) < findIndex(6));
}

TEST_CASE("Preference for minimum tardiness") {
    // Two tasks with same deadline but different durations
    std::vector<std::tuple<int, int, int, std::vector<int>>> tasks = {
        {1, 10, 15, {}},
        {2, 5, 15, {}}
    };

    auto schedule = task_scheduler::schedule_tasks(tasks);
    
    REQUIRE(schedule.size() == 2);
    
    // Verify that the shorter task is scheduled first to minimize tardiness
    // Either both tasks can complete on time, or the shorter task (2) should be first
    if (schedule[0] != 2) {
        int total_tardiness = 0;
        int current_time = 0;
        
        std::unordered_map<int, std::tuple<int, int>> task_map;
        for (const auto& task : tasks) {
            task_map[std::get<0>(task)] = {std::get<1>(task), std::get<2>(task)};
        }
        
        for (int id : schedule) {
            auto [duration, deadline] = task_map[id];
            current_time += duration;
            total_tardiness += std::max(0, current_time - deadline);
        }
        
        // Check alternative schedule
        int alt_tardiness = 0;
        current_time = 0;
        std::vector<int> alt_schedule = {2, 1};
        
        for (int id : alt_schedule) {
            auto [duration, deadline] = task_map[id];
            current_time += duration;
            alt_tardiness += std::max(0, current_time - deadline);
        }
        
        // The chosen schedule should have the same or less tardiness
        REQUIRE(total_tardiness <= alt_tardiness);
    }
}

TEST_CASE("Impossible task completion") {
    // Create a scenario where not all tasks can complete by their deadlines
    std::vector<std::tuple<int, int, int, std::vector<int>>> tasks = {
        {1, 10, 5, {}},  // Impossible to complete on time
        {2, 5, 20, {}},
        {3, 8, 25, {}}
    };

    auto schedule = task_scheduler::schedule_tasks(tasks);
    
    REQUIRE(schedule.size() == 3);
    
    // Verify all tasks are scheduled
    std::vector<int> task_ids(schedule.begin(), schedule.end());
    std::sort(task_ids.begin(), task_ids.end());
    REQUIRE(task_ids == std::vector<int>{1, 2, 3});
    
    // Calculate number of tasks completed on time
    int completed_by_deadline = 0;
    int current_time = 0;
    std::unordered_map<int, std::tuple<int, int>> task_map;
    for (const auto& task : tasks) {
        task_map[std::get<0>(task)] = {std::get<1>(task), std::get<2>(task)};
    }
    
    for (int id : schedule) {
        auto [duration, deadline] = task_map[id];
        current_time += duration;
        if (current_time <= deadline) {
            completed_by_deadline++;
        }
    }
    
    // At least tasks 2 and 3 should be completed on time
    REQUIRE(completed_by_deadline >= 2);
}

TEST_CASE("Empty input") {
    std::vector<std::tuple<int, int, int, std::vector<int>>> tasks;
    auto schedule = task_scheduler::schedule_tasks(tasks);
    REQUIRE(schedule.empty());
}

TEST_CASE("Single task") {
    std::vector<std::tuple<int, int, int, std::vector<int>>> tasks = {
        {1, 5, 10, {}}
    };
    
    auto schedule = task_scheduler::schedule_tasks(tasks);
    
    REQUIRE(schedule.size() == 1);
    REQUIRE(schedule[0] == 1);
}

TEST_CASE("Task chain with tight deadlines") {
    std::vector<std::tuple<int, int, int, std::vector<int>>> tasks = {
        {1, 3, 3, {}},
        {2, 3, 6, {1}},
        {3, 3, 9, {2}},
        {4, 3, 12, {3}}
    };
    
    auto schedule = task_scheduler::schedule_tasks(tasks);
    
    REQUIRE(schedule.size() == 4);
    
    // Verify dependency chain is respected
    auto findIndex = [&schedule](int id) {
        return std::distance(schedule.begin(), std::find(schedule.begin(), schedule.end(), id));
    };
    
    REQUIRE(findIndex(1) < findIndex(2));
    REQUIRE(findIndex(2) < findIndex(3));
    REQUIRE(findIndex(3) < findIndex(4));
    
    // All tasks should complete exactly at their deadlines
    int current_time = 0;
    std::unordered_map<int, std::tuple<int, int>> task_map;
    for (const auto& task : tasks) {
        task_map[std::get<0>(task)] = {std::get<1>(task), std::get<2>(task)};
    }
    
    int completed_on_time = 0;
    for (int id : schedule) {
        auto [duration, deadline] = task_map[id];
        current_time += duration;
        if (current_time <= deadline) {
            completed_on_time++;
        }
    }
    
    REQUIRE(completed_on_time == 4);
}