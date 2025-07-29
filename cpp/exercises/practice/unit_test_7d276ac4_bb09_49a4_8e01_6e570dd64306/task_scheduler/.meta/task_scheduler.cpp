#include "task_scheduler.h"
#include <algorithm>
#include <queue>
#include <unordered_map>
#include <unordered_set>
#include <limits>
#include <functional>

namespace task_scheduler {

// Helper struct to represent a task with all relevant information
struct Task {
    int id;
    int duration;
    int deadline;
    std::vector<int> dependencies;
    std::vector<int> dependents;
    bool visited = false;
    bool in_schedule = false;
};

// Structure to hold a schedule and its evaluation metrics
struct ScheduleResult {
    std::vector<int> schedule;
    int tasks_on_time;
    int total_tardiness;
};

// Performs topological sort to ensure dependencies are respected
std::vector<int> topological_sort(std::unordered_map<int, Task>& tasks) {
    std::vector<int> result;
    std::function<void(int)> dfs = [&](int id) {
        auto& task = tasks[id];
        if (task.visited) return;
        
        task.visited = true;
        for (int dep_id : task.dependents) {
            dfs(dep_id);
        }
        result.push_back(id);
    };
    
    for (const auto& [id, _] : tasks) {
        dfs(id);
    }
    
    std::reverse(result.begin(), result.end());
    return result;
}

// Check if a task has all its dependencies in the schedule
bool can_schedule(const Task& task, const std::unordered_set<int>& scheduled_tasks) {
    for (int dep_id : task.dependencies) {
        if (scheduled_tasks.find(dep_id) == scheduled_tasks.end()) {
            return false;
        }
    }
    return true;
}

// Evaluate a schedule: count tasks completed on time and total tardiness
void evaluate_schedule(const std::vector<int>& schedule, 
                       const std::unordered_map<int, Task>& tasks, 
                       int& tasks_on_time, 
                       int& total_tardiness) {
    tasks_on_time = 0;
    total_tardiness = 0;
    int current_time = 0;
    
    for (int id : schedule) {
        const Task& task = tasks.at(id);
        current_time += task.duration;
        if (current_time <= task.deadline) {
            tasks_on_time++;
        }
        total_tardiness += std::max(0, current_time - task.deadline);
    }
}

// Dynamic programming approach with branch-and-bound pruning
ScheduleResult optimize_schedule(const std::unordered_map<int, Task>& tasks, 
                                const std::vector<int>& eligible_tasks, 
                                std::unordered_set<int> scheduled_tasks = {},
                                int current_time = 0,
                                int best_on_time = 0,
                                int best_tardiness = std::numeric_limits<int>::max()) {
    
    // Base case: All eligible tasks have been scheduled
    if (scheduled_tasks.size() == eligible_tasks.size()) {
        std::vector<int> schedule;
        for (int id : eligible_tasks) {
            if (scheduled_tasks.find(id) != scheduled_tasks.end()) {
                schedule.push_back(id);
            }
        }
        
        int tasks_on_time = 0;
        int total_tardiness = 0;
        evaluate_schedule(schedule, tasks, tasks_on_time, total_tardiness);
        
        return {schedule, tasks_on_time, total_tardiness};
    }
    
    ScheduleResult best_result;
    best_result.tasks_on_time = best_on_time;
    best_result.total_tardiness = best_tardiness;
    
    // Try each unscheduled task that has all dependencies satisfied
    for (int id : eligible_tasks) {
        if (scheduled_tasks.find(id) != scheduled_tasks.end()) continue;
        
        const Task& task = tasks.at(id);
        if (!can_schedule(task, scheduled_tasks)) continue;
        
        // Calculate metrics if we add this task next
        int new_time = current_time + task.duration;
        int new_on_time = (new_time <= task.deadline) ? 1 : 0;
        int new_tardiness = std::max(0, new_time - task.deadline);
        
        // Pruning: Skip if this path is guaranteed to be worse
        int remaining_tasks = eligible_tasks.size() - scheduled_tasks.size() - 1;
        int max_possible_on_time = new_on_time + remaining_tasks;
        
        if (max_possible_on_time < best_result.tasks_on_time || 
            (max_possible_on_time == best_result.tasks_on_time && 
             new_tardiness >= best_result.total_tardiness)) {
            continue;
        }
        
        // Try this task
        scheduled_tasks.insert(id);
        ScheduleResult result = optimize_schedule(
            tasks, eligible_tasks, scheduled_tasks, new_time, 
            best_result.tasks_on_time, best_result.total_tardiness
        );
        
        // Update best result if this path is better
        if (result.tasks_on_time > best_result.tasks_on_time || 
            (result.tasks_on_time == best_result.tasks_on_time && 
             result.total_tardiness < best_result.total_tardiness)) {
            best_result = result;
        }
        
        scheduled_tasks.erase(id);
    }
    
    return best_result;
}

// Heuristic approach based on EDF (Earliest Deadline First) with dependency constraints
std::vector<int> heuristic_schedule(const std::unordered_map<int, Task>& tasks) {
    std::vector<int> schedule;
    std::unordered_set<int> scheduled;
    std::priority_queue<std::pair<int, int>, 
                        std::vector<std::pair<int, int>>, 
                        std::greater<>> pq; // (deadline, id)
    
    // Initialize with tasks that have no dependencies
    for (const auto& [id, task] : tasks) {
        if (task.dependencies.empty()) {
            pq.push({task.deadline, id});
        }
    }
    
    while (!pq.empty()) {
        int id = pq.top().second;
        pq.pop();
        
        // Skip if already scheduled
        if (scheduled.find(id) != scheduled.end()) continue;
        
        // Check if all dependencies are satisfied
        const Task& task = tasks.at(id);
        bool dependencies_met = true;
        for (int dep : task.dependencies) {
            if (scheduled.find(dep) == scheduled.end()) {
                dependencies_met = false;
                break;
            }
        }
        
        if (dependencies_met) {
            // Schedule this task
            schedule.push_back(id);
            scheduled.insert(id);
            
            // Add dependent tasks to the priority queue
            for (int dep_id : task.dependents) {
                if (scheduled.find(dep_id) == scheduled.end()) {
                    pq.push({tasks.at(dep_id).deadline, dep_id});
                }
            }
        } else {
            // Re-add with a penalty to prioritize other tasks
            pq.push({task.deadline + 1000, id});
        }
    }
    
    return schedule;
}

// Main function to schedule tasks
std::vector<int> schedule_tasks(const std::vector<std::tuple<int, int, int, std::vector<int>>>& input_tasks) {
    if (input_tasks.empty()) {
        return {};
    }
    
    // Convert input tasks to our internal representation
    std::unordered_map<int, Task> tasks;
    for (const auto& [id, duration, deadline, dependencies] : input_tasks) {
        tasks[id] = {id, duration, deadline, dependencies, {}, false, false};
    }
    
    // Build dependency graph (add reverse edges for dependents)
    for (auto& [id, task] : tasks) {
        for (int dep_id : task.dependencies) {
            tasks[dep_id].dependents.push_back(id);
        }
    }
    
    // For small task sets (N ≤ 10), use exact DP with branch-and-bound
    if (tasks.size() <= 10) {
        std::vector<int> eligible_tasks;
        for (const auto& [id, _] : tasks) {
            eligible_tasks.push_back(id);
        }
        
        // First, use topological sort to determine valid task ordering for dependencies
        auto topo_order = topological_sort(tasks);
        
        // Solve optimization problem using DP with pruning
        auto result = optimize_schedule(tasks, topo_order);
        return result.schedule;
    } 
    // For larger task sets, use heuristic approach
    else {
        return heuristic_schedule(tasks);
    }
}

} // namespace task_scheduler