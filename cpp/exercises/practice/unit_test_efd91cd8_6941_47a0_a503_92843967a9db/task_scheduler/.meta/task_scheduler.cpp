#include "task_scheduler.h"
#include <algorithm>
#include <queue>
#include <unordered_map>
#include <unordered_set>

namespace task_scheduler {

    struct Task {
        int id;
        int duration;
        int deadline;
        std::vector<int> dependencies;
        std::vector<int> dependents;
        int in_degree = 0;
    };

    std::vector<int> topological_sort(std::vector<Task>& tasks) {
        std::vector<int> result;
        std::queue<int> q;
        
        // Find tasks with no dependencies
        for (size_t i = 0; i < tasks.size(); i++) {
            if (tasks[i].in_degree == 0) {
                q.push(i);
            }
        }
        
        while (!q.empty()) {
            int current = q.front();
            q.pop();
            result.push_back(current);
            
            for (int dependent : tasks[current].dependents) {
                tasks[dependent].in_degree--;
                if (tasks[dependent].in_degree == 0) {
                    q.push(dependent);
                }
            }
        }
        
        return result;
    }

    int get_max_completed_tasks(int n,
                              const std::vector<int>& id,
                              const std::vector<int>& duration,
                              const std::vector<int>& deadline,
                              const std::vector<std::vector<int>>& dependencies) {
        if (n == 0) return 0;
        
        // Create map for id to index
        std::unordered_map<int, int> id_to_index;
        for (int i = 0; i < n; i++) {
            id_to_index[id[i]] = i;
        }
        
        // Create tasks
        std::vector<Task> tasks(n);
        for (int i = 0; i < n; i++) {
            tasks[i].id = id[i];
            tasks[i].duration = duration[i];
            tasks[i].deadline = deadline[i];
            tasks[i].dependencies = dependencies[i];
            
            // Calculate in-degree and build dependents list
            for (int dep : dependencies[i]) {
                int dep_idx = id_to_index[dep];
                tasks[i].in_degree++;
                tasks[dep_idx].dependents.push_back(i);
            }
        }
        
        // Get topologically sorted order
        std::vector<int> topo_order = topological_sort(tasks);
        
        // Dynamic programming approach
        std::vector<std::vector<int>> dp(n + 1, std::vector<int>(1000001, -1));
        
        // Base case: no tasks scheduled
        dp[0][0] = 0;
        
        int max_completed = 0;
        
        // For each prefix of tasks in topological order
        for (int i = 0; i < n; i++) {
            int task_idx = topo_order[i];
            
            // For each possible current time
            for (int current_time = 0; current_time <= 1000000; current_time++) {
                if (dp[i][current_time] == -1) continue;
                
                // Don't schedule this task
                dp[i + 1][current_time] = std::max(dp[i + 1][current_time], dp[i][current_time]);
                
                // Schedule this task
                int completion_time = current_time + tasks[task_idx].duration;
                if (completion_time <= 1000000) {
                    int new_value = dp[i][current_time];
                    if (completion_time <= tasks[task_idx].deadline) {
                        new_value++;
                    }
                    dp[i + 1][completion_time] = std::max(dp[i + 1][completion_time], new_value);
                    max_completed = std::max(max_completed, dp[i + 1][completion_time]);
                }
            }
        }
        
        return max_completed;
    }

}