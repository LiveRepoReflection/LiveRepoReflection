#include "task_scheduler.h"
#include <vector>
#include <queue>
#include <functional>
#include <algorithm>

namespace task_scheduler {

int min_total_penalty(const std::vector<int>& duration,
                      const std::vector<int>& deadline,
                      const std::vector<std::vector<int>>& dependencies) {
    int n = duration.size();
    // Build graph: for each task, we need out_edges to children
    std::vector<std::vector<int>> graph(n);
    // Compute in-degree for each task. The "dependencies" vector for task i lists tasks that must precede i.
    std::vector<int> indegree(n, 0);
    for (int i = 0; i < n; ++i) {
        for (int pre : dependencies[i]) {
            // pre -> i edge
            graph[pre].push_back(i);
            indegree[i]++;
        }
    }
    
    // Priority queue to select the next available task.
    // We prioritize tasks with the earliest deadline.
    auto cmp = [&deadline](int left, int right) {
        return deadline[left] > deadline[right];
    };
    std::priority_queue<int, std::vector<int>, decltype(cmp)> pq(cmp);
    
    // Insert tasks with no dependencies (in-degree 0).
    for (int i = 0; i < n; ++i) {
        if (indegree[i] == 0) {
            pq.push(i);
        }
    }
    
    // Greedy scheduling: always pick the available task with the smallest deadline.
    long long current_time = 0;
    long long total_penalty = 0;
    
    while (!pq.empty()) {
        int task = pq.top();
        pq.pop();
        
        current_time += duration[task];
        if (current_time > deadline[task]) {
            total_penalty += (current_time - deadline[task]);
        }
        
        // Reduce the in-degree for tasks that depend on the current task.
        for (int next_task : graph[task]) {
            indegree[next_task]--;
            if (indegree[next_task] == 0) {
                pq.push(next_task);
            }
        }
    }
    
    return static_cast<int>(total_penalty);
}

}  // namespace task_scheduler